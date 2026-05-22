import numpy as np
import pandas as pd
from datetime import datetime
import warnings
import threading
import traceback

from PyQt5.QtWidgets import (
    QApplication,
    QVBoxLayout,
    QHBoxLayout,
    QWidget,
    QTabWidget,
    QMessageBox,
    QDesktopWidget,
    QMainWindow,
    QAction,
    QFileDialog
)

from PyQt5.QtCore import *


class Operation():
    def __init__(self, opType=None, parameters=None):
        """
        A single operation. It could be anything, but has a type and associated
        parameters. The QueueWorker implements the operation depending on its
        type, and handles the parameters accordingly.
        """

        # operation ID, making it uniquely identifyable in the queue
        # It is just the prefix op_ plus the time it was created.
        self.opID = "op_" + datetime.now().strftime("%d%H%M%S%f")

        self.is_running = False
        
        self.opType = opType
        self.parameters = parameters

        self.label = self.opType + "_" + self.opID


class OperationQueue(QObject):
    """
    Manages the list of operations in the queue, for displaying to the user.
    It therefore exists in the main GUI thread.
    """
    # Signals to communicate with QueueWorker
    operation_added = pyqtSignal(object)
    operation_removed = pyqtSignal(int)  # by index
    queue_cleared = pyqtSignal()
    start_processing = pyqtSignal()
    pause_processing = pyqtSignal()
    resume_processing = pyqtSignal()
    stop_processing = pyqtSignal()

    def __init__(self, parent, debug):
        """
        """
        super().__init__()
        self.parent = parent
        self.hardwareManager = parent.hardwareManager
        self.debug = debug

        self.is_running = False
        self._lock = threading.RLock()    # recursive lock for nested access
        self._operations = []   # the 'actual' queue where the operations are

    def add(self, operation):
        """
        Add a new operation to the queue
        """
        with self._lock:
            self._operations.append(operation)
            if self.debug:
                print(f"Operation {operation.opID} added to the queue!")
        self.operation_added.emit(operation)

    def clear(self):
        """
        Remove all operations frome the queue. Uses the .clear() method rather
        than just setting _operations to an empty list as this allows the same
        object to stay in use, preventing issues of other threads attempting to
        access the old queue before it is deleted.
        """
        with self._lock:
            self._operations.clear()
        self.queue_cleared.emit()

    def remove(self, opID):
        """
        Remove the operation with the specified ID
        """

    def move(self, opID, new_index):
        """
        Move an operation with the specified ID to a new index in the queue
        """

    def get_all_operations(self):
        """
        Thread safe read of all operations in the queue
        """
        with self._lock:
            # this creates a shallow copy of _operations, which is thread safe
            return list(self._operations)

    def peek_next(self):
        """
        Get the next instruction, but do not remove it from the queue
        """
        with self._lock:
            return self._operations[0] if self._operations else None

    def pop_next(self):
        """
        Remove and return the next instruction in the queue
        """
        with self._lock:
            return self._operations.pop(0) if self._operations else None


class QueueWorker(QObject):
    """
    Executes operations from the queue, and runs in a separate thread. It
    communicates with the HardwareManager and GUI using PyQt signals.
    """
    # signals for GUI feedback
    operation_started = pyqtSignal(object)
    operation_completed = pyqtSignal(object, bool)
    operation_failed = pyqtSignal(object, str)
    progress_update = pyqtSignal(str)
    queue_finished = pyqtSignal()

    # signals for control to HardwareManager
    set_temperature = pyqtSignal(float)
    acquire_spectrum = pyqtSignal()
    move_parameter = pyqtSignal()
    do_wait = pyqtSignal()
    
    def __init__(self, operationQueue, hardwareManager, debug):
        super().__init__()
        self.operationQueue = operationQueue
        self.hardwareManager = hardwareManager
        self.debug = debug

        self.is_running = False
        self.is_paused = False
        self._abort_requested = False
        self._lock = threading.RLock()

        # Connect queue signals
        self.operationQueue.start_processing.connect(self.start)
        self.operationQueue.pause_processing.connect(self.pause)
        self.operationQueue.resume_processing.connect(self.resume)
        self.operationQueue.stop_processing.connect(self.abort)

    @pyqtSlot()
    def run(self):
        """Called when thread starts"""
        # Timer for polling queue status
        # the timer is useful because the process_queue function only looks at
        # the next item in the queue. When it is done it needs to be called
        # again. So, the timer keeps calling it, and it only starts if the
        # running state is True, which is set by the GUI buttons.
        self.worker_timer = QTimer()
        self.worker_timer.timeout.connect(self.process_queue)
        self.worker_timer.start(100)  # Poll every 100ms

    @pyqtSlot()
    def start(self):
        """Start processing the queue"""
        with self._lock:
            self.is_running = True
            self.is_paused = False
            self._abort_requested = False
            if self.debug:
                print("Set queue runnning to True")

    @pyqtSlot()
    def pause(self):
        """Pause processing"""
        with self._lock:
            self.is_paused = True

    @pyqtSlot()
    def resume(self):
        """Resume processing"""
        with self._lock:
            self.is_paused = False

    @pyqtSlot()
    def abort(self):
        """Abort processing"""
        with self._lock:
            self._abort_requested = True
            self.is_running = False

    @pyqtSlot()
    def process_queue(self):
        """
        The main processing loop, which is called periodically by the timer.
        """
        with self._lock:
            # only proceed if we are allowed to
            if not self.is_running or self.is_paused or self._abort_requested:
                return

            if self.debug:
                print("Started processing the queue!")

            # what's next in the queue?
            operation = self.operationQueue.peek_next()

            # are we done?
            if operation is None:
                self.queue_finished.emit()
                with self._lock:
                    self.is_running = False
                return

            # we have an operation - let's run it
            try:
                self.operation_started.emit(operation)
                success = self._execute_operation(operation)

                # we only want to remove the operation if it succeeded
                if success:
                    self.operationQueue.pop_next()
                    self.operation_completed.emit(operation, True)
                else:
                    self.operation_failed.emit(operation, "operation failed")
            except Exception as e:
                # what about a major failure? Then we halt the queue entirely.
                error_msg = str(e)
                if self.debug:
                    traceback.print_exc()
                self.operation_failed.emit(operation, error_msg)
                self.abort()

    def _execute_operation(self, operation):
        """
        Execute a single operation.
        Returns True if successful, False otherwise.
        """
        op_type = operation.opType
        params = operation.parameters
        
        try:
            if op_type == 'temperature':
                return self._handle_temperature(params)
            elif op_type == 'spectrum':
                return self._handle_spectrum(params)
            elif op_type == 'move':
                return self._handle_move(params)
            elif op_type == 'wait':
                return self._handle_wait(params)
            else:
                raise ValueError(f"Unknown operation type: {op_type}")
        
        except Exception as e:
            self.progress_update.emit(f"Error: {str(e)}")
            return False

    def _handle_temperature(self, params):
        """
        Handle the heating of the substrate.
        """
        print("handling temperature!!!!!")
        print(params)

        setpoint = params.get('setpoint')

        self.progress_update.emit(f"Setting temperature to {setpoint} K")
        self.set_temperature.emit(setpoint)

        return True

    def _handle_spectrum(self, params):
        """
        Handle acqusition of spectra. The wavelength is moved according to the
        spectrum's resolution and integration time.
        """

    def _handle_timescan(self, params):
        """
        Handle acquisition of timescans, separate from spectra. The wavelength
        is not moved during a timescan.
        """

    def _handle_wait(self, params):
        """
        Handle wait time.
        """

    def _handle_move(self, params):
        """
        Handle the changing of simple parameters from one to another.
        For example, setting the wavelength to some single value and leaving it
        there.
        """

    def _handle_cryo(self, params):
        """
        Set the cryo to turn on or off
        """

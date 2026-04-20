import numpy as np
import pandas as pd
from datetime import datetime
import warnings

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


class OperationQueue():
    def __init__(self, parent, debug):
        """
        """

        self.parent = parent
        self.hardwareManager = parent.hardwareManager
        self.debug = debug

        self.running = False

        self.instructions = []

    def add(self, instruction):
        """
        """
        self.instructions.append(instruction)

    def clear(self):
        """
        """
        self.instructions = []
        return None


class QueueWorker():
    def __init__(self):
        """
        """
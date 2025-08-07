"""
DUVET!
It's UV-VIS spectroscopy time.

This is the main file, which creates the main window. All the 'stuff' in the
program like the spectrum display and deposition fitting gets put into the main
window as tabs. As such, they are separated into different .py files. They are
structured into 'Interface', 'Devices', and 'Tools' folders. This file interacts
with the interface files, which then interact with the devices and/or tools as
needed.

Functions relating to GUI elements should be under 'Interface'.
Functions relating to hardware interaction should be under 'Devices'.
Functions relating to analysis, fitting, etc, should be under 'Tools'.
"""

import sys
import traceback
from datetime import datetime
import json

sys.path.insert(0, 'Interface')
import analysisGUI
import controlGUI
from generalElements import configViewWindow

sys.path.insert(0, 'Devices')
import hardwareManager

from PyQt5 import QtGui

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

def get_config():
    """
    Open the configuration json file and return its contents in a dictionary
    """
    with open("config.json", "r", encoding='utf-8') as f:
        config_file = json.load(f)
    return config_file

def save_config(config_file):
    """
    Save the contents of a dictionary to the configuration json file
    """
    with open("config.json", "w", encoding='utf-8') as f:
        json.dump(config_file, f, ensure_ascii=False, indent=4)

def excepthook(exc_type, exc_value, exc_tb):
    """
    Catch errors and allow the program to continue
    """
    tb = "".join(traceback.format_exception(exc_type, exc_value, exc_tb))
    print("error caught!:")
    print("error message:\n", tb)

def center(window):
    """
    Thanks Pedro
    https://stackoverflow.com/questions/20243637/pyqt4-center-window-on-active-screen
    """
    frameGm = window.frameGeometry()
    screen = QApplication.desktop().screenNumber(
        QApplication.desktop().cursor().pos())
    centerPoint = QApplication.desktop().screenGeometry(screen).center()
    frameGm.moveCenter(centerPoint)
    window.move(frameGm.topLeft())


class Worker(QObject):
    def __init__(self, debug, parent):
        super().__init__()
        self.debug = debug
        self.hardwareManager = hardwareManager.HardwareManager(self.debug,
                                                               parent)

    def run(self):
        self.timer = QTimer()
        self.timer.timeout.connect(self.hardwareManager._refresh)
        self.timer.start(self.hardwareManager.polling_rate)


class MainWindow(QMainWindow):
    """
    The main window which opens at the beginning once DUVET is run
    """
    def __init__(self, debug):
        super().__init__()
        self.debug = debug
        self.config = get_config()

        # initialize the log file
        self.changelog = ""
        now = datetime.now()
        current_time = now.strftime("%Y-%m-%d_%H%M%S")
        self.changelogFile = "./Logs/"+current_time+".log"

        # create the hardware manager, which gets its own thread
        #self.hardwareManager = hardwareManager.HardwareManager(self.debug)
        self.hardwareThread = QThread()
        #self.hardwareWorker = Worker(self.hardwareManager)
        self.hardwareWorker = Worker(self.debug, self)
        self.hardwareThread.started.connect(self.hardwareWorker.run)
        self.hardwareThread.start()
        self.hardwareManager = self.hardwareWorker.hardwareManager

        self.log("Started DUVET!")
        if self.debug:
            self.log("Debug mode is ON. Exciting!")

        # ---------------------------------------------------------------------
        # Setup accessory windows
        # ---------------------------------------------------------------------
        self.configWindow = configViewWindow(self)
        
        # ---------------------------------------------------------------------
        # Setup main window and tabs
        # ---------------------------------------------------------------------
        self.setWindowTitle("DUVET: Danish UV End-station Tool")
        # define the top-level layout of the window
        self.layout = QVBoxLayout()
        # define the tab widget that will exist in the top level layout
        self.tabs = QTabWidget()

        # ---------------------------------------------------------------------
        # Setup spectrum display tab
        # ---------------------------------------------------------------------
        
        self.specTab = QWidget()
        # create the spectrum display
        self.SDT = analysisGUI.AnalysisTab(self, debug)
        # set the layout of the spectrum display tab placeholder widget
        self.specTab.setLayout(self.SDT.outerLayout)

        # ---------------------------------------------------------------------
        # Setup Control tab
        # ---------------------------------------------------------------------
        
        self.controlTab = QWidget()
        self.CT = controlGUI.ControlTab(self, debug)
        self.controlTab.setLayout(self.CT.outerLayout)

        # ---------------------------------------------------------------------
        # Create the menu bar
        # ---------------------------------------------------------------------

        self.menu = self.menuBar()

        self.fileMenu = self.menu.addMenu("&File")
        self.saveDirSelAction = QAction(QtGui.QIcon("./Icons/floppyDisk.png"),
                                        "Change Save Directory", self)
        self.saveDirSelAction.triggered.connect(self.update_save_dir)
        self.fileMenu.addAction(self.saveDirSelAction)

        self.CCAction = QAction(QtGui.QIcon("./Icons/clipboard.png"),
                                "View Current Configuration", self)
        self.CCAction.triggered.connect(self.configWindow.show_window)
        self.fileMenu.addAction(self.CCAction)
        
        self.BNWAction = QAction(QtGui.QIcon("./Icons/magnifyingGlass.png"),
                                 "Open Big Numbers Window", self)
        self.fileMenu.addAction(self.BNWAction)

        self.helpAction = QAction(QtGui.QIcon("./Icons/sad.png"),
                                        "help", self)
        self.helpAction.setStatusTip("Ahhhhhhhhh")
        self.fileMenu.addAction(self.helpAction)

        # ---------------------------------------------------------------------
        # Finalize main window
        # ---------------------------------------------------------------------

        # add the individual tabs to the tabs widget
        self.tabs.addTab(self.specTab, "Analysis")
        #self.tabs.addTab(self.depTab, "Timescan")
        self.tabs.addTab(self.controlTab, "Control")

        # Set the window's main layout
        self.layout.addWidget(self.tabs)
        self.centralWidget = QWidget()
        self.centralWidget.setLayout(self.layout)
        self.setCentralWidget(self.centralWidget)

    def update_save_dir(self):
        """
        Update the directory where new data will be saved
        """
        oldDir = self.config["save_directory"]

        new_dir = QFileDialog.getExistingDirectory(
            self, "Select Directory", directory=oldDir)
        
        self.config["save_directory"] = new_dir

        # we have a / at the end right?
        if self.config["save_directory"][-1] != "/":
            self.config["save_directory"] += '/'

        # update the configwindow
        self.configWindow.refresh()

        logMessage = f"changed save directory from {oldDir} to {new_dir}"
        self.log(logMessage)

    def log(self, message):
        """
        Log an event to the changelog file.
        """
        now = datetime.now()
        current_time = now.strftime("%d-%m-%Y %H:%M:%S")
        self.changelog += current_time + " " + message + "\n"
        if self.debug:
            print(current_time + " " + message)

    def _save_log(self):
        """
        Save the changelog to file
        """
        with open(self.changelogFile, 'w') as file:
            self.log("Saving .log file")
            file.write(self.changelog)

    def closeEvent(self, event):
        """
        Event to run on quitting DUVET
        """
        msgBox = QMessageBox()  # no not that msg, silly
        msgBox.setIcon(QMessageBox.Warning)
        msgBox.setText("Are you sure you want to quit?")
        msgBox.setWindowTitle("Confirm Exit")
        msgBox.setStandardButtons(QMessageBox.No | QMessageBox.Yes)
        msgBox.setDefaultButton(QMessageBox.No)
        center(msgBox)
        reply = msgBox.exec()

        if reply == QMessageBox.Yes:
            msgBox2 = QMessageBox()
            msgBox2.setIcon(QMessageBox.Question)
            msgBox2.setText("Wow, you're really leaving? That's so rude 😔")
            msgBox2.setWindowTitle("Confirm Exit")
            msgBox2.setStandardButtons(QMessageBox.Cancel | QMessageBox.Yes)
            msgBox2.setDefaultButton(QMessageBox.Cancel)
            center(msgBox2)
            reply2 = msgBox2.exec()
            if reply2 == QMessageBox.Yes:
                self.log("Quitting DUVET")
                self._save_log()
                save_config(self.config)
                self.log("Closing ConSys API")
                self.hardwareManager.ConSysInterface.close()
                self.log("ConSys API closed")
                event.accept()
            else:
                hahaBox = QMessageBox()
                #hahaBox.setIcon(QMessageBox.Warning)
                hahaBox.setText("Yeah, that's what I thought.")
                hahaBox.setWindowTitle("😤")
                hahaBox.setStandardButtons(QMessageBox.Ok)
                center(hahaBox)
                reply3 = hahaBox.exec()
                event.ignore()
        else:
            event.ignore()
    

if __name__ == "__main__":
    # do we debug?
    if "debug=True" in sys.argv:
        debug = True
    else:
        debug = False
        
    # intialize error catching
    sys.excepthook = excepthook

    # contruct the application
    app = QApplication(sys.argv)

    # set our font
    font = QtGui.QFont("Arial", 11)
    app.setFont(font)

    # create and show the main window
    window = MainWindow(debug)
    window.show()

    # execute the application
    rc = app.exec_()
    sys.exit(rc)

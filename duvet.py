"""
DUVET!
It's UV-VIS spectroscopy time.

This is the main file, which creates the main window. All the 'stuff' in the
program like the spectrum display and deposition fitting gets put into the main
window as tabs. As such, they are separated into different .py files. They are
structured into 'GUI' and 'tools' files. For example the code relating to
displaying and fitting spectra are called 'analysisGUI' and 'spectools.' The 'tools'
files contain the physics and mathematics that interact with the data. The 'GUI'
files contain the infrastructure for putting those analysis tools into the
format the user interacts with.

Here is a layout of DUVET's structure:

duvet.py
 |----> analysisGUI.py <-> spectools.py
 |----> controlGUI.py <-> controltools.py

Further functionality can be added this way, as different options for tabs in
the DUVET main display.
"""

import sys
import traceback
from datetime import datetime

sys.path.insert(0, 'Interface')
import analysisGUI
#import depGUI
import controlGUI


from PyQt5 import QtGui

from PyQt5.QtWidgets import (
    QApplication,
    QVBoxLayout,
    QHBoxLayout,
    QWidget,
    QTabWidget,
    QMessageBox,
    QDesktopWidget
)

def excepthook(exc_type, exc_value, exc_tb):
    """
    Catch errors
    """
    tb = "".join(traceback.format_exception(exc_type, exc_value, exc_tb))
    print("error caught!:")
    print("error message:\n", tb)
    #QtWidgets.QApplication.quit()
    # or QtWidgets.QApplication.exit(0)

def center(window):
    """
    Thanks Pedro
    https://stackoverflow.com/questions/20243637/pyqt4-center-window-on-active-screen
    """
    frameGm = window.frameGeometry()
    screen = QApplication.desktop().screenNumber(QApplication.desktop().cursor().pos())
    centerPoint = QApplication.desktop().screenGeometry(screen).center()
    frameGm.moveCenter(centerPoint)
    window.move(frameGm.topLeft())


class MainWindow(QWidget):
    """
    The main window which opens at the beginning once DUVET is run
    """
    def __init__(self, debug):
        super().__init__()
        self.debug = debug

        # initialize the log file
        self.changelog = ""
        now = datetime.now()
        current_time = now.strftime("%Y-%m-%d_%H%M%S")
        self.changelogFile = "./Logs/"+current_time+".log"

        self.log("Started DUVET!")
        if self.debug:
            self.log("Debug mode is ON. Exciting!")
        
        # ---------------------------------------------------------------------
        # Setup window and tabs
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
        self.SDT = analysisGUI.spectrumDisplayTab(self, debug)
        # set the layout of the spectrum display tab placeholder widget
        self.specTab.setLayout(self.SDT.outerLayout)

        # ---------------------------------------------------------------------
        # Setup timescan tab
        # ---------------------------------------------------------------------
        
        #self.depTab = QWidget()
        #self.DFT = depGUI.depositionFittingTab()
        #self.depTab.setLayout(self.DFT.outerLayout)

        # ---------------------------------------------------------------------
        # Setup Control tab
        # ---------------------------------------------------------------------
        
        self.controlTab = QWidget()
        self.CT = controlGUI.ControlTab(self, debug)
        self.controlTab.setLayout(self.CT.outerLayout)
        
        # ---------------------------------------------------------------------
        # Finalize main window
        # ---------------------------------------------------------------------

        # add the individual tabs to the tabs widget
        self.tabs.addTab(self.specTab, "Analysis")
        #self.tabs.addTab(self.depTab, "Timescan")
        self.tabs.addTab(self.controlTab, "Control")

        # Set the window's main layout
        self.layout.addWidget(self.tabs)
        self.setLayout(self.layout)

    def log(self, message):
        """
        Log an event to the changelog file.
        """
        now = datetime.now()
        current_time = now.strftime("%d-%m-%Y %H:%M:%S")
        self.changelog += current_time + " " + message + "\n"
        if self.debug:
            # printed message specifies which spectrum we are dealing with
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
    if "debug" in sys.argv:
        debug = True
    else:
        debug = False
    # intialize error catching
    sys.excepthook = excepthook
    
    # set our font
    font = QtGui.QFont("Arial", 11)
    #instance = QApplication.instance()
    #instance.setFont(font)

    # contruct the application
    app = QApplication(sys.argv)
    app.setFont(font)
    window = MainWindow(debug)
    #window.setFont(font)
    window.show()
    sys.exit(app.exec())

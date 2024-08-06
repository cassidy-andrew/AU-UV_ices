"""
DUVET!
It's UV-VIS spectroscopy time.

This is the main file, which creates the main window. All the 'stuff' in the
program like the spectrum display and deposition fitting gets put into the main
window as tabs. As such, they are separated into different .py files. They are
structured into 'GUI' and 'tools' files. For example the code relating to
displaying and fitting spectra are called 'specGUI' and 'spectools.' The 'tools'
files contain the physics and mathematics that interact with the data. The 'GUI'
files contain the infrastructure for putting those analysis tools into the
format the user interacts with.

Here is a layout of DUVET's structure:

duvet.py
 |----> specGUI.py <-> spectools.py
 |----> depGUI.py <-> deptools.py

Further functionality can be added this way, as different options for tabs in
the DUVET main display.
"""


import sys
import specGUI
import depGUI
import traceback

from PyQt5 import QtGui

from PyQt5.QtWidgets import (
    QApplication,
    QVBoxLayout,
    QHBoxLayout,
    QWidget,
    QTabWidget,
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


class MainWindow(QWidget):
    """
    The main window which opens at the beginning once DUVET is run
    """
    def __init__(self, debug):
        super().__init__()
        # ---------------------------------------------------------------------
        # Setup window and tabs
        # ---------------------------------------------------------------------
        self.setWindowTitle("DUVET: Danish UV End-station Tool")
        # define the top-level layout of the window
        self.layout = QVBoxLayout()
        # define the tab widget that will exist in the top level layout
        self.tabs = QTabWidget()
        # define the individual tab placeholder widgets
        self.specTab = QWidget()
        self.depTab = QWidget()

        # ---------------------------------------------------------------------
        # Setup spectrum display tab
        # ---------------------------------------------------------------------

        # create the spectrum display
        self.SDT = specGUI.spectrumDisplayTab(debug)
        # set the layout of the spectrum display tab placeholder widget
        self.specTab.setLayout(self.SDT.outerLayout)

        # ---------------------------------------------------------------------
        # Setup timescan tab
        # ---------------------------------------------------------------------

        self.DFT = depGUI.depositionFittingTab()
        self.depTab.setLayout(self.DFT.outerLayout)
        # ---------------------------------------------------------------------
        # Finalize main window
        # ---------------------------------------------------------------------

        # add the individual tabs to the tabs widget
        self.tabs.addTab(self.specTab, "Spectrum Display")
        self.tabs.addTab(self.depTab, "Timescan")

        # Set the window's main layout
        self.layout.addWidget(self.tabs)
        self.setLayout(self.layout)


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
    #font.setFamily()
    instance = QApplication.instance()
    instance.setFont(font)

    # contruct the application
    app = QApplication(sys.argv)
    #app.setFont(font)
    window = MainWindow(debug)
    #window.setFont(font)
    window.show()
    sys.exit(app.exec())

import sys
import os
import inspect

import specGUI

currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, parentdir+'/Tools')
import spectools
import deptools

import matplotlib
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import (
    FigureCanvasQTAgg,
    NavigationToolbar2QT as NavigationToolbar
)
matplotlib.use('QtAgg')
plt.style.use('./au-uv.mplstyle')
plt.autoscale(False)

from pyqt_color_picker import ColorPickerDialog

from PyQt5.QtWidgets import (
    QApplication,
    QCheckBox,
    QFormLayout,
    QLineEdit,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QListWidget,
    QListWidgetItem,
    QLabel,
    QWidget,
    QFileDialog,
    QDoubleSpinBox,
    QTabWidget,
    QDialog
)
from PyQt5.QtGui import (
    QPalette,
    QColor
)

from PyQt5.QtCore import *

from PyQt5.Qt import (
    QRect
)


class DepMplCanvas(FigureCanvasQTAgg):
    def __init__(self, parent=None):
        self.fig, self.axes = plt.subplots(1, 1)
        self.fig.set_size_inches(16/2.5, 9/2.5)
        self.axes.set_ylim(0, 1)
        self.axes.set_xlim(0, 1)
        super(DepMplCanvas, self).__init__(self.fig)


class depositionFittingTab():
    def __init__(self):
        self.outerLayout = QVBoxLayout()
        # Create a layout for the plot and scan list
        self.topLayout = QHBoxLayout()
        # Create a layout for the plot
        self.plotLayout = QVBoxLayout()
        # Create a layout for the scan
        self.scanLayout = QVBoxLayout()
        # Create a layout for the buttons
        self.bottomLayout = QHBoxLayout()

        # ---------------------------
        # Plot
        # ---------------------------

        self.sc = DepMplCanvas(self)
        self.toolbar = NavigationToolbar(self.sc)

        self.plotLayout.addWidget(self.toolbar)
        self.plotLayout.addWidget(self.sc)
        #self.sc.axes.plot([0,1,2,3,4], [10,1,20,3,40])

        # ---------------------------
        # Spectrum Menu
        # ---------------------------
        
        # button for adding a scan
        self.add_scan_btn = QPushButton("Add Scan")
        self.add_scan_btn.pressed.connect(self.add_scan)
        #self.scanLayout.addWidget(self.add_scan_btn)

        # display list of spectra
        #self.speclist = QListWidget()
        #self.listLayout.addWidget(self.speclist)

        # ---------------------------
        # Bottom Buttons
        # ---------------------------
        self.eb_clear = QPushButton("Clear Plot")
        self.eb_clear.pressed.connect(self.clear_plot)
        self.bottomLayout.addWidget(self.eb_clear)

        self.eb_adata = QPushButton("Export Fit Parameters")
        self.eb_adata.pressed.connect(self.export_adata)
        self.bottomLayout.addWidget(self.eb_adata)

        # ---------------------------
        # Nest the inner layouts into the outer layout
        # ---------------------------
        self.topLayout.addLayout(self.plotLayout)
        #self.topLayout.addLayout(self.scanLayout)
        #self.topLayout.addWidget(self.add_scan_btn)
        
        self.outerLayout.addLayout(self.topLayout)
        self.outerLayout.addLayout(self.bottomLayout)
        

    def add_scan(self):
        """
        Add a timescan
        """
        print("to be implimented")

    def clear_plot(self):
        print('clear plot is to be implemented')

    def export_sdata(self):
        print('export data is to be implemented')

    def export_adata(self):
        print('export data is to be implemented')

    def remove_data(self):
        print('remove data is to be implemented')
        



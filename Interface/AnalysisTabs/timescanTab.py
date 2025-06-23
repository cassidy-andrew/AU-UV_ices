import sys
import os
import inspect

currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
interfacedir = os.path.dirname(currentdir)
maindir = os.path.dirname(interfacedir)

sys.path.insert(0, maindir)
from duvet import center

sys.path.insert(0, maindir+'/Tools')
import depTools

from datetime import datetime

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
    QTextEdit,
    QDialog,
    QScrollArea,
    QComboBox,
    QAbstractItemView
)

from PyQt5.QtGui import (
    QPalette,
    QColor,
    QFont
)

from PyQt5.QtCore import *

from PyQt5.Qt import (
    QRect
)

class TimescanMplCanvas(FigureCanvasQTAgg):
    def __init__(self, parent=None):
        self.fig, self.axes = depTools.plot_timescan(None,
            return_fig_and_ax=True)
        super(TimescanMplCanvas, self).__init__(self.fig)

class TimescanDisplayTab():
    def __init__(self, parent, debug):
        self.parent = parent
        self.mainWindow = parent.parentWindow
        self.debug = debug
        self.guiTS = guiTimescan(self.mainWindow, self.debug)
        # Create an outer layout
        self.outerLayout = QHBoxLayout()
        self.plotLayout = QVBoxLayout()
        self.paramsOuterLayout = QVBoxLayout()

        # ---------------------------
        # Plot
        # ---------------------------
        self.sc = TimescanMplCanvas(self)
        self.sc.setMinimumWidth(900)
        self.sc.setMinimumHeight(600)
        self.toolbar = NavigationToolbar(self.sc)
        self.xlims = [0, 1000]
        self.ylims = [-0.1, 1.1]
        self.sc.axes.set_ylim(self.ylims)
        self.sc.axes.set_xlim(self.xlims)

        self.plotLayout.addWidget(self.toolbar)
        self.plotLayout.addWidget(self.sc)

        # ---------------------------
        # Parameter Area
        # ---------------------------
        self.paramsTopLayout = QVBoxLayout()
        # button for adding timescan
        self.add_timescan_btn = QPushButton("Load Timescan")
        self.add_timescan_btn.setMinimumWidth(350)
        self.add_timescan_btn.pressed.connect(self.add_timescan)
        self.paramsTopLayout.addWidget(self.add_timescan_btn)

        # button for fitting the timescan
        self.fit_timescan_btn = QPushButton("Fit Loaded Timescan")
        self.fit_timescan_btn.pressed.connect(
            lambda: self.fit_timescan(self.tStartLineEdit.value(),
                                      self.tEndLineEdit.value()))
        self.paramsTopLayout.addWidget(self.fit_timescan_btn)

        # parameter labels
        self.paramsTopFormLayout = QFormLayout()
        # label for the spectrum name
        self.nameLabel = QLabel("None")
        # number entry for fit range start
        self.tStartLineEdit = QDoubleSpinBox()
        self.tStartLineEdit.setRange(0, 9999999999)
        self.tStartLineEdit.setDecimals(1)
        self.tStartLineEdit.setSingleStep(1)
        self.tStartLineEdit.setValue(0)
        
        # number entry for fit range end
        self.tEndLineEdit = QDoubleSpinBox()
        self.tEndLineEdit.setRange(0, 9999999999)
        self.tEndLineEdit.setDecimals(1)
        self.tEndLineEdit.setSingleStep(1)
        self.tEndLineEdit.setValue(0)

        # why not make the fit happen as soon as you change the limits?
        self.tStartLineEdit.valueChanged.connect(
            lambda: self.fit_timescan(self.tStartLineEdit.value(),
                                      self.tEndLineEdit.value())
        )
        self.tEndLineEdit.valueChanged.connect(
            lambda: self.fit_timescan(self.tStartLineEdit.value(),
                                      self.tEndLineEdit.value())
        )

        self.paramsBottomLayout = QVBoxLayout()
        self.fitTitleLabel = QLabel("Fitted Parameters")
        self.paramsBottomLayout.addWidget(self.fitTitleLabel)

        self.paramsBottomFormLayout = QFormLayout()
        # the fitted parameter values
        self.redchi2Label = QLabel("")
        self.depRateLabel = QLabel("")
        self.refractiveIndexLabel = QLabel("")
        
        self.paramsTopFormLayout.addRow("File Name: ", self.nameLabel)
        self.paramsTopFormLayout.addRow("Fit Lower Limit (s)", self.tStartLineEdit)
        self.paramsTopFormLayout.addRow("Fit Upper Limit (s)", self.tEndLineEdit)
        self.paramsBottomFormLayout.addRow("Reduced Chi Square = ",
                                     self.redchi2Label)
        self.paramsBottomFormLayout.addRow("Ice Deposition Rate = ",
                                     self.depRateLabel)
        self.paramsBottomFormLayout.addRow("Ice Index of Refraction = ",
                                     self.refractiveIndexLabel)

        # ---------------------------
        # Nest the inner layouts into the outer layout
        # ---------------------------
        self.outerLayout.addLayout(self.plotLayout)
        self.paramsTopLayout.addLayout(self.paramsTopFormLayout)
        self.paramsOuterLayout.addLayout(self.paramsTopLayout)
        self.paramsBottomLayout.addLayout(self.paramsBottomFormLayout)
        self.paramsOuterLayout.addLayout(self.paramsBottomLayout)
        self.outerLayout.addLayout(self.paramsOuterLayout)

    def add_timescan(self):
        """
        """
        # ask the user for a file
        fname = QFileDialog.getOpenFileName()[0]
        #print(fname)
        self.guiTS.load_timescan(fname)
        self.update_plot()
        self.nameLabel.setText(self.guiTS.timescan.name)

    def fit_timescan(self, t_start, t_end):
        """
        """
        if self.guiTS.timescan is not None:
            self.guiTS.timescan.find_deposition_rate(guesses=None,
                                                     t_start=t_start, 
                                                     t_end=t_end,
                                                     verbose=False)
            self.update_plot()
            self.redchi2Label.setText(f"{self.guiTS.timescan.redchi2:.4e}")
            self.depRateLabel.setText(
                f"{self.guiTS.timescan.deposition_rate['value']:.4f}+-"+
                f"{self.guiTS.timescan.deposition_rate['error']:.4f} nm/s")
            self.refractiveIndexLabel.setText(
                f"{self.guiTS.timescan.refractive_index['value']:.4f}")
        else:
            print("no timescan exists yet")
            return None

    def update_plot(self):
        self.sc.axes.cla()
        depTools.plot_timescan(self.guiTS.timescan, ax=self.sc.axes)
        self.sc.draw()


class guiTimescan():
    """
    """
    def __init__(self, parentWindow, debug):
        self.parentWindow = parentWindow
        self.debug = debug
        self.default_laser_wavelength = 632.8   # nm
        self.timescan = None

    def load_timescan(self, fname):
        self.timescan = depTools.DepositionTimeScan(fname)

    def update_name(self):
        if self.timescane is not None:
            return self.timescan.name
        else:
            return None

import sys
import os
import inspect
import pandas as pd

from datetime import datetime

sys.path.insert(0, "Interface/ControlTabs")
import annealTab

currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
interfacedir = os.path.dirname(currentdir)
maindir = os.path.dirname(interfacedir)

sys.path.insert(0, maindir)

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
    QGridLayout,
    QPushButton,
    QListWidget,
    QListWidgetItem,
    QLabel,
    QWidget,
    QFileDialog,
    QDoubleSpinBox,
    QTabWidget,
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

import pyqtgraph as pg
pg.setConfigOption('background', (255,255,255, 100))


class TSMplCanvas(FigureCanvasQTAgg):
    def __init__(self, parent=None):
        self.fig, self.axes = plt.subplots(1, 1)
        super(SpecMplCanvas, self).__init__(self.fig)


class TimescanPlot():
    """
    Represents a plot specifically for timescan data. The control tab has three
    of these. Each one should be configurable to show any data as a function
    of time.
    """
    def __init__(self, parent, debug):
        self.parent = parent
        self.hardwareManager = self.parent.hardwareManager
        self.debug = debug
        self.yData = "Temperature (K)"
        self.data_line = None

        self.layout = QVBoxLayout()
    
        # menu for selecting what is on the y axis
        self.yMenu = QComboBox()
        # add all the available data fields to the dropdown menu
        for col in self.hardwareManager.data.columns.values.tolist():
            if col != "Time":    # we skip the time column
                self.yMenu.addItem(col)
        self.yMenu.currentTextChanged.connect(self._update_yAxis)

        # the figure
        self.figureWidget = pg.PlotWidget(
            self.parent.parentWindow,
            axisItems={'bottom':pg.AxisItem(orientation='bottom')}
        )
        self.figureWidget.setMinimumWidth(500)
        #self.figureWidget.setMinimumHeight(300)
        self.figureWidget.setTitle("")

        # add items to the layout
        self.layout.addWidget(self.yMenu)
        self.layout.addWidget(self.figureWidget)

    def _update_yAxis(self):
        self.yData = self.yMenu.currentText()

    def refresh_plot(self):
        # get the latest data from the hardware manager
        df = self.hardwareManager.data
        # have we plotted before?
        if self.data_line is None:
            self.data_line = self.figureWidget.plot((df['Time'],df[self.yData]))
        else:
            self.data_line.setData(df['Time'], df[self.yData])
        self.figureWidget.setData
        

class ControlTab():
    def __init__(self, parentWindow, debug):
        self.parentWindow = parentWindow
        self.debug = debug
        self.hardwareManager = parentWindow.hardwareManager
        self.valueFont = QFont("Consolas", 30)
        self.titleFont = QFont("Arial", 12)
        #self.TSRecorder = TimescanRecorder(self)
        
        self.outerLayout = QHBoxLayout()

        # ------------------------------------
        # functional item tabs
        # ------------------------------------
        self.tabs = QTabWidget()
        self.tabs.setFixedWidth(500)

        self.annealTabWidget = QWidget()
        #self.annealTabWidget.setFixedWidth(500)
        self.annealTabObject = annealTab.AnnealTab(self, debug)
        self.annealTabWidget.setLayout(self.annealTabObject.outerLayout)
        self.tabs.addTab(self.annealTabWidget, "Anneal")

        self.acquisitionTab = QWidget()
        self.tabs.addTab(self.acquisitionTab, "Acquire Spectrum")

        self.timescanTab = QWidget()
        self.tabs.addTab(self.timescanTab, "Acquire Timescan")

        # ------------------------------------
        # Scheduler
        # ------------------------------------
        self.schedulerLayout = QVBoxLayout()

        self.queueTitle = QLabel("Queue")
        self.queueTitle.setFont(self.titleFont)
        self.schedulerLayout.addWidget(self.queueTitle)

        self.queueList = QListWidget()
        self.queueList.setMinimumWidth(100)
        self.queueList.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.schedulerLayout.addWidget(self.queueList)

        self.historyTitle = QLabel("History")
        self.historyTitle.setFont(self.titleFont)
        self.schedulerLayout.addWidget(self.historyTitle)

        self.historyList = QListWidget()
        self.historyList.setMinimumWidth(100)
        self.historyList.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.schedulerLayout.addWidget(self.historyList)

        # ------------------------------------
        # Plotter
        # ------------------------------------
        self.plotterLayout = QVBoxLayout()

        # temperature plot
        #self.tempTimeAxis = pg.DateAxisItem('bottom')
        """self.tempFig = pg.PlotWidget(
            self.parentWindow, title='Temperature',
            labels={'left': 'Temperature (K)'},
            axisItems={'bottom':pg.AxisItem(orientation='bottom')}
        )
        self.tempFig.setBackground(background=None)
        self.plotterLayout.addWidget(self.tempFig)
        self.tempFig.setMinimumWidth(500)"""
        self.plot1 = TimescanPlot(self, self.debug)
        self.plotterLayout.addLayout(self.plot1.layout)

        self.plot2 = TimescanPlot(self, self.debug)
        self.plotterLayout.addLayout(self.plot2.layout)

        self.plot3 = TimescanPlot(self, self.debug)
        self.plotterLayout.addLayout(self.plot3.layout)

        """# pressure plot
        self.pressureTimeAxis = pg.DateAxisItem('bottom')
        self.pressureFig = pg.PlotWidget(self.parentWindow, title='Pressure',
                                    axisItems={'bottom':self.pressureTimeAxis})
        self.pressureFig.setBackground(background=None)
        self.pressureFig.setLogMode(None, True)
        self.plotterLayout.addWidget(self.pressureFig)
        self.pressureFig.setMinimumWidth(500)

        # laser plot
        self.laserTimeAxis = pg.DateAxisItem('bottom')
        self.laserFig = pg.PlotWidget(self.parentWindow, title='Laser Signal',
                                     axisItems={'bottom':self.laserTimeAxis})
        self.laserFig.setBackground(background=None)
        self.plotterLayout.addWidget(self.laserFig)
        self.laserFig.setMinimumWidth(500)"""

        # collection buttons
        self.collectorLayout = QHBoxLayout()
        # start collection button
        self.startColButton = QPushButton("Start Collection")
        self.startColButton.clicked.connect(
            self.hardwareManager.start_timescan_collection)
        self.collectorLayout.addWidget(self.startColButton)
        # stop collection button
        self.stopColButton = QPushButton("Stop Collection")
        self.stopColButton.clicked.connect(
            self.hardwareManager.stop_timescan_collection)
        self.collectorLayout.addWidget(self.stopColButton)

        self.plotterLayout.addLayout(self.collectorLayout)
        

        self.outerLayout.addWidget(self.tabs)
        self.outerLayout.addLayout(self.schedulerLayout)
        self.outerLayout.addLayout(self.plotterLayout)

        
        self.hardwareManager.add_refresh_function(self.refresh_figures)

    def refresh_figures(self):
        #df = self.hardwareManager.data
        #self.tempFig.getPlotItem.clear()
        #self.tempFig.setData(df['Time'], df['Temperature (K)'])
        self.plot1.refresh_plot()
        self.plot2.refresh_plot()
        aelf.plot3.refresh_plot()
        
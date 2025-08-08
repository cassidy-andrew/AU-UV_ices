import sys
import os
import inspect
import pandas as pd

from datetime import datetime

sys.path.insert(0, "Interface/ControlTabs")
import annealTab
import overviewTab

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
    QAbstractItemView,
    QSplitter
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


class scientificAxisItem(pg.AxisItem):
    """
    https://stackoverflow.com/questions/59768880/how-to-format-y-axis-displayed-numbers-in-pyqtgraph
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def tickStrings(self, values, scale, spacing):
        return [f'{10**v:.2e}' for v in values]


class TimescanPlot():
    """
    Represents a plot specifically for timescan data. The control tab has three
    of these. Each one should be configurable to show any data as a function
    of time.
    """
    def __init__(self, parent, debug, yData="Temperatures (K)"):
        self.parent = parent
        self.hardwareManager = self.parent.hardwareManager
        self.debug = debug
        self.yDataName = yData

        # what can we plot, and in what style?
        self.yItems = {
            'Sample T (K)':{'pen':pg.mkPen('black', width=2)},
            'Setpoint T (K)':{'pen':pg.mkPen('red', width=2)},
            'Heater Power (%)':{'pen':pg.mkPen('black', width=2)},
            'MC Pressure (mbar)':{'pen':pg.mkPen('black', width=2)},
            'DL Pressure (mbar)':{'pen':pg.mkPen('black', width=2)},
            'Hamamatsu (V)':{'pen':pg.mkPen('black', width=2)},
        }

        self.layout = QVBoxLayout()
    
        # menu for selecting what is on the y axis
        self.yMenu = QComboBox()
        self.yMenu.addItem('Temperatures (K)')
        # add all the available data fields to the dropdown menu
        for col in self.yItems:
            self.yMenu.addItem(col)
        self.yMenu.setCurrentText(self.yDataName)
        self.yMenu.currentTextChanged.connect(self._update_yAxis)

        """self.figureWidget = pg.PlotWidget(
                self.parent.parentWindow,
                axisItems={'bottom':pg.DateAxisItem(orientation='bottom')}
            )"""

        if "pressure" in self.yDataName.lower():
            self.figureWidget = pg.PlotWidget(
                self.parent.parentWindow,
                axisItems={'bottom':pg.DateAxisItem(orientation='bottom'),
                           #'left': scientificAxisItem(orientation='left')}
                          })
            self.figureWidget.setLogMode(False, True)
        else:
            self.figureWidget = pg.PlotWidget(
                self.parent.parentWindow,
                axisItems={'bottom':pg.DateAxisItem(orientation='bottom')}
            )
        self.figureLegend = self.figureWidget.addLegend()
        self.figureWidget.setMinimumWidth(500)
        #self.figureWidget.setMinimumHeight(300)
        self.figureWidget.setTitle("")
        self.figureWidget.getAxis('left').setTextPen('black')
        self.figureWidget.getAxis('bottom').setTextPen('black')

        self.data_line1 = self.figureWidget.plot([], [])
        self.data_line2 = self.figureWidget.plot([], []) # None

        # add items to the layout
        self.layout.addWidget(self.yMenu)
        self.layout.addWidget(self.figureWidget)


    def _update_yAxis(self):
        self.yDataName = self.yMenu.currentText()
        # pressure should be on a log scale
        if "pressure" in self.yDataName.lower():
            self.figureWidget.setAxisItems(axisItems={
                'bottom':pg.DateAxisItem(orientation='bottom'),
                #'left': scientificAxisItem(orientation='left')
            })
            self.data_line1.setLogMode(False, True)
            self.data_line2.setLogMode(False, True)
            self.figureWidget.setLogMode(False, True)
        else:
            self.data_line1.setLogMode(False, False)
            self.data_line2.setLogMode(False, False)
            self.figureWidget.setLogMode(False, False)
            self.figureWidget.setAxisItems(axisItems={
                'bottom':pg.DateAxisItem(orientation='bottom')
            })
        self.data_line1.clear()
        self.data_line2.clear()

    def refresh_plot(self):
        # get the latest data from the hardware manager
        data = self.hardwareManager.buffer
        self.figureLegend.clear()

        #xData = [datetime.timestamp(row['Time']) for row in data]
        xData = list(data['Timestamp'])
        if self.yDataName == 'Temperatures (K)':
            y1 = 'Sample T (K)'
            #y1Data = [row[y1] for row in data]
            y1Data = list(data[y1])
            self.data_line1.setData(xData, y1Data,
                                    pen=self.yItems[y1]['pen'], name=y1)
            self.figureLegend.addItem(self.data_line1, y1)
            y2 = 'Setpoint T (K)'
            #y2Data = [row[y2] for row in data]
            y2Data = list(data[y2])
            self.data_line2.setData(xData, y2Data,
                                    pen=self.yItems[y2]['pen'], name=y2)
            self.figureLegend.addItem(self.data_line2, y2)
        else:
            #yData = [row[self.yDataName] for row in data]
            yData = list(data[self.yDataName])
            self.data_line1.setData(xData, yData,
                                    pen=self.yItems[self.yDataName]['pen'],
                                    name=self.yDataName)
        

class ControlTab():
    def __init__(self, parentWindow, debug):
        self.parentWindow = parentWindow
        self.debug = debug
        self.hardwareManager = parentWindow.hardwareManager
        self.valueFont = QFont("Consolas", 30)
        self.titleFont = QFont("Arial", 12)
        
        self.outerLayout = QHBoxLayout()
        self.splitter = QSplitter(Qt.Horizontal)

        # ------------------------------------
        # functional item tabs
        # ------------------------------------
        self.tabs = QTabWidget()
        self.tabs.setFixedWidth(500)

        self.overviewTabWidget = QWidget()
        #self.annealTabWidget.setFixedWidth(500)
        self.overviewTabObject = overviewTab.OverviewTab(self, debug)
        self.overviewTabWidget.setLayout(self.overviewTabObject.outerLayout)
        self.tabs.addTab(self.overviewTabWidget, "Overview")

        self.annealTabWidget = QWidget()
        #self.annealTabWidget.setFixedWidth(500)
        self.annealTabObject = annealTab.AnnealTab(self, debug)
        self.annealTabWidget.setLayout(self.annealTabObject.outerLayout)
        self.tabs.addTab(self.annealTabWidget, "Set Temperature")

        self.acquisitionTab = QWidget()
        self.tabs.addTab(self.acquisitionTab, "Acquire Spectrum")

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

        # timescan plots
        self.plot1 = TimescanPlot(self, self.debug, yData="Temperatures (K)")
        self.plotterLayout.addLayout(self.plot1.layout)
        self.plot2 = TimescanPlot(self, self.debug, yData="MC Pressure (mbar)")
        self.plotterLayout.addLayout(self.plot2.layout)
        self.plot3 = TimescanPlot(self, self.debug, yData="DL Pressure (mbar)")
        self.plotterLayout.addLayout(self.plot3.layout)

        # collection buttons
        self.collectorLayout = QHBoxLayout()
        # start collection button
        self.startColButton = QPushButton("Start Recording")
        self.startColButton.clicked.connect(self.start_recording)
        self.collectorLayout.addWidget(self.startColButton)
        # stop collection button
        self.stopColButton = QPushButton("Stop Recording")
        self.stopColButton.clicked.connect(self.stop_recording)
        self.collectorLayout.addWidget(self.stopColButton)
        self.plotterLayout.addLayout(self.collectorLayout)
        # status light
        self.collectionStatusLabel = QLabel()
        self.collectionStatusLabel.setText("Not Recording")
        self.collectionStatusLabel.setStyleSheet("background-color: lightgrey")
        self.collectionStatusLabel.setAlignment(Qt.AlignCenter)
        self.collectorLayout.addWidget(self.collectionStatusLabel)
        
        """self.outerLayout.addWidget(self.tabs)
        self.outerLayout.addLayout(self.schedulerLayout)
        self.outerLayout.addLayout(self.plotterLayout)"""
        self.splitter.addWidget(self.tabs)
        self.schedulerWrapperWidget = QWidget()
        self.schedulerWrapperWidget.setLayout(self.schedulerLayout)
        self.splitter.addWidget(self.schedulerWrapperWidget)
        self.plotterWrapperWidget = QWidget()
        self.plotterWrapperWidget.setLayout(self.plotterLayout)
        self.splitter.addWidget(self.plotterWrapperWidget)

        self.outerLayout.addWidget(self.splitter)

        self.timer = QTimer()
        self.timer.timeout.connect(self.refresh_figures)
        self.timer.start(self.hardwareManager.polling_rate)

    def refresh_figures(self):
        self.plot1.refresh_plot()
        self.plot2.refresh_plot()
        self.plot3.refresh_plot()

    def start_recording(self):
        self.hardwareManager.start_timescan_collection()
        self.collectionStatusLabel.setText("Recording!")
        self.collectionStatusLabel.setStyleSheet("background-color: lightgreen")

    def stop_recording(self):
        self.hardwareManager.stop_timescan_collection()
        self.collectionStatusLabel.setText("Not Recording")
        self.collectionStatusLabel.setStyleSheet("background-color: lightgrey")
        
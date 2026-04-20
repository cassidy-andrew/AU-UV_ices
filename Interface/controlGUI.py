import sys
import os
import inspect
import pandas as pd

from datetime import datetime

sys.path.insert(0, "Interface/ControlTabs")
import annealTab
import overviewTab
import acquisitionTab
import cryoTab

currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
interfacedir = os.path.dirname(currentdir)
maindir = os.path.dirname(interfacedir)

sys.path.insert(0, maindir)

import matplotlib
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
import matplotlib.animation as animation
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
        super(TSMplCanvas, self).__init__(self.fig)


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
            'Ch0 (V)':{'pen':pg.mkPen('black', width=2)},
            'Ch1 (V)':{'pen':pg.mkPen('black', width=2)},
            'Ch2 (V)':{'pen':pg.mkPen('black', width=2)},
            'Ch3 (V)':{'pen':pg.mkPen('black', width=2)},
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

        self._update_yAxis()

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
            #self.figureWidget.setYRange(1e-10, 1)
            self.data_line1.setLogMode(False, True)
            self.data_line2.setLogMode(False, True)
            self.figureWidget.setLogMode(False, True)
            #self.figureWidget.setDefaultPadding(1)
            self.figureWidget.setRange(rect=None, xRange=None, yRange=(-10, 0),
                                       padding=None, update=True,
                                       disableAutoRange=True)
        else:
            #self.figureWidget.setDefaultPadding(0.02)
            self.figureWidget.setRange(rect=None, xRange=None, yRange=(0, 300),
                                       padding=None, update=True,
                                       disableAutoRange=False)
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
        self.tabs.setMinimumWidth(500)

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

        self.acquisitionTabWidget = QWidget()
        self.acquisitionTabObject = acquisitionTab.AcquisitionTab(self, debug)
        self.acquisitionTabWidget.setLayout(self.acquisitionTabObject.outerLayout)
        self.tabs.addTab(self.acquisitionTabWidget, "Acquire Spectrum")

        self.cryoTabWidget = QWidget()
        self.cryoTabObject = cryoTab.CryoTab(self, debug)
        self.cryoTabWidget.setLayout(self.cryoTabObject.outerLayout)
        self.tabs.addTab(self.cryoTabWidget, "Cryostat")

        self.tabs.setCurrentIndex(0)

        # ------------------------------------
        # Scheduler
        # ------------------------------------
        self.schedulerLayout = QVBoxLayout()

        self.queueTitle = QLabel("Queue")
        self.queueTitle.setFont(self.titleFont)
        self.schedulerLayout.addWidget(self.queueTitle)

        self.queueList = QListWidget()
        self.queueList.setMinimumWidth(300)
        self.queueList.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.queueList.setWordWrap(True)
        self.queueList.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.queueList.setUniformItemSizes(False)
        self.schedulerLayout.addWidget(self.queueList)

        self.startStopLayout = QHBoxLayout()
        self.schedulerLayout.addLayout(self.startStopLayout)

        self.SQBtn = QPushButton("Start")
        self.SQBtn.pressed.connect(self.start_queue)
        self.SQBtn.setFont(self.titleFont)
        self.startStopLayout.addWidget(self.SQBtn)
        self.AQBtn = QPushButton("Abort")
        self.AQBtn.pressed.connect(self.abort_queue)
        self.AQBtn.setFont(self.titleFont)
        self.startStopLayout.addWidget(self.AQBtn)
        self.CQBtn = QPushButton("Clear")
        self.CQBtn.pressed.connect(self.clear_queue)
        self.CQBtn.setFont(self.titleFont)
        self.startStopLayout.addWidget(self.CQBtn)

        self.queueStatusLabel = QLabel()
        self.queueStatusLabel.setText("Not Running")
        self.queueStatusLabel.setStyleSheet("background-color: lightgrey")
        self.queueStatusLabel.setAlignment(Qt.AlignCenter)
        self.schedulerLayout.addWidget(self.queueStatusLabel)

        self.historyTitle = QLabel("History")
        self.historyTitle.setFont(self.titleFont)
        self.schedulerLayout.addWidget(self.historyTitle)

        self.historyList = QListWidget()
        self.historyList.setMinimumWidth(200)
        self.historyList.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.historyList.setWordWrap(True)
        self.historyList.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.historyList.setUniformItemSizes(False)
        self.parentWindow.eventLog.item_added.connect(self.refresh_history)

        #self.historyScrollBar = QScrollBar
        
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
        self.startColButton.clicked.connect(self.start_timescan)
        self.collectorLayout.addWidget(self.startColButton)
        # stop collection button
        self.stopColButton = QPushButton("Stop Recording")
        self.stopColButton.clicked.connect(self.stop_timescan)
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

    def refresh_history(self, event):
        scrollbar = self.historyList.verticalScrollBar()
        at_bottom = scrollbar.value() >= scrollbar.maximum() -2
        self.historyList.addItem(event[10:])
        if at_bottom:
            self.historyList.scrollToBottom()

    def refresh_figures(self):
        self.plot1.refresh_plot()
        self.plot2.refresh_plot()
        self.plot3.refresh_plot()

    def start_timescan(self):
        self.hardwareManager.start_timescan_collection()
        self.collectionStatusLabel.setText("Recording Timescan!")
        self.collectionStatusLabel.setStyleSheet("background-color: lightgreen")

    def stop_timescan(self):
        self.hardwareManager.stop_timescan_collection()
        self.collectionStatusLabel.setText("Not Recording")
        self.collectionStatusLabel.setStyleSheet("background-color: lightgrey")

    def start_queue(self):
        self.queueStatusLabel.setText("Running Queue!")
        self.queueStatusLabel.setStyleSheet("background-color: lightgreen")

    def abort_queue(self):
        self.queueStatusLabel.setText("Not Running")
        self.queueStatusLabel.setStyleSheet("background-color: lightgrey")

    def clear_queue(self):
        self.abort_queue()
        
        
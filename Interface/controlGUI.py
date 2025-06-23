import sys
import os
import inspect

from datetime import datetime

sys.path.insert(0, "Interface/ControlTabs")
import annealTab

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


class TimescanRecorder():
    """
    """
    def __init__(self, parent):
        self.parent = parent
        self.hardwareManager = self.parent.hardwareManager
        self.collecting = False

    def start_collection(self):
        """
        Enables collecting data
        """
        if self.collecting:
            print("Already collecting!")
            return None
        self.data = pd.DataFrame(columns=['Time', 'T (K)'])
        self.collecting = True

    def stop_collection(self):
        """
        Exports the data and ends collection
        """
        if not self.collecting:
            print("Already not collecting!")
            return None
        self.collecting = False
        # export the data
        self.data.to_csv(f"T{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv")

    def collect(self):
        if self.collecting:
            time = datetime.now()
            temp = self.harwdareManager.temperatureController.get_temp()
            this_dict = {'Time':time, 'T (K)':temp}
            self.data = pd.concat([self.data, this_dict], ignore_index=True)


class ControlTab():
    def __init__(self, parentWindow, debug):
        self.parentWindow = parentWindow
        self.hardwareManager = parentWindow.hardwareManager
        self.valueFont = QFont("Consolas", 30)
        self.titleFont = QFont("Arial", 12)
        self.TSRecorder = TimescanRecorder(self)
        self.hardwareManager.add_refresh_function(self.TSRecorder.collect)
        
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
        self.tempTimeAxis = pg.AxisItem('bottom')
        self.tempFig = pg.PlotWidget(self.parentWindow, title='Temperature',
                                     axisItems={'bottom':self.tempTimeAxis})
        self.tempFig.setBackground(background=None)
        self.plotterLayout.addWidget(self.tempFig)
        self.tempFig.setMinimumWidth(500)

        # pressure plot
        self.pressureTimeAxis = pg.AxisItem('bottom')
        self.pressureFig = pg.PlotWidget(self.parentWindow, title='Pressure',
                                    axisItems={'bottom':self.pressureTimeAxis})
        self.pressureFig.setBackground(background=None)
        self.pressureFig.setLogMode(None, True)
        self.plotterLayout.addWidget(self.pressureFig)
        self.pressureFig.setMinimumWidth(500)

        # laser plot
        self.laserTimeAxis = pg.AxisItem('bottom')
        self.laserFig = pg.PlotWidget(self.parentWindow, title='Laser Signal',
                                     axisItems={'bottom':self.laserTimeAxis})
        self.laserFig.setBackground(background=None)
        self.plotterLayout.addWidget(self.laserFig)
        self.laserFig.setMinimumWidth(500)

        # collection buttons
        self.collectorLayout = QHBoxLayout()
        # start collection button
        self.startColButton = QPushButton("Start Collection")
        self.startColButton.clicked.connect(self.TSRecorder.start_collection)
        self.collectorLayout.addWidget(self.startColButton)
        # stop collection button
        self.stopColButton = QPushButton("Stop Collection")
        self.stopColButton.clicked.connect(self.TSRecorder.stop_collection)
        self.collectorLayout.addWidget(self.stopColButton)

        self.plotterLayout.addLayout(self.collectorLayout)
        

        self.outerLayout.addWidget(self.tabs)
        self.outerLayout.addLayout(self.schedulerLayout)
        self.outerLayout.addLayout(self.plotterLayout)
        
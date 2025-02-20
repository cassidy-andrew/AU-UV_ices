import sys
import os
import inspect

import annealTab

currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, parentdir+'/Tools')
import tempTools
import depTools

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

class ControlTab():
    def __init__(self, parentWindow, debug):
        self.parentWindow = parentWindow
        self.valueFont = QFont("Consolas", 30)
        self.titleFont = QFont("Arial", 12)
        
        self.outerLayout = QHBoxLayout()

        # ------------------------------------
        # functional item tabs
        # ------------------------------------
        self.tabs = QTabWidget()
        self.tabs.setFixedWidth(500)

        self.annealTabWidget = QWidget()
        #self.annealTabWidget.setFixedWidth(500)
        self.annealTabObject = annealTab.AnnealTab(debug)
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
        

        self.outerLayout.addWidget(self.tabs)
        self.outerLayout.addLayout(self.schedulerLayout)
        self.outerLayout.addLayout(self.plotterLayout)
        
import sys
import os
import inspect

currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)

sys.path.insert(0, parentdir)
from duvet import center

sys.path.insert(0, parentdir+'/Tools')
import specTools
import depTools

sys.path.insert(0, "Interface/AnalysisTabs")
import spectraTab
import timescanTab

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

class AnalysisTab():
    def __init__(self, parentWindow, debug):
        self.parentWindow = parentWindow
        self.valueFont = QFont("Consolas", 30)
        self.titleFont = QFont("Arial", 12)
        
        self.outerLayout = QHBoxLayout()
        
        # ------------------------------------
        # functional item tabs
        # ------------------------------------
        self.tabs = QTabWidget()
        #self.tabs.setFixedWidth(500)

        self.spectrumTabWidget = QWidget()
        #self.annealTabWidget.setFixedWidth(500)
        self.spectrumTabObject = spectraTab.spectrumDisplayTab(self, debug)
        self.spectrumTabWidget.setLayout(self.spectrumTabObject.outerLayout)
        self.tabs.addTab(self.spectrumTabWidget,
                         "Photoabsorption Spectra Analysis")

        self.timescanTab = QWidget()
        self.tabs.addTab(self.timescanTab, "Timescan Analysis")

        self.outerLayout.addWidget(self.tabs)

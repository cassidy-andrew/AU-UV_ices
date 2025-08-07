import sys
import os
import inspect

currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
maindir = os.path.dirname(currentdir)

sys.path.insert(0, maindir)

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

from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.Qt import *


class configViewWindow(QWidget):
    """
    A window for viewing the current configuration of DUVET, such as the
    hardware polling rate and save directory.
    """
    def __init__(self, parent):
        super().__init__()
        self.parent = parent

        self.setWindowTitle(f'DUVET Current Configuration')

        # define fonts
        self.titleFontA = QFont("Arial", 15)
        self.valueFontA = QFont("Consolas", 12)

        self.outerLayout = QVBoxLayout()

        # this is good for making things a little easier to read
        self.verticalSpacer = QSpacerItem(10, 10)   # x, y

        self.saveDirLabel = QLabel(
            f'Save Directory =  "{self.parent.config["save_directory"]}"'
        )
        self.saveDirLabel.setFont(self.valueFontA)
        #self.saveDirLabel.setAlignment(Qt.AlignHCenter)
        self.outerLayout.addWidget(self.saveDirLabel)
        self.outerLayout.addItem(self.verticalSpacer)

        self.PRLabel = QLabel(
            f'Polling Rate =  {self.parent.config["polling_rate"]} ms'
        )
        self.PRLabel.setFont(self.valueFontA)
        #self.PRLabel.setAlignment(Qt.AlignHCenter)
        self.outerLayout.addWidget(self.PRLabel)
        self.outerLayout.addItem(self.verticalSpacer)

        self.setLayout(self.outerLayout)

    def refresh(self):
        self.saveDirLabel.setText(
            f'Save Directory =  "{self.parent.config["save_directory"]}"'
        )
        self.PRLabel.setText(
            f'Polling Rate =  {self.parent.config["polling_rate"]} ms'
        )

    def show_window(self):
        self.show()


class ScrollLabel(QScrollArea):
    def __init__(self, *args, **kwargs):
        QScrollArea.__init__(self, *args, **kwargs)
        self.setWidgetResizable(True)
        content = QWidget(self)
        self.setWidget(content)
        self.layout = QVBoxLayout(content)
        self.label = QLabel(content)
        self.label.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        self.label.setWordWrap(True)
        #self.label.setMinimumWidth(600)
        #self.label.setMinimumHeight(400)
        self.layout.addWidget(self.label)

    def setText(self, text):
        self.label.setText(text)

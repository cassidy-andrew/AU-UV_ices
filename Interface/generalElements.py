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


class bigNumbersViewWindow(QWidget):
    """
    A window for displaying the most important parameters in huge, high contrast
    text, readable from across the room. There are four corners with values. In
    the future these should be adjustable to display whatever you want. For now,
    they just display the substrate temperature, setpoint temperature, main
    chamber pressure, and dosing line pressure.
    """
    def __init__(self, parent):
        super().__init__()
        self.parent = parent

        self.setWindowTitle("DUVET BIG NUMBER VIEWER")

        # define fonts
        self.titleFontA = QFont("Arial", 30)
        self.valueFontA = QFont("Consolas", 60)

        self.outerLayout = QGridLayout()

        # -----------------------------------------
        # Measured Temperature
        # -----------------------------------------
        self.measuredTempLayout = QVBoxLayout()
        self.measuredTempLayout.addItem(self.verticalSpacer)
        
        # measured temperature display title
        self.mtLabelTitle = QLabel("Sample Temperature (K)")
        self.mtLabelTitle.setFont(self.titleFontA)
        self.mtLabelTitle.setAlignment(Qt.AlignHCenter)
        self.measuredTempLayout.addWidget(self.mtLabelTitle)

        # measured temperature display value
        self.measured_temperature = "No Signal Yet"
        self.mtLabel = QLabel(self.measured_temperature)
        self.mtLabel.setFont(self.valueFontA)
        self.mtLabel.setAlignment(Qt.AlignHCenter)
        self.measuredTempLayout.addWidget(self.mtLabel)
        
        self.measuredTempLayout.addItem(self.verticalSpacer)
        self.outerLayout.addLayout(self.measuredTempLayout, 0, 0)

        # -----------------------------------------
        # Current set point
        # -----------------------------------------
        self.measuredSetPointLayout = QVBoxLayout()
        
        # measured set point display title
        self.mspLabelTitle = QLabel("Setpoint Temperature (K)")
        self.mspLabelTitle.setFont(self.titleFontA)
        self.mspLabelTitle.setAlignment(Qt.AlignHCenter)
        self.measuredSetPointLayout.addWidget(self.mspLabelTitle)

        # measured temperature display value
        self.measured_set_point = "No Signal Yet"
        self.mspLabel = QLabel(self.measured_temperature)
        self.mspLabel.setFont(self.valueFontA)
        self.mspLabel.setAlignment(Qt.AlignHCenter)
        self.measuredSetPointLayout.addWidget(self.mspLabel)
        
        self.measuredSetPointLayout.addItem(self.verticalSpacer)
        self.outerLayout.addLayout(self.measuredSetPointLayout, 0, 1)

        # -----------------------------------------
        # Main Chamber Pressure
        # -----------------------------------------
        self.mcpLayout = QVBoxLayout()
        
        # display title
        self.mcpLabelTitle = QLabel("Main Chamber Pressure (mbar)")
        self.mcpLabelTitle.setFont(self.titleFontA)
        self.mcpLabelTitle.setAlignment(Qt.AlignHCenter)
        self.mcpLayout.addWidget(self.mcpLabelTitle)

        # display value
        self.mcp = "No Signal Yet"
        self.mcpLabel = QLabel(self.mcp)
        self.mcpLabel.setFont(self.valueFontA)
        self.mcpLabel.setAlignment(Qt.AlignHCenter)
        self.mcpLayout.addWidget(self.mcpLabel)
        
        self.mcpLayout.addItem(self.verticalSpacer)
        self.outerLayout.addLayout(self.mcpLayout, 1, 0)

        # -----------------------------------------
        # Dosing Line Pressure
        # -----------------------------------------

        self.dlpLayout = QVBoxLayout()
        
        # display title
        self.dlpLabelTitle = QLabel("Dosing Line Pressure (mbar)")
        self.dlpLabelTitle.setFont(self.titleFontA)
        self.dlpLabelTitle.setAlignment(Qt.AlignHCenter)
        self.dlpLayout.addWidget(self.dlpLabelTitle)

        # display value
        self.dlp = "No Signal Yet"
        self.dlpLabel = QLabel(self.dlp)
        self.dlpLabel.setFont(self.valueFontA)
        self.dlpLabel.setAlignment(Qt.AlignHCenter)
        self.dlpLayout.addWidget(self.dlpLabel)
        
        self.dlpLayout.addItem(self.verticalSpacer)
        self.outerLayout.addLayout(self.dlpLayout, 1, 1)

        self.timer = QTimer()
        self.timer.timeout.connect(self.refresh)
        self.timer.start(self.parent.hardwareManager.polling_rate)

    def refresh(self):
        """
        Update all values
        """
        #measured_values = self.parent.hardwareManager.buffer[-1]
        measured_values = {}
        for key in self.parent.hardwareManager.buffer:
            measured_values[key] = self.parent.hardwareManager.buffer[key][-1]
        # measured temperature
        self.mtLabel.setText(str(measured_values['Sample T (K)']))
        # current target temperature
        self.mspLabel.setText(str(measured_values['Setpoint T (K)']))

        self.mcpLabel.setText(
            f"{measured_values['MC Pressure (mbar)']:.2e}")
        self.dlpLabel.setText(
            f"{measured_values['DL Pressure (mbar)']:.2e}")


class configViewWindow(QWidget):
    """
    A window for viewing the current configuration of DUVET, such as the
    hardware polling rate and save directory.
    """
    def __init__(self, parent):
        super().__init__()
        self.parent = parent

        self.setWindowTitle('DUVET Current Configuration')

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

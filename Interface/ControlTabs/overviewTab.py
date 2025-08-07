import sys
import os
import inspect
import json

from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.Qt import *

class OverviewTab():
    def __init__(self, parent, debug):
        """
        A tab for viewing the most important parameters in big font
        """
        self.parent = parent
        self.debug = debug

        # define fonts
        self.valueFontA = QFont("Consolas", 30)
        self.titleFontA = QFont("Arial", 15)
        self.valueFontB = QFont("Consolas", 15)
        self.titleFontB = QFont("Arial", 10)

        # where we hold all the smaller UI elements
        self.outerLayout = QGridLayout()

        # this is good for making the tab a little easier to read
        self.verticalSpacer = QSpacerItem(20, 20)   # x, y

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
        self.outerLayout.addLayout(self.measuredSetPointLayout, 1, 0)

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
        self.outerLayout.addLayout(self.mcpLayout, 2, 0)

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
        self.outerLayout.addLayout(self.dlpLayout, 3, 0)

        # -----------------------------------------
        # Configuration & Logistics
        # -----------------------------------------

        # this helps formatting the rows so they stay at the top of the tab
        self.outerLayout.setRowStretch(self.outerLayout.rowCount(), 1)

        # configure update timer to refresh the data
        #self.parent.hardwareManager.add_refresh_function(
        #    self.refresh_controller
        #)
        self.timer = QTimer()
        self.timer.timeout.connect(self.refresh)
        self.timer.start(self.hardwareManager.polling_rate)

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
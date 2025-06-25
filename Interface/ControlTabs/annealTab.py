import sys
import os
import inspect
import json

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
    QTextEdit,
    QDialog,
    QScrollArea,
    QComboBox,
    QAbstractItemView,
    QSpacerItem
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

class AnnealTab():
    def __init__(self, parent, debug):
        """
        A tab for annealing stuff with!
        """
        self.parent = parent
        self.debug = debug

        # temperature controller hardware!
        self.tempController = parent.hardwareManager.temperatureController

        # define fonts
        self.valueFont = QFont("Consolas", 15)
        self.titleFont = QFont("Arial", 10)

        # where we hold all the smaller UI elements
        self.outerLayout = QGridLayout()

        # this is good for making the tab a little easier to read
        self.verticalSpacer = QSpacerItem(20, 20)   # x, y

        # -----------------------------------------
        # Temperature
        # -----------------------------------------
        self.measuredTempLayout = QVBoxLayout()
        self.measuredTempLayout.addItem(self.verticalSpacer)
        
        # measured temperature display title
        self.mtLabelTitle = QLabel("Measured Temperature (K)")
        self.mtLabelTitle.setFont(self.titleFont)
        self.mtLabelTitle.setAlignment(Qt.AlignHCenter)
        self.measuredTempLayout.addWidget(self.mtLabelTitle)

        # measured temperature display value
        self.measured_temperature = "No Signal Yet"
        self.mtLabel = QLabel(self.measured_temperature)
        self.mtLabel.setFont(self.valueFont)
        self.mtLabel.setAlignment(Qt.AlignHCenter)
        self.measuredTempLayout.addWidget(self.mtLabel)
        
        self.measuredTempLayout.addItem(self.verticalSpacer)
        self.outerLayout.addLayout(self.measuredTempLayout, 0, 0)

        self.targetTempLayout = QVBoxLayout()
        self.targetTempLayout.addItem(self.verticalSpacer)

        # target temperature display title
        self.targetTitle = QLabel("Set Target Temperature (K)")
        self.targetTitle.setFont(self.titleFont)
        self.targetTitle.setAlignment(Qt.AlignHCenter)
        self.targetTempLayout.addWidget(self.targetTitle)

        # target temperature display value
        self.target_temperature = 300
        self.tempLineEdit = QDoubleSpinBox()
        self.tempLineEdit.setRange(0.0, 999.0)
        self.tempLineEdit.setDecimals(1)
        self.tempLineEdit.setSingleStep(1)
        self.tempLineEdit.setFont(self.valueFont)
        self.tempLineEdit.setValue(self.target_temperature)
        self.tempLineEdit.editingFinished.connect(
            lambda: self.set_target_temperature(self.tempLineEdit.text())
            )
        self.tempLineEdit.setAlignment(Qt.AlignHCenter)
        self.targetTempLayout.addWidget(self.tempLineEdit)
        
        self.targetTempLayout.addItem(self.verticalSpacer)
        self.outerLayout.addLayout(self.targetTempLayout, 0, 1)

        # -----------------------------------------
        # Current set point
        # -----------------------------------------
        self.measuredSetPointLayout = QVBoxLayout()
        
        # measured set point display title
        self.mspLabelTitle = QLabel("Current Target Temperature (K)")
        self.mspLabelTitle.setFont(self.titleFont)
        self.mspLabelTitle.setAlignment(Qt.AlignHCenter)
        self.measuredSetPointLayout.addWidget(self.mspLabelTitle)

        # measured temperature display value
        self.measured_set_point = "No Signal Yet"
        self.mspLabel = QLabel(self.measured_temperature)
        self.mspLabel.setFont(self.valueFont)
        self.mspLabel.setAlignment(Qt.AlignHCenter)
        self.measuredSetPointLayout.addWidget(self.mspLabel)
        
        self.measuredSetPointLayout.addItem(self.verticalSpacer)
        self.outerLayout.addLayout(self.measuredSetPointLayout, 1, 0)

        # -----------------------------------------
        # Power Setting
        # -----------------------------------------
        self.powerSettingLayout = QVBoxLayout()
        
        # measured power setting title
        self.mpsLabelTitle = QLabel("Power Setting")
        self.mpsLabelTitle.setFont(self.titleFont)
        self.mpsLabelTitle.setAlignment(Qt.AlignHCenter)
        self.powerSettingLayout.addWidget(self.mpsLabelTitle)

        # measured power setting value
        self.measured_power_setting = "No Signal Yet"
        self.mpsLabel = QLabel(self.measured_power_setting)
        self.mpsLabel.setFont(self.valueFont)
        self.mpsLabel.setAlignment(Qt.AlignHCenter)
        self.powerSettingLayout.addWidget(self.mpsLabel)
        
        self.powerSettingLayout.addItem(self.verticalSpacer)
        self.outerLayout.addLayout(self.powerSettingLayout, 2, 0)

        self.powerTargetLayout = QVBoxLayout()

        # target power setting title
        self.targetPowerLabel = QLabel("Set Power Setting")
        self.targetPowerLabel.setFont(self.titleFont)
        self.targetPowerLabel.setAlignment(Qt.AlignHCenter)
        self.powerTargetLayout.addWidget(self.targetPowerLabel)

        # target power setting value
        self.targetPowerComboBox = QComboBox()
        self.targetPowerComboBox.addItem("LOW")
        self.targetPowerComboBox.addItem("MEDIUM")
        self.targetPowerComboBox.addItem("HIGH")
        self.targetPowerComboBox.setFont(self.valueFont)
        #self.targetPowerComboBox.currentTextChanged.connect()
        self.powerTargetLayout.addWidget(self.targetPowerComboBox)
        
        self.powerTargetLayout.addItem(self.verticalSpacer)
        self.outerLayout.addLayout(self.powerTargetLayout, 2, 1)

        # -----------------------------------------
        # Power Level
        # -----------------------------------------
        self.powerLevelLayout = QVBoxLayout()

        # measured power level title
        self.plLabelTitle = QLabel("Power Level")
        self.plLabelTitle.setFont(self.titleFont)
        self.plLabelTitle.setAlignment(Qt.AlignHCenter)
        self.powerLevelLayout.addWidget(self.plLabelTitle)

        # measured power level label
        self.measured_power_level = "No Signal Yet"
        self.plLabel = QLabel(self.measured_power_level)
        self.plLabel.setFont(self.valueFont)
        self.plLabel.setAlignment(Qt.AlignHCenter)
        self.powerLevelLayout.addWidget(self.plLabel)
        
        self.powerLevelLayout.addItem(self.verticalSpacer)
        self.outerLayout.addLayout(self.powerLevelLayout, 3, 0)

        # -----------------------------------------
        # Ramp Rate
        # -----------------------------------------
        self.measuredRRLayout = QVBoxLayout()
        
        # measured ramp rate display title
        self.mrrLabelTitle = QLabel("Ramp Rate (K/min)")
        self.mrrLabelTitle.setFont(self.titleFont)
        self.mrrLabelTitle.setAlignment(Qt.AlignHCenter)
        self.measuredRRLayout.addWidget(self.mrrLabelTitle)

        # measured ramp rate display value
        self.measured_ramp_rate = "No Signal Yet"
        self.mrrLabel = QLabel(self.measured_ramp_rate)
        self.mrrLabel.setFont(self.valueFont)
        self.mrrLabel.setAlignment(Qt.AlignHCenter)
        self.measuredRRLayout.addWidget(self.mrrLabel)
        
        self.measuredRRLayout.addItem(self.verticalSpacer)
        self.outerLayout.addLayout(self.measuredRRLayout, 4, 0)

        self.targetRRLayout = QVBoxLayout()

        # target ramp rate display title
        self.trrTitle = QLabel("Set Ramp Rate (K/min)")
        self.trrTitle.setFont(self.titleFont)
        self.trrTitle.setAlignment(Qt.AlignHCenter)
        self.targetRRLayout.addWidget(self.trrTitle)

        # target ramp rate display value
        self.target_ramp_rate = 5
        self.rrLineEdit = QDoubleSpinBox()
        self.rrLineEdit.setRange(0.0, 100.0)
        self.rrLineEdit.setDecimals(3)
        self.rrLineEdit.setSingleStep(0.5)
        self.rrLineEdit.setFont(self.valueFont)
        self.rrLineEdit.setValue(self.target_ramp_rate)
        #self.rrLineEdit.editingFinished.connect()
        self.rrLineEdit.setAlignment(Qt.AlignHCenter)
        self.targetRRLayout.addWidget(self.rrLineEdit)
        
        self.targetRRLayout.addItem(self.verticalSpacer)
        self.outerLayout.addLayout(self.targetRRLayout, 4, 1)

        # -----------------------------------------
        # Heater Status
        # -----------------------------------------
        self.measuredHeaterStatusLayout = QVBoxLayout()

        # measured heater status display title
        self.mhsLabelTitle = QLabel("Heater Status")
        self.mhsLabelTitle.setFont(self.titleFont)
        self.mhsLabelTitle.setAlignment(Qt.AlignHCenter)
        self.measuredHeaterStatusLayout.addWidget(self.mhsLabelTitle)

        # measured  heater status display value
        self.measured_heater_status = "No Signal Yet"
        self.mhsLabel = QLabel(self.measured_heater_status)
        self.mhsLabel.setFont(self.valueFont)
        self.mhsLabel.setAlignment(Qt.AlignHCenter)
        self.measuredHeaterStatusLayout.addWidget(self.mhsLabel)
        
        self.measuredHeaterStatusLayout.addItem(self.verticalSpacer)
        self.outerLayout.addLayout(self.measuredHeaterStatusLayout, 5, 0)

        # -----------------------------------------
        # OFF button
        # -----------------------------------------
        self.OFFLayout = QVBoxLayout()

        # OFF title
        self.OFFTitle = QLabel("Turn the Heater Off (Skips Queue)")
        self.OFFTitle.setFont(self.titleFont)
        self.OFFTitle.setAlignment(Qt.AlignHCenter)
        self.OFFLayout.addWidget(self.OFFTitle)

        # OFF button
        self.OFFButton = QPushButton("OFF")
        self.OFFButton.pressed.connect(self.heater_off)
        self.OFFButton.setFont(self.valueFont)
        self.OFFButton.setStyleSheet("background-color : red")
        self.OFFLayout.addWidget(self.OFFButton)
        self.OFFLayout.addItem(self.verticalSpacer)
        self.outerLayout.addLayout(self.OFFLayout, 6, 1)

        self.OFFWithQueueLayout = QVBoxLayout()

        # OFF with queue title
        self.OFFWQTitle = QLabel("Turn the Heater Off (Adds to Queue)")
        self.OFFWQTitle.setFont(self.titleFont)
        self.OFFWQTitle.setAlignment(Qt.AlignHCenter)
        self.OFFWithQueueLayout.addWidget(self.OFFWQTitle)

        # OFF with queue button
        self.OFFWQButton = QPushButton("OFF")
        #self.OFFWQButton.pressed.connect()
        self.OFFWQButton.setFont(self.valueFont)
        self.OFFWithQueueLayout.addWidget(self.OFFWQButton)
        self.OFFWithQueueLayout.addItem(self.verticalSpacer)
        self.outerLayout.addLayout(self.OFFWithQueueLayout, 5, 1)

        # -----------------------------------------
        # Configuration & Logistics
        # -----------------------------------------

        # this helps formatting the rows so they stay at the top of the tab
        self.outerLayout.setRowStretch(self.outerLayout.rowCount(), 1)

        # configure update timer to refresh the data
        self.parent.hardwareManager.add_refresh_function(
            self.refresh_controller
        )

    def refresh_controller(self):
        """
        Update all values from the temperature controller.
        """
        measured_values = self.parent.hardwareManager.data.iloc[-1]
        # measured temperature
        self.mtLabel.setText(str(measured_values['Temperature (K)']))
        # current target temperature
        self.mspLabel.setText(str(measured_values['Setpoint (K)']))
        # heater power setting / range
        #self.mpsLabel.setText(self.measured_power_setting)
        # heater power percent of maximum
        self.plLabel.setText(str(measured_values['Heater Power (%)']))
        # ramp rate
        #self.mrrLabel.setText(self.measured_ramp_rate)
        # heater status
        #self.mhsLabel.setText(self.heater_status)

    def set_target_temperature(self, target):
        self.tempController.set_temp(target)

    def heater_off(self):
        """
        Turns the heater off
        """
        
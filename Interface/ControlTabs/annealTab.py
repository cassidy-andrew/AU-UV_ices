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
        self.valueFontA = QFont("Consolas", 30)
        self.titleFontA = QFont("Arial", 15)
        self.valueFontB = QFont("Consolas", 15)
        self.titleFontB = QFont("Arial", 10)

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

        self.targetTempLayout = QVBoxLayout()
        self.targetTempLayout.addItem(self.verticalSpacer)

        # target temperature display title
        self.targetTitle = QLabel("Set Target Temperature (K)")
        self.targetTitle.setFont(self.titleFontB)
        self.targetTitle.setAlignment(Qt.AlignHCenter)
        self.targetTempLayout.addWidget(self.targetTitle)

        # target temperature display value
        self.target_temperature = 300
        self.tempLineEdit = QDoubleSpinBox()
        self.tempLineEdit.setRange(0.0, 999.0)
        self.tempLineEdit.setDecimals(1)
        self.tempLineEdit.setSingleStep(1)
        self.tempLineEdit.setFont(self.valueFontB)
        self.tempLineEdit.setValue(self.target_temperature)
        self.tempLineEdit.editingFinished.connect(
            lambda: self.set_target_temperature(self.tempLineEdit.text())
            )
        self.tempLineEdit.setAlignment(Qt.AlignHCenter)
        self.targetTempLayout.addWidget(self.tempLineEdit)
        
        self.targetTempLayout.addItem(self.verticalSpacer)
        #self.outerLayout.addLayout(self.targetTempLayout, 0, 1)

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
        # Power Setting
        # -----------------------------------------
        self.powerSettingLayout = QVBoxLayout()
        
        # measured power setting title
        self.mpsLabelTitle = QLabel("Power Setting")
        self.mpsLabelTitle.setFont(self.titleFontB)
        self.mpsLabelTitle.setAlignment(Qt.AlignHCenter)
        self.powerSettingLayout.addWidget(self.mpsLabelTitle)

        # measured power setting value
        self.measured_power_setting = "No Signal Yet"
        self.mpsLabel = QLabel(self.measured_power_setting)
        self.mpsLabel.setFont(self.valueFontB)
        self.mpsLabel.setAlignment(Qt.AlignHCenter)
        self.powerSettingLayout.addWidget(self.mpsLabel)
        
        self.powerSettingLayout.addItem(self.verticalSpacer)
        #self.outerLayout.addLayout(self.powerSettingLayout, 2, 0)

        self.powerTargetLayout = QVBoxLayout()

        # target power setting title
        self.targetPowerLabel = QLabel("Set Power Setting")
        self.targetPowerLabel.setFont(self.titleFontB)
        self.targetPowerLabel.setAlignment(Qt.AlignHCenter)
        self.powerTargetLayout.addWidget(self.targetPowerLabel)

        # target power setting value
        self.targetPowerComboBox = QComboBox()
        self.targetPowerComboBox.addItem("LOW")
        self.targetPowerComboBox.addItem("MEDIUM")
        self.targetPowerComboBox.addItem("HIGH")
        self.targetPowerComboBox.setFont(self.valueFontB)
        #self.targetPowerComboBox.currentTextChanged.connect()
        self.powerTargetLayout.addWidget(self.targetPowerComboBox)
        
        self.powerTargetLayout.addItem(self.verticalSpacer)
        #self.outerLayout.addLayout(self.powerTargetLayout, 2, 1)

        # -----------------------------------------
        # Power Level
        # -----------------------------------------
        self.powerLevelLayout = QVBoxLayout()

        # measured power level title
        self.plLabelTitle = QLabel("Power Level (%)")
        self.plLabelTitle.setFont(self.titleFontB)
        self.plLabelTitle.setAlignment(Qt.AlignHCenter)
        self.powerLevelLayout.addWidget(self.plLabelTitle)

        # measured power level label
        self.measured_power_level = "No Signal Yet"
        self.plLabel = QLabel(self.measured_power_level)
        self.plLabel.setFont(self.valueFontB)
        self.plLabel.setAlignment(Qt.AlignHCenter)
        self.powerLevelLayout.addWidget(self.plLabel)
        
        self.powerLevelLayout.addItem(self.verticalSpacer)
        self.outerLayout.addLayout(self.powerLevelLayout, 3, 0)

        # -----------------------------------------
        # PID Values
        # -----------------------------------------
        self.pidPLayout = QVBoxLayout()
        # measured PID P title
        self.pidPLabelTitle = QLabel("Proportional Band (%)")
        self.pidPLabelTitle.setFont(self.titleFontB)
        self.pidPLabelTitle.setAlignment(Qt.AlignHCenter)
        self.pidPLayout.addWidget(self.pidPLabelTitle)
        # measured PID P label
        self.measured_pidP = "No Signal Yet"
        self.pidPLabel = QLabel(self.measured_pidP)
        self.pidPLabel.setFont(self.valueFontB)
        self.pidPLabel.setAlignment(Qt.AlignHCenter)
        self.pidPLayout.addWidget(self.pidPLabel)
        # add it to the layout
        self.pidPLayout.addItem(self.verticalSpacer)
        self.outerLayout.addLayout(self.pidPLayout, 4, 0)

        self.pidILayout = QVBoxLayout()
        # measured PID I title
        self.pidILabelTitle = QLabel("Integral Action Time (min)")
        self.pidILabelTitle.setFont(self.titleFontB)
        self.pidILabelTitle.setAlignment(Qt.AlignHCenter)
        self.pidILayout.addWidget(self.pidILabelTitle)
        # measured PID I label
        self.measured_pidI = "No Signal Yet"
        self.pidILabel = QLabel(self.measured_pidI)
        self.pidILabel.setFont(self.valueFontB)
        self.pidILabel.setAlignment(Qt.AlignHCenter)
        self.pidILayout.addWidget(self.pidILabel)
        # add it to the layout
        self.pidILayout.addItem(self.verticalSpacer)
        self.outerLayout.addLayout(self.pidILayout, 5, 0)

        self.pidDLayout = QVBoxLayout()
        # measured PID D title
        self.pidDLabelTitle = QLabel("Derivative Action Time (min)")
        self.pidDLabelTitle.setFont(self.titleFontB)
        self.pidDLabelTitle.setAlignment(Qt.AlignHCenter)
        self.pidDLayout.addWidget(self.pidDLabelTitle)
        # measured PID D label
        self.measured_pidD = "No Signal Yet"
        self.pidDLabel = QLabel(self.measured_pidD)
        self.pidDLabel.setFont(self.valueFontB)
        self.pidDLabel.setAlignment(Qt.AlignHCenter)
        self.pidDLayout.addWidget(self.pidDLabel)
        # add it to the layout
        self.pidDLayout.addItem(self.verticalSpacer)
        self.outerLayout.addLayout(self.pidDLayout, 6, 0)

        # -----------------------------------------
        # Ramp Rate
        # -----------------------------------------
        self.measuredRRLayout = QVBoxLayout()
        
        # measured ramp rate display title
        self.mrrLabelTitle = QLabel("Ramp Rate (K/min)")
        self.mrrLabelTitle.setFont(self.titleFontB)
        self.mrrLabelTitle.setAlignment(Qt.AlignHCenter)
        self.measuredRRLayout.addWidget(self.mrrLabelTitle)

        # measured ramp rate display value
        self.measured_ramp_rate = "No Signal Yet"
        self.mrrLabel = QLabel(self.measured_ramp_rate)
        self.mrrLabel.setFont(self.valueFontB)
        self.mrrLabel.setAlignment(Qt.AlignHCenter)
        self.measuredRRLayout.addWidget(self.mrrLabel)
        
        self.measuredRRLayout.addItem(self.verticalSpacer)
        #self.outerLayout.addLayout(self.measuredRRLayout, 4, 0)

        self.targetRRLayout = QVBoxLayout()

        # target ramp rate display title
        self.trrTitle = QLabel("Set Ramp Rate (K/min)")
        self.trrTitle.setFont(self.titleFontB)
        self.trrTitle.setAlignment(Qt.AlignHCenter)
        self.targetRRLayout.addWidget(self.trrTitle)

        # target ramp rate display value
        self.target_ramp_rate = 5
        self.rrLineEdit = QDoubleSpinBox()
        self.rrLineEdit.setRange(0.0, 100.0)
        self.rrLineEdit.setDecimals(3)
        self.rrLineEdit.setSingleStep(0.5)
        self.rrLineEdit.setFont(self.valueFontB)
        self.rrLineEdit.setValue(self.target_ramp_rate)
        #self.rrLineEdit.editingFinished.connect()
        self.rrLineEdit.setAlignment(Qt.AlignHCenter)
        self.targetRRLayout.addWidget(self.rrLineEdit)
        
        self.targetRRLayout.addItem(self.verticalSpacer)
        #self.outerLayout.addLayout(self.targetRRLayout, 4, 1)

        # -----------------------------------------
        # Heater Status
        # -----------------------------------------
        self.measuredHeaterStatusLayout = QVBoxLayout()

        # measured heater status display title
        self.mhsLabelTitle = QLabel("Heater Status")
        self.mhsLabelTitle.setFont(self.titleFontB)
        self.mhsLabelTitle.setAlignment(Qt.AlignHCenter)
        self.measuredHeaterStatusLayout.addWidget(self.mhsLabelTitle)

        # measured  heater status display value
        self.measured_heater_status = "No Signal Yet"
        self.mhsLabel = QLabel(self.measured_heater_status)
        self.mhsLabel.setFont(self.valueFontB)
        self.mhsLabel.setAlignment(Qt.AlignHCenter)
        self.measuredHeaterStatusLayout.addWidget(self.mhsLabel)
        
        self.measuredHeaterStatusLayout.addItem(self.verticalSpacer)
        #self.outerLayout.addLayout(self.measuredHeaterStatusLayout, 5, 0)

        # -----------------------------------------
        # Pressure
        # -----------------------------------------
        self.mcpLayout = QVBoxLayout()
        
        # display title
        self.mcpLabelTitle = QLabel("Main Chamber Pressure (mbar)")
        self.mcpLabelTitle.setFont(self.titleFontB)
        self.mcpLabelTitle.setAlignment(Qt.AlignHCenter)
        self.mcpLayout.addWidget(self.mcpLabelTitle)

        # display value
        self.mcp = "No Signal Yet"
        self.mcpLabel = QLabel(self.mcp)
        self.mcpLabel.setFont(self.valueFontB)
        self.mcpLabel.setAlignment(Qt.AlignHCenter)
        self.mcpLayout.addWidget(self.mcpLabel)
        
        self.mcpLayout.addItem(self.verticalSpacer)
        self.outerLayout.addLayout(self.mcpLayout, 7, 0)

        self.dlpLayout = QVBoxLayout()
        
        # display title
        self.dlpLabelTitle = QLabel("Dosing Line Pressure (mbar)")
        self.dlpLabelTitle.setFont(self.titleFontB)
        self.dlpLabelTitle.setAlignment(Qt.AlignHCenter)
        self.dlpLayout.addWidget(self.dlpLabelTitle)

        # display value
        self.dlp = "No Signal Yet"
        self.dlpLabel = QLabel(self.dlp)
        self.dlpLabel.setFont(self.valueFontB)
        self.dlpLabel.setAlignment(Qt.AlignHCenter)
        self.dlpLayout.addWidget(self.dlpLabel)
        
        self.dlpLayout.addItem(self.verticalSpacer)
        self.outerLayout.addLayout(self.dlpLayout, 7, 1)

        # -----------------------------------------
        # OFF button
        # -----------------------------------------
        self.OFFLayout = QVBoxLayout()

        # OFF title
        self.OFFTitle = QLabel("Turn the Heater Off (Skips Queue)")
        self.OFFTitle.setFont(self.titleFontB)
        self.OFFTitle.setAlignment(Qt.AlignHCenter)
        self.OFFLayout.addWidget(self.OFFTitle)

        # OFF button
        self.OFFButton = QPushButton("OFF")
        self.OFFButton.pressed.connect(self.heater_off)
        self.OFFButton.setFont(self.valueFontB)
        self.OFFButton.setStyleSheet("background-color : red")
        self.OFFLayout.addWidget(self.OFFButton)
        self.OFFLayout.addItem(self.verticalSpacer)
        #self.outerLayout.addLayout(self.OFFLayout, 6, 1)

        self.OFFWithQueueLayout = QVBoxLayout()

        # OFF with queue title
        self.OFFWQTitle = QLabel("Turn the Heater Off (Adds to Queue)")
        self.OFFWQTitle.setFont(self.titleFontB)
        self.OFFWQTitle.setAlignment(Qt.AlignHCenter)
        #self.OFFWithQueueLayout.addWidget(self.OFFWQTitle)

        # OFF with queue button
        self.OFFWQButton = QPushButton("OFF")
        #self.OFFWQButton.pressed.connect()
        self.OFFWQButton.setFont(self.valueFontB)
        self.OFFWithQueueLayout.addWidget(self.OFFWQButton)
        self.OFFWithQueueLayout.addItem(self.verticalSpacer)
        #self.outerLayout.addLayout(self.OFFWithQueueLayout, 5, 1)

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
        #measured_values = self.parent.hardwareManager.data.iloc[-1]
        measured_values = self.parent.hardwareManager.buffer[-1]
        # measured temperature
        self.mtLabel.setText(str(measured_values['Sample T (K)']))
        # current target temperature
        self.mspLabel.setText(str(measured_values['Setpoint T (K)']))
        # heater power setting / range
        #self.mpsLabel.setText(self.measured_power_setting)
        # heater power percent of maximum
        self.plLabel.setText(str(measured_values['Heater Power (%)']))
        # PID values
        self.pidPLabel.setText(str(measured_values['ITC502_P (%)']))
        self.pidILabel.setText(str(measured_values['ITC502_I (min)']))
        self.pidDLabel.setText(str(measured_values['ITC502_D (min)']))
        # ramp rate
        #self.mrrLabel.setText(self.measured_ramp_rate)
        # heater status
        #self.mhsLabel.setText(self.heater_status)
        self.mcpLabel.setText(
            f"{measured_values['MC Pressure (mbar)']:.2e}")
        self.dlpLabel.setText(
            f"{measured_values['DL Pressure (mbar)']:.2e}")

    def set_target_temperature(self, target):
        self.tempController.set_temp(target)

    def heater_off(self):
        """
        Turns the heater off
        """
        
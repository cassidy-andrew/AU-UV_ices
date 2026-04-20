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

        # define fonts
        self.titleFontA = QFont("Arial", 12)
        self.valueFontA = QFont("Consolas", 12)

        # this is good for making the tab a little easier to read
        self.verticalSpacer = QSpacerItem(10, 10)   # x, y

        # where we hold all the smaller UI elements
        self.outerLayout = QVBoxLayout()
        self.activeLayout = QGridLayout()
        self.parameterLayout = QVBoxLayout()
        self.controlLayout = QGridLayout()
        self.outerLayout.addLayout(self.activeLayout)
        self.outerLayout.addLayout(self.parameterLayout)
        self.outerLayout.addLayout(self.controlLayout)

        # -----------------------------------------
        # Temperature
        # -----------------------------------------
        self.measuredTempLayout = QVBoxLayout()
        #self.measuredTempLayout.addItem(self.verticalSpacer)
        
        # measured temperature display title
        self.mtLabelTitle = QLabel("Sample Temperature (K)")
        self.mtLabelTitle.setFont(self.titleFontA)
        self.mtLabelTitle.setAlignment(Qt.AlignLeft)
        self.measuredTempLayout.addWidget(self.mtLabelTitle)

        # measured temperature display value
        self.measured_temperature = "No Signal Yet"
        self.mtLabel = QLabel(self.measured_temperature)
        self.mtLabel.setFont(self.valueFontA)
        self.mtLabel.setAlignment(Qt.AlignHCenter)
        self.measuredTempLayout.addWidget(self.mtLabel)
        
        self.measuredTempLayout.addItem(self.verticalSpacer)
        self.activeLayout.addLayout(self.measuredTempLayout, 0, 0)

        # -----------------------------------------
        # Current set point
        # -----------------------------------------
        self.measuredSetPointLayout = QVBoxLayout()
        
        # measured set point display title
        self.mspLabelTitle = QLabel("Setpoint Temperature (K)")
        self.mspLabelTitle.setFont(self.titleFontA)
        self.mspLabelTitle.setAlignment(Qt.AlignLeft)
        self.measuredSetPointLayout.addWidget(self.mspLabelTitle)

        # measured temperature display value
        self.measured_set_point = "No Signal Yet"
        self.mspLabel = QLabel(self.measured_temperature)
        self.mspLabel.setFont(self.valueFontA)
        self.mspLabel.setAlignment(Qt.AlignHCenter)
        self.measuredSetPointLayout.addWidget(self.mspLabel)
        
        self.measuredSetPointLayout.addItem(self.verticalSpacer)
        self.activeLayout.addLayout(self.measuredSetPointLayout, 0, 1)

        # -----------------------------------------
        # Power Level
        # -----------------------------------------
        self.powerLevelLayout = QVBoxLayout()

        # measured power level title
        self.plLabelTitle = QLabel("Power Level (%)")
        self.plLabelTitle.setFont(self.titleFontA)
        self.plLabelTitle.setAlignment(Qt.AlignLeft)
        self.powerLevelLayout.addWidget(self.plLabelTitle)

        # measured power level label
        self.measured_power_level = "No Signal Yet"
        self.plLabel = QLabel(self.measured_power_level)
        self.plLabel.setFont(self.valueFontA)
        self.plLabel.setAlignment(Qt.AlignHCenter)
        self.powerLevelLayout.addWidget(self.plLabel)
        
        self.powerLevelLayout.addItem(self.verticalSpacer)
        self.activeLayout.addLayout(self.powerLevelLayout, 1, 0)

        # -----------------------------------------
        # PID Values
        # -----------------------------------------
        self.pidPLayout = QVBoxLayout()
        # measured PID P title
        self.pidPLabelTitle = QLabel("Proportional Band (%)")
        self.pidPLabelTitle.setFont(self.titleFontA)
        self.pidPLabelTitle.setAlignment(Qt.AlignLeft)
        self.pidPLayout.addWidget(self.pidPLabelTitle)
        # measured PID P label
        self.measured_pidP = "No Signal Yet"
        self.pidPLabel = QLabel(self.measured_pidP)
        self.pidPLabel.setFont(self.valueFontA)
        self.pidPLabel.setAlignment(Qt.AlignHCenter)
        self.pidPLayout.addWidget(self.pidPLabel)
        # add it to the layout
        self.pidPLayout.addItem(self.verticalSpacer)
        self.activeLayout.addLayout(self.pidPLayout, 1, 1)

        self.pidILayout = QVBoxLayout()
        # measured PID I title
        self.pidILabelTitle = QLabel("Integral Action Time (min)")
        self.pidILabelTitle.setFont(self.titleFontA)
        self.pidILabelTitle.setAlignment(Qt.AlignLeft)
        self.pidILayout.addWidget(self.pidILabelTitle)
        # measured PID I label
        self.measured_pidI = "No Signal Yet"
        self.pidILabel = QLabel(self.measured_pidI)
        self.pidILabel.setFont(self.valueFontA)
        self.pidILabel.setAlignment(Qt.AlignHCenter)
        self.pidILayout.addWidget(self.pidILabel)
        # add it to the layout
        self.pidILayout.addItem(self.verticalSpacer)
        self.activeLayout.addLayout(self.pidILayout, 2, 0)

        self.pidDLayout = QVBoxLayout()
        # measured PID D title
        self.pidDLabelTitle = QLabel("Derivative Action Time (min)")
        self.pidDLabelTitle.setFont(self.titleFontA)
        self.pidDLabelTitle.setAlignment(Qt.AlignLeft)
        self.pidDLayout.addWidget(self.pidDLabelTitle)
        # measured PID D label
        self.measured_pidD = "No Signal Yet"
        self.pidDLabel = QLabel(self.measured_pidD)
        self.pidDLabel.setFont(self.valueFontA)
        self.pidDLabel.setAlignment(Qt.AlignHCenter)
        self.pidDLayout.addWidget(self.pidDLabel)
        # add it to the layout
        self.pidDLayout.addItem(self.verticalSpacer)
        self.activeLayout.addLayout(self.pidDLayout, 2, 1)

        # -----------------------------------------
        # Heater Status
        # -----------------------------------------
        self.measuredHeaterStatusLayout = QVBoxLayout()

        # measured heater status display title
        self.mhsLabelTitle = QLabel("Heater Status")
        self.mhsLabelTitle.setFont(self.titleFontA)
        self.mhsLabelTitle.setAlignment(Qt.AlignLeft)
        self.measuredHeaterStatusLayout.addWidget(self.mhsLabelTitle)

        # measured  heater status display value
        self.measured_heater_status = "No Signal Yet"
        self.mhsLabel = QLabel(self.measured_heater_status)
        self.mhsLabel.setFont(self.valueFontA)
        self.mhsLabel.setAlignment(Qt.AlignHCenter)
        self.measuredHeaterStatusLayout.addWidget(self.mhsLabel)
        
        self.measuredHeaterStatusLayout.addItem(self.verticalSpacer)
        self.activeLayout.addLayout(self.measuredHeaterStatusLayout, 3, 0)

        # ---------------------------------------------------------------------
        # Parameter Controls
        # ---------------------------------------------------------------------

        # Title to the scan parameter set area
        self.parameterTitle = QLabel("Sweep Parameters")
        self.parameterTitle.setFont(self.titleFontA)
        self.parameterTitle.setStyleSheet("color:blue")
        self.parameterTitle.setAlignment(Qt.AlignLeft)
        self.parameterLayout.addWidget(self.parameterTitle)

        # this holds the parameter setting fields
        #self.parameterGridLayout = QGridLayout()
        #self.parameterLayout.addLayout(self.parameterGridLayout)

        # -----------------------------------------
        # Set target temperature
        # -----------------------------------------

        self.targetTempLayout = QHBoxLayout()
        self.targetTempLayout.addItem(self.verticalSpacer)
        # target temperature display title
        self.targetTitle = QLabel("Set Target Temperature (K)")
        self.targetTitle.setFont(self.titleFontA)
        self.targetTitle.setAlignment(Qt.AlignVCenter)
        self.targetTempLayout.addWidget(self.targetTitle)

        # target temperature display value
        self.target_temperature = 273
        self.tempLineEdit = QDoubleSpinBox()
        self.tempLineEdit.setRange(0.0, 273.0)
        self.tempLineEdit.setDecimals(1)
        self.tempLineEdit.setSingleStep(1)
        self.tempLineEdit.setFont(self.valueFontA)
        self.tempLineEdit.setValue(self.target_temperature)
        self.tempLineEdit.setAlignment(Qt.AlignHCenter)
        self.targetTempLayout.addWidget(self.tempLineEdit)
        
        self.targetTempLayout.addItem(self.verticalSpacer)
        self.parameterLayout.addLayout(self.targetTempLayout)

        # -----------------------------------------
        # Set Power level
        # -----------------------------------------

        self.targetPowerLayout = QHBoxLayout()
        self.targetPowerLayout.addItem(self.verticalSpacer)
        # target temperature display title
        self.targetPowerTitle = QLabel("Set Power Level (%)")
        self.targetPowerTitle.setFont(self.titleFontA)
        self.targetPowerTitle.setAlignment(Qt.AlignVCenter)
        self.targetPowerLayout.addWidget(self.targetPowerTitle)

        # target temperature display value
        self.target_Power = 100
        self.powerLineEdit = QDoubleSpinBox()
        self.powerLineEdit.setRange(0, 100)
        self.powerLineEdit.setDecimals(0)
        self.powerLineEdit.setSingleStep(1)
        self.powerLineEdit.setFont(self.valueFontA)
        self.powerLineEdit.setValue(self.target_Power)
        self.powerLineEdit.setAlignment(Qt.AlignHCenter)
        self.targetPowerLayout.addWidget(self.powerLineEdit)
        
        self.targetPowerLayout.addItem(self.verticalSpacer)
        #self.parameterLayout.addLayout(self.targetPowerLayout)

        # -----------------------------------------
        # Set P
        # -----------------------------------------

        self.targetPLayout = QHBoxLayout()
        self.targetPLayout.addItem(self.verticalSpacer)
        # target temperature display title
        self.targetPTitle = QLabel("Set Proportional Band (%)")
        self.targetPTitle.setFont(self.titleFontA)
        self.targetPTitle.setAlignment(Qt.AlignVCenter)
        self.targetPLayout.addWidget(self.targetPTitle)

        # target temperature display value
        self.target_P = 30.0
        self.pLineEdit = QDoubleSpinBox()
        self.pLineEdit.setRange(0.0, 199.9)
        self.pLineEdit.setDecimals(1)
        self.pLineEdit.setSingleStep(1)
        self.pLineEdit.setFont(self.valueFontA)
        self.pLineEdit.setValue(self.target_P)
        self.pLineEdit.setAlignment(Qt.AlignHCenter)
        self.targetPLayout.addWidget(self.pLineEdit)
        
        self.targetPLayout.addItem(self.verticalSpacer)
        self.parameterLayout.addLayout(self.targetPLayout)

        # -----------------------------------------
        # Set I
        # -----------------------------------------

        self.targetILayout = QHBoxLayout()
        self.targetILayout.addItem(self.verticalSpacer)
        self.targetITitle = QLabel("Set Integral Action Time (min)")
        self.targetITitle.setFont(self.titleFontA)
        self.targetITitle.setAlignment(Qt.AlignVCenter)
        self.targetILayout.addWidget(self.targetITitle)

        self.target_I = 2.0
        self.iLineEdit = QDoubleSpinBox()
        self.iLineEdit.setRange(0.0, 140.0)
        self.iLineEdit.setDecimals(1)
        self.iLineEdit.setSingleStep(1)
        self.iLineEdit.setFont(self.valueFontA)
        self.iLineEdit.setValue(self.target_I)
        self.iLineEdit.setAlignment(Qt.AlignHCenter)
        self.targetILayout.addWidget(self.iLineEdit)
        
        self.targetILayout.addItem(self.verticalSpacer)
        self.parameterLayout.addLayout(self.targetILayout)

        # -----------------------------------------
        # Set D
        # -----------------------------------------

        self.targetDLayout = QHBoxLayout()
        self.targetDLayout.addItem(self.verticalSpacer)
        self.targetDTitle = QLabel("Set Derivative Action Time (min)")
        self.targetDTitle.setFont(self.titleFontA)
        self.targetDTitle.setAlignment(Qt.AlignVCenter)
        self.targetDLayout.addWidget(self.targetDTitle)

        self.target_D = 0.0
        self.dLineEdit = QDoubleSpinBox()
        self.dLineEdit.setRange(0.0, 273.0)
        self.dLineEdit.setDecimals(1)
        self.dLineEdit.setSingleStep(1)
        self.dLineEdit.setFont(self.valueFontA)
        self.dLineEdit.setValue(self.target_D)
        self.dLineEdit.setAlignment(Qt.AlignHCenter)
        self.targetDLayout.addWidget(self.dLineEdit)
        
        self.targetDLayout.addItem(self.verticalSpacer)
        self.parameterLayout.addLayout(self.targetDLayout)

        # -----------------------------------------
        # Sweep description
        # -----------------------------------------
        self.sdLayout = QVBoxLayout()
        self.sdLayout.addItem(self.verticalSpacer)
        self.sdTitle = QLabel("Sweep Description / Comments")
        self.sdTitle.setFont(self.titleFontA)
        self.sdTitle.setStyleSheet("color:blue")
        self.sdTitle.setAlignment(Qt.AlignLeft)
        self.sdLayout.addWidget(self.sdTitle)
        self.sdTextEdit = QTextEdit()
        #self.sdTextEdit.setMaximumHeight(100)
        self.sdLayout.addWidget(self.sdTextEdit)
        self.sdLayout.addItem(self.verticalSpacer)
        self.parameterLayout.addLayout(self.sdLayout)

        # -----------------------------------------
        # Start the sweep button
        # -----------------------------------------
        # define a layout for the elements
        self.startSweepLayout = QVBoxLayout()
        #self.startSweepLayout.addItem(self.verticalSpacer)
        # make the button
        self.startSweepBtn = QPushButton("Queue Sweep")
        self.startSweepBtn.pressed.connect(self.add_to_queue)
        self.startSweepBtn.setFont(self.titleFontA)
        self.startSweepLayout.addWidget(self.startSweepBtn)
        # add it to the layout
        self.controlLayout.addLayout(self.startSweepLayout, 0, 0)
        

        # -----------------------------------------
        # OFF button
        # -----------------------------------------
        self.OFFLayout = QVBoxLayout()

        # OFF title
        self.OFFTitle = QLabel("Turn the Heater Off (Skips Queue)")
        self.OFFTitle.setFont(self.titleFontA)
        self.OFFTitle.setAlignment(Qt.AlignHCenter)
        #self.OFFLayout.addWidget(self.OFFTitle)

        # OFF button
        self.OFFButton = QPushButton("Heater STOP (skips queue!)")
        self.OFFButton.pressed.connect(self.heater_off)
        self.OFFButton.setFont(self.titleFontA)
        self.OFFButton.setStyleSheet("background-color : red")
        self.OFFLayout.addWidget(self.OFFButton)
        self.OFFLayout.addItem(self.verticalSpacer)
        self.outerLayout.addItem(self.verticalSpacer)
        self.outerLayout.addItem(self.verticalSpacer)
        self.outerLayout.addItem(self.verticalSpacer)
        self.outerLayout.addItem(self.verticalSpacer)
        self.outerLayout.addLayout(self.OFFLayout)

        self.OFFWithQueueLayout = QVBoxLayout()

        # OFF with queue title
        self.OFFWQTitle = QLabel("Turn the Heater Off (Adds to Queue)")
        self.OFFWQTitle.setFont(self.titleFontA)
        self.OFFWQTitle.setAlignment(Qt.AlignHCenter)
        #self.OFFWithQueueLayout.addWidget(self.OFFWQTitle)

        # OFF with queue button
        self.OFFWQButton = QPushButton("OFF")
        #self.OFFWQButton.pressed.connect()
        self.OFFWQButton.setFont(self.valueFontA)
        self.OFFWithQueueLayout.addWidget(self.OFFWQButton)
        self.OFFWithQueueLayout.addItem(self.verticalSpacer)
        #self.activeLayout.addLayout(self.OFFWithQueueLayout, 3, 1)

        # -----------------------------------------
        # Configuration & Logistics
        # -----------------------------------------

        # this helps formatting the rows so they stay at the top of the tab
        self.activeLayout.setRowStretch(self.activeLayout.rowCount(), 1)

        # configure update timer to refresh the data
        self.parent.hardwareManager.add_refresh_function(
            self.refresh_controller
        )

    def refresh_controller(self):
        """
        Update all values from the Hardware Manager / temperature controller
        """
        #measured_values = self.parent.hardwareManager.data.iloc[-1]
        #measured_values = self.parent.hardwareManager.buffer[-1]
        measured_values = {}
        for key in self.parent.hardwareManager.buffer:
            measured_values[key] = self.parent.hardwareManager.buffer[key][-1]
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

    def heater_off(self):
        """
        Turns the heater off
        """

    def add_to_queue():
        """
        Adds the sweep instruction to the queue
        """
        instruction = {
            'type':'heater',
            'params':{
                'setpoint':self.tempLineEdit.value(),
                'P':self.pLineEdit.value(),
                'I':self.iLineEdit.value(),
                'D':self.dLineEdit.value(),
                'comment':self.sdTextEdit
            }
        }
        
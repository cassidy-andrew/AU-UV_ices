import sys
import os
import inspect
import json
import numpy as np

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

class AcquisitionTab():
    def __init__(self, parent, debug):
        """
        A tab for annealing stuff with!
        """
        self.parent = parent
        self.debug = debug
        self.mainWindow = self.parent.parentWindow

        # are we currently scanning? This parameter holds that information
        self.scan_state = False

        #self.scan_config = self.parent.hardwareManager.scan_config
        self.scan_config = {
            "wl_start":110,
            "wl_end":220,
            "wl_step":1.0,
            "n_scans":1,
            "n_points":111,
            "n_avg":15,
            "t_avg":np.nan,
            "t_bllock":np.nan,
            "UnduPos_start":np.nan,
            "UnduPos_end":np.nan,
            "Table_Pos":np.nan,
            "Grating":np.nan,
            "Comments":"",
            "Sample":"",
            "EXS_rPos":np.nan,
            "ENS_rPos":np.nan,
            "PMTVac":np.nan
        }

        # define fonts
        self.titleFontA = QFont("Arial", 12)
        self.valueFontA = QFont("Consolas", 12)

        # where we hold all the smaller UI elements
        self.outerLayout = QVBoxLayout()
        self.activeLayout = QGridLayout()
        self.parameterLayout = QVBoxLayout()
        self.statusLayout = QVBoxLayout()
        self.controlLayout = QGridLayout()
        self.outerLayout.addLayout(self.activeLayout)
        self.outerLayout.addLayout(self.parameterLayout)
        #self.outerLayout.addLayout(self.statusLayout)
        self.outerLayout.addLayout(self.controlLayout)

        # this is good for making the tab a little easier to read
        self.verticalSpacer = QSpacerItem(10, 10)   # x, y
        self.verticalSpacerS = QSpacerItem(5, 5)   # x, y

        # --------------------------------------------------------------------
        # Active parameter displays
        # --------------------------------------------------------------------

        # -----------------------------------------
        # The current wavelength position
        # -----------------------------------------

        self.measuredWavelengthLayout = QVBoxLayout()
        #self.measuredWavelengthLayout.addItem(self.verticalSpacer)

        self.mwlLabelTitle = QLabel("AU-UV Wavelength (nm)")
        self.mwlLabelTitle.setFont(self.titleFontA)
        self.mwlLabelTitle.setAlignment(Qt.AlignLeft)
        self.measuredWavelengthLayout.addWidget(self.mwlLabelTitle)

        self.measured_wavelength = "No Signal Yet"
        self.mwlLabel = QLabel(self.measured_wavelength)
        self.mwlLabel.setFont(self.valueFontA)
        self.mwlLabel.setAlignment(Qt.AlignHCenter)
        self.measuredWavelengthLayout.addWidget(self.mwlLabel)

        self.measuredWavelengthLayout.addItem(self.verticalSpacer)
        self.activeLayout.addLayout(self.measuredWavelengthLayout, 0, 0)

        # -----------------------------------------
        # The measured average per reading (mapr)
        # -----------------------------------------

        """self.maprLayout = QVBoxLayout()
        self.maprLayout.addItem(self.verticalSpacer)

        self.maprLabelTitle = QLabel("Average per reading")
        self.maprLabelTitle.setFont(self.titleFontA)
        self.maprLabelTitle.setAlignment(Qt.AlignLeft)
        self.maprLayout.addWidget(self.maprLabelTitle)

        self.mapr = "No Signal Yet"
        self.maprLabel = QLabel(self.mapr)
        self.maprLabel.setFont(self.valueFontA)
        self.maprLabel.setAlignment(Qt.AlignHCenter)
        self.maprLayout.addWidget(self.maprLabel)

        self.maprLayout.addItem(self.verticalSpacer)
        self.activeLayout.addLayout(self.maprLayout, 0, 1)"""

        # Measured Table position
        self.mtpLayout = QVBoxLayout()
        #self.mtpLayout.addItem(self.verticalSpacerS)
        self.mtpLabelTitle = QLabel("Table Position (kstep)")
        self.mtpLabelTitle.setFont(self.titleFontA)
        self.mtpLabelTitle.setAlignment(Qt.AlignLeft)
        self.mtpLayout.addWidget(self.mtpLabelTitle)
        self.mtp = "No Signal Yet"
        self.mtpLabel = QLabel(self.mtp)
        self.mtpLabel.setFont(self.valueFontA)
        self.mtpLabel.setAlignment(Qt.AlignHCenter)
        self.mtpLayout.addWidget(self.mtpLabel)
        self.mtpLayout.addItem(self.verticalSpacerS)
        self.activeLayout.addLayout(self.mtpLayout, 0, 1)

        # -----------------------------------------
        # The individual channel readings (mch1, mch2, etc.)
        # -----------------------------------------

        # Channel 0
        self.mch0Layout = QVBoxLayout()
        self.mch0Layout.addItem(self.verticalSpacer)
        self.mch0LabelTitle = QLabel("Ch0 Signal (V)")
        self.mch0LabelTitle.setFont(self.titleFontA)
        self.mch0LabelTitle.setAlignment(Qt.AlignLeft)
        self.mch0Layout.addWidget(self.mch0LabelTitle)
        self.mch0 = "No Signal Yet"
        self.mch0Label = QLabel(self.mch0)
        self.mch0Label.setFont(self.valueFontA)
        self.mch0Label.setAlignment(Qt.AlignHCenter)
        self.mch0Layout.addWidget(self.mch0Label)
        self.mch0Layout.addItem(self.verticalSpacerS)
        self.activeLayout.addLayout(self.mch0Layout, 1, 0)

        # Channel 1
        self.mch1Layout = QVBoxLayout()
        self.mch1Layout.addItem(self.verticalSpacer)
        self.mch1LabelTitle = QLabel("Ch1 Signal (V)")
        self.mch1LabelTitle.setFont(self.titleFontA)
        self.mch1LabelTitle.setAlignment(Qt.AlignLeft)
        self.mch1Layout.addWidget(self.mch1LabelTitle)
        self.mch1 = "No Signal Yet"
        self.mch1Label = QLabel(self.mch1)
        self.mch1Label.setFont(self.valueFontA)
        self.mch1Label.setAlignment(Qt.AlignHCenter)
        self.mch1Layout.addWidget(self.mch1Label)
        self.mch1Layout.addItem(self.verticalSpacerS)
        self.activeLayout.addLayout(self.mch1Layout, 1, 1)

        # Channel 2
        self.mch2Layout = QVBoxLayout()
        self.mch2Layout.addItem(self.verticalSpacerS)
        self.mch2LabelTitle = QLabel("Ch2 Signal (V)")
        self.mch2LabelTitle.setFont(self.titleFontA)
        self.mch2LabelTitle.setAlignment(Qt.AlignLeft)
        self.mch2Layout.addWidget(self.mch2LabelTitle)
        self.mch2 = "No Signal Yet"
        self.mch2Label = QLabel(self.mch2)
        self.mch2Label.setFont(self.valueFontA)
        self.mch2Label.setAlignment(Qt.AlignHCenter)
        self.mch2Layout.addWidget(self.mch2Label)
        self.mch2Layout.addItem(self.verticalSpacerS)
        self.activeLayout.addLayout(self.mch2Layout, 2, 0)

        # Channel 3
        self.mch3Layout = QVBoxLayout()
        self.mch3Layout.addItem(self.verticalSpacerS)
        self.mch3LabelTitle = QLabel("Ch3 Signal (V)")
        self.mch3LabelTitle.setFont(self.titleFontA)
        self.mch3LabelTitle.setAlignment(Qt.AlignLeft)
        self.mch3Layout.addWidget(self.mch3LabelTitle)
        self.mch3 = "No Signal Yet"
        self.mch3Label = QLabel(self.mch3)
        self.mch3Label.setFont(self.valueFontA)
        self.mch3Label.setAlignment(Qt.AlignHCenter)
        self.mch3Layout.addWidget(self.mch3Label)
        self.mch3Layout.addItem(self.verticalSpacerS)
        self.activeLayout.addLayout(self.mch3Layout, 2, 1)


        # --------------------------------------------------------------------
        # Parameter controls
        # --------------------------------------------------------------------

        # Title to the scan parameter set area
        self.parameterTitle = QLabel("Scan Parameters")
        self.parameterTitle.setFont(self.titleFontA)
        self.parameterTitle.setStyleSheet("color:blue")
        self.parameterTitle.setAlignment(Qt.AlignLeft)
        self.parameterLayout.addWidget(self.parameterTitle)

        # this holds the parameter setting fields
        self.parameterGridLayout = QGridLayout()
        self.parameterLayout.addLayout(self.parameterGridLayout)

        # start wavelength
        self.swlLayout = QVBoxLayout()
        self.swlLayout.addItem(self.verticalSpacerS)
        self.swlTitle = QLabel("Start Wavelength (nm)")
        self.swlTitle.setFont(self.titleFontA)
        self.swlTitle.setAlignment(Qt.AlignLeft)
        self.swlLayout.addWidget(self.swlTitle)
        self.swlBox = QDoubleSpinBox()
        self.swlBox.setRange(100, 700)
        self.swlBox.setDecimals(0)
        self.swlBox.setSingleStep(1.0)
        self.swlBox.setValue(self.scan_config['wl_start'])
        self.swlBox.valueChanged.connect(
            lambda: self._update_start_wavelength(self.swlBox.value())
        )
        self.swlLayout.addWidget(self.swlBox)
        self.swlLayout.addItem(self.verticalSpacerS)
        self.parameterGridLayout.addLayout(self.swlLayout, 0, 0)

        # end wavelength
        self.ewlLayout = QVBoxLayout()
        self.ewlLayout.addItem(self.verticalSpacerS)
        self.ewlTitle = QLabel("End Wavelength (nm)")
        self.ewlTitle.setFont(self.titleFontA)
        self.ewlTitle.setAlignment(Qt.AlignLeft)
        self.ewlLayout.addWidget(self.ewlTitle)
        self.ewlBox = QDoubleSpinBox()
        self.ewlBox.setRange(100, 700)
        self.ewlBox.setDecimals(0)
        self.ewlBox.setSingleStep(1.0)
        self.ewlBox.setValue(self.scan_config['wl_end'])
        self.ewlBox.valueChanged.connect(
            lambda: self._update_end_wavelength(self.ewlBox.value())
        )
        self.ewlLayout.addWidget(self.ewlBox)
        self.ewlLayout.addItem(self.verticalSpacerS)
        self.parameterGridLayout.addLayout(self.ewlLayout, 0, 1)

        # wavelength step
        self.wlsLayout = QVBoxLayout()
        self.wlsLayout.addItem(self.verticalSpacerS)
        self.wlsTitle = QLabel("Wavelength Step (nm)")
        self.wlsTitle.setFont(self.titleFontA)
        self.wlsTitle.setAlignment(Qt.AlignLeft)
        self.wlsLayout.addWidget(self.wlsTitle)
        self.wlsBox = QDoubleSpinBox()
        self.wlsBox.setRange(0.1, 5)
        self.wlsBox.setDecimals(1)
        self.wlsBox.setSingleStep(0.1)
        self.wlsBox.setValue(self.scan_config['wl_step'])
        self.wlsBox.valueChanged.connect(
            lambda: self._update_wavelength_step(self.wlsBox.value())
        )
        self.wlsLayout.addWidget(self.wlsBox)
        self.wlsLayout.addItem(self.verticalSpacerS)
        self.parameterGridLayout.addLayout(self.wlsLayout, 1, 0)

        # number of data points
        self.ndpLayout = QVBoxLayout()
        self.ndpLayout.addItem(self.verticalSpacerS)
        self.ndpLabelTitle = QLabel("# Data Points")
        self.ndpLabelTitle.setFont(self.titleFontA)
        self.ndpLabelTitle.setAlignment(Qt.AlignLeft)
        self.ndpLayout.addWidget(self.ndpLabelTitle)
        self.ndpLabel = QLabel("None")
        self.ndpLabel.setFont(self.valueFontA)
        self.ndpLabel.setAlignment(Qt.AlignHCenter)
        self.ndpLayout.addWidget(self.ndpLabel)
        self.ndpLayout.addItem(self.verticalSpacerS)
        self.parameterGridLayout.addLayout(self.ndpLayout, 1, 1)

        # average per reading
        self.aprLayout = QVBoxLayout()
        self.aprLayout.addItem(self.verticalSpacerS)
        self.aprTitle = QLabel("Average Per Reading")
        self.aprTitle.setFont(self.titleFontA)
        self.aprTitle.setAlignment(Qt.AlignLeft)
        self.aprLayout.addWidget(self.aprTitle)
        self.aprBox = QDoubleSpinBox()
        self.aprBox.setRange(1, 100)
        self.aprBox.setDecimals(0)
        self.aprBox.setSingleStep(1)
        self.aprBox.setValue(self.scan_config['n_avg'])
        self.aprBox.valueChanged.connect(
            lambda: self._update_n_avg(self.aprBox.value())
        )
        self.aprLayout.addWidget(self.aprBox)
        self.aprLayout.addItem(self.verticalSpacerS)
        self.parameterGridLayout.addLayout(self.aprLayout, 2, 0)

        # time per reading
        self.tprLayout = QVBoxLayout()
        self.tprLayout.addItem(self.verticalSpacerS)
        self.tprLabelTitle = QLabel("Time Per Reading (sec)")
        self.tprLabelTitle.setFont(self.titleFontA)
        self.tprLabelTitle.setAlignment(Qt.AlignLeft)
        self.tprLayout.addWidget(self.tprLabelTitle)
        self.tprLabel = QLabel("None")
        self.tprLabel.setFont(self.valueFontA)
        self.tprLabel.setAlignment(Qt.AlignHCenter)
        self.tprLayout.addWidget(self.tprLabel)
        self.tprLayout.addItem(self.verticalSpacerS)
        self.parameterGridLayout.addLayout(self.tprLayout, 2, 1)

        # number of scans
        self.nsLayout = QVBoxLayout()
        self.nsLayout.addItem(self.verticalSpacerS)
        self.nsTitle = QLabel("# Scans")
        self.nsTitle.setFont(self.titleFontA)
        self.nsTitle.setAlignment(Qt.AlignLeft)
        self.nsLayout.addWidget(self.nsTitle)
        self.nsBox = QDoubleSpinBox()
        self.nsBox.setRange(1, 100)
        self.nsBox.setDecimals(0)
        self.nsBox.setSingleStep(1)
        self.nsBox.setValue(self.scan_config['n_scans'])
        self.nsBox.valueChanged.connect(
            lambda: self._update_n_scans(self.nsBox.value())
        )
        self.nsLayout.addWidget(self.nsBox)
        self.nsLayout.addItem(self.verticalSpacerS)
        self.parameterGridLayout.addLayout(self.nsLayout, 3, 0)

        # estimated time
        self.etLayout = QVBoxLayout()
        self.etLayout.addItem(self.verticalSpacerS)
        self.etLabelTitle = QLabel("Estimated Time")
        self.etLabelTitle.setFont(self.titleFontA)
        self.etLabelTitle.setAlignment(Qt.AlignLeft)
        self.etLayout.addWidget(self.etLabelTitle)
        self.etLabel = QLabel("None")
        self.etLabel.setFont(self.valueFontA)
        self.etLabel.setAlignment(Qt.AlignHCenter)
        self.etLayout.addWidget(self.etLabel)
        self.etLayout.addItem(self.verticalSpacerS)
        self.parameterGridLayout.addLayout(self.etLayout, 3, 1)

        # set the table position
        self.setTableVLayout = QVBoxLayout()
        self.setTableTitle = QLabel("Configure Table Position")
        self.setTableTitle.setFont(self.titleFontA)
        #self.setTableTitle.setStyleSheet("color:blue")
        self.setTableVLayout.addWidget(self.setTableTitle)
        self.setTableParamLayout = QHBoxLayout()
        self.STAcheckmark = QCheckBox("Auto")
        self.setTableParamLayout.addWidget(self.STAcheckmark)
        self.STComboBox = QComboBox()
        self.STComboBox.addItem("-500 kstp")
        self.STComboBox.addItem("-450 kstp")
        self.STComboBox.addItem("-300 kstp")
        self.STComboBox.addItem("-100 kstp")
        self.STComboBox.addItem("   0 kstp")
        self.STComboBox.addItem(" 125 kstp")
        self.STComboBox.addItem(" 250 kstp")
        self.STComboBox.addItem(" 400 kstp")
        self.STComboBox.addItem(" 650 kstp")
        self.setTableParamLayout.addWidget(self.STComboBox)
        self.STAcheckmark.stateChanged.connect(self.auto_table_position)
        self.setTableVLayout.addLayout(self.setTableParamLayout)
        self.parameterLayout.addLayout(self.setTableVLayout)

        # set the grating
        self.setGratingVLayout = QVBoxLayout()
        self.setGratingTitle = QLabel("Configure High/Low Energy Grating")
        self.setGratingTitle.setFont(self.titleFontA)
        #self.setGratingTitle.setStyleSheet("color:blue")
        self.setGratingVLayout.addWidget(self.setGratingTitle)
        self.setGratingParamLayout = QHBoxLayout()
        self.SGcheckmark = QCheckBox("Auto")
        #self.setGratingParamLayout.addWidget(self.SGcheckmark)
        self.SGComboBox = QComboBox()
        self.SGComboBox.addItem("Low Energy (HEG)")
        self.SGComboBox.addItem("High Energy (LEG)")
        self.setGratingParamLayout.addWidget(self.SGComboBox)
        self.SGcheckmark.stateChanged.connect(self.auto_grating)
        self.setGratingVLayout.addLayout(self.setGratingParamLayout)
        self.parameterLayout.addLayout(self.setGratingVLayout)

        # set the PMT Vac
        self.setPMTVacVLayout = QVBoxLayout()
        self.setPMTVacTitle = QLabel("Set Detector Air Filter")
        self.setPMTVacTitle.setFont(self.titleFontA)
        #self.setPMTVacTitle.setStyleSheet("color:blue")
        self.setPMTVacVLayout.addWidget(self.setPMTVacTitle)
        self.setPMTVacParamLayout = QHBoxLayout()
        self.SPMTcheckmark = QCheckBox("Auto")
        self.setPMTVacParamLayout.addWidget(self.SPMTcheckmark)
        self.SPMTComboBox = QComboBox()
        self.SPMTComboBox.addItem("ON")
        self.SPMTComboBox.addItem("OFF")
        self.setPMTVacParamLayout.addWidget(self.SPMTComboBox)
        self.SPMTcheckmark.stateChanged.connect(self.auto_grating)
        self.setPMTVacVLayout.addLayout(self.setPMTVacParamLayout)
        self.parameterLayout.addLayout(self.setPMTVacVLayout)

        # sample description
        self.sdLayout = QVBoxLayout()
        self.sdLayout.addItem(self.verticalSpacerS)
        self.sdTitle = QLabel("Sample Description / Comments")
        self.sdTitle.setFont(self.titleFontA)
        self.sdTitle.setStyleSheet("color:blue")
        self.sdTitle.setAlignment(Qt.AlignLeft)
        self.sdLayout.addWidget(self.sdTitle)
        self.sdTextEdit = QTextEdit()
        self.sdLayout.addWidget(self.sdTextEdit)
        self.sdLayout.addItem(self.verticalSpacerS)
        self.parameterLayout.addLayout(self.sdLayout)

        # -----------------------------------------
        # Start the scan button
        # -----------------------------------------
        # define a layout for the elements
        self.startScanLayout = QVBoxLayout()
        self.startScanLayout.addItem(self.verticalSpacer)
        # make the button
        self.startScanBtn = QPushButton("Queue Scan")
        self.startScanBtn.pressed.connect(self.add_to_queue)
        self.startScanBtn.setFont(self.titleFontA)
        self.startScanLayout.addWidget(self.startScanBtn)
        # add it to the layout
        self.controlLayout.addLayout(self.startScanLayout, 0, 0)

        # ---------------------------------------------------------------------
        # Configuration & Logistics
        # ---------------------------------------------------------------------

        # this helps formatting the rows so they stay at the top of the tab
        #self.outerLayout.setRowStretch(self.outerLayout.rowCount(), 1)
        self.activeLayout.setRowStretch(self.activeLayout.rowCount(), 1)
        self.parameterGridLayout.setRowStretch(self.parameterGridLayout.rowCount(), 1)
        self.controlLayout.setRowStretch(self.controlLayout.rowCount(), 1)

        # configure update timer to refresh the data
        self.parent.hardwareManager.add_refresh_function(
            self.refresh_controller
        )

    def update_statusLabel(self, event):
        self.statusLabel.setText(event[10:])

    def _update_start_wavelength(self, value):
        self.scan_config['wl_start'] = value

    def _update_end_wavelength(self, value):
        self.scan_config['wl_end'] = value

    def _update_wavelength_step(self, value):
        self.scan_config['wl_step'] = value

    def _update_n_avg(self, value):
        self.scan_config['n_avg'] = value

    def _update_n_scans(self, value):
        self.scan_config['n_scans'] = value
        

    def end_scan(self, abort=False, auto=True, user=False):
        """
        Ends a scan cleanly

        abort : (bool) Are we stopping because of an error?
        """
        if abort == True:
            verb = "Aborting"
        else:
            verb = "Stopping"
        if user == True:
            subject = "the user"
        else:
            subject = "DUVET"
        message = f"{verb} scan by {subject}"
        self.mainWindow.log(message)
        

        self.scan_state = False
        return None

    def start_scan(self):
        """
        Starts a scan
        """
        wli = self.scan_config['wl_start']
        wlf = self.scan_config['wl_end']
        self.mainWindow.log(f"Starting scan from {wli} to {wlf} nm")
        self.scan_state = True

        return None

    def refresh_controller(self):
        """
        Update all values from the Hardware Manager / ConSys
        """

        return None

    def add_to_queue(self):
        """
        Add a spectrum acquisition to the queue based on the current parameters
        """
        # check the auto parameter determination functions
        self.refresh_auto_parameters()

    def refresh_auto_parameters(self):
        """
        Re-calculate all things set to automatically recalculate
        """
        self.auto_table_position()

    def auto_grating():
        """
        Automatically determine the grating
        """
        return None

    def auto_PMT_Vac():
        """
        Automatically determine if vacuum is needed in front of the PMT
        """
        wl_start = self.swlBox.value()

        if wl_start > 210:
            # we should have vacuum
            return True

    def auto_table_position(self):
        """
        Automatically determine the table position
        """
        # understand the state of the check box
        if not self.STAcheckmark.isChecked():
            # we want to set the table position freely
            self.STComboBox.setEnabled(True)
            return None

        # otherwise, determine the correct table position for the settings above
        #
        # Recommended for CD
        # 160-340 nm    0 kstp       i = 4
        # 
        # Medium resolution
        # 110-210 nm    -500 kstp    i = 0
        # 200-260 nm    -100 kstp    i = 3
        # 250-310 nm     250 kstp    i = 6
        #
        # High resolution
        # 115-150 nm    -450 kstp    i = 1
        # 150-185 nm    -300 kstp    i = 2
        # 185-220 nm    -100 kstp    i = 3
        # 220-255 nm     125 kstp    i = 5
        # 255-290 nm     400 kstp    i = 7
        # 290-325 nm     650 kstp    i = 8

        res = self.wlsBox.value()
        wl_start = self.swlBox.value()
        wl_end = self.ewlBox.value()

        # are we using high resolution?
        if res < 1:
            if wl_end < 150:
                self.STComboBox.setCurrentIndex(1)
            elif wl_end < 185:
                self.STComboBox.setCurrentIndex(2)
            elif wl_end < 220:
                self.STComboBox.setCurrentIndex(3)
            elif wl_end < 255:
                self.STComboBox.setCurrentIndex(5)
            elif wl_end < 290:
                self.STComboBox.setCurrentIndex(7)
            else:
                self.STComboBox.setCurrentIndex(8)
        else:
            if wl_end < 210:
                self.STComboBox.setCurrentIndex(0)
            elif wl_end < 260:
                self.STComboBox.setCurrentIndex(3)
            elif wl_end < 310:
                self.STComboBox.setCurrentIndex(6)

        # lock the drop down from user editing, since "auto" has been checked
        self.STComboBox.setEnabled(False)

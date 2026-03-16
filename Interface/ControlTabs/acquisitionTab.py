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

        # Note! this is done referentially, so changes automatically apply!
        self.scan_config = self.parent.hardwareManager.scan_config

        # define fonts
        self.titleFontA = QFont("Arial", 11)
        self.valueFontA = QFont("Consolas", 11)

        # where we hold all the smaller UI elements
        self.outerLayout = QVBoxLayout()
        self.activeLayout = QGridLayout()
        self.statusLayout = QVBoxLayout()
        self.controlLayout = QGridLayout()
        self.outerLayout.addLayout(self.activeLayout)
        self.outerLayout.addLayout(self.statusLayout)
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
        self.measuredWavelengthLayout.addItem(self.verticalSpacer)

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

        self.maprLayout = QVBoxLayout()
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
        self.activeLayout.addLayout(self.maprLayout, 0, 1)

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

        # ---------------------------------------------------------------------
        # The status
        # ---------------------------------------------------------------------

        self.statusLayout.addItem(self.verticalSpacer)

        self.statusLabelTitle = QLabel("Status")
        self.statusLabelTitle.setFont(self.titleFontA)
        self.statusLabelTitle.setAlignment(Qt.AlignLeft)
        self.statusLayout.addWidget(self.statusLabelTitle)

        self.statusLabel = QLabel("")
        self.statusLabel.setFont(self.valueFontA)
        self.statusLabel.setAlignment(Qt.AlignLeft)
        self.statusLayout.addWidget(self.statusLabel)

        self.mainWindow.eventLog.item_added.connect(self.update_statusLabel)

        self.statusLayout.addItem(self.verticalSpacer)

        # --------------------------------------------------------------------
        # Parameter controls
        # --------------------------------------------------------------------

        # -----------------------------------------
        # Start the scan button
        # -----------------------------------------
        # define a layout for the elements
        self.startScanLayout = QVBoxLayout()
        self.startScanLayout.addItem(self.verticalSpacer)
        # make the button
        self.startScanBtn = QPushButton("Start Scan")
        self.startScanBtn.pressed.connect(self.start_scan)
        self.startScanBtn.setFont(self.titleFontA)
        self.startScanLayout.addWidget(self.startScanBtn)
        # add it to the layout
        self.controlLayout.addLayout(self.startScanLayout, 0, 0)

        # -----------------------------------------
        # Abort the scan button
        # -----------------------------------------
        # define a layout for the elements
        self.abortScanLayout = QVBoxLayout()
        self.abortScanLayout.addItem(self.verticalSpacer)
        # make the button
        self.abortScanBtn = QPushButton("Abort Scan")
        self.abortScanBtn.pressed.connect(
            lambda: self.end_scan(abort=True, user=True)
        )
        self.abortScanBtn.setFont(self.titleFontA)
        self.abortScanLayout.addWidget(self.abortScanBtn)
        # add it to the layout
        self.controlLayout.addLayout(self.abortScanLayout, 0, 1)


        # ---------------------------------------------------------------------
        # Configuration & Logistics
        # ---------------------------------------------------------------------

        # this helps formatting the rows so they stay at the top of the tab
        #self.outerLayout.setRowStretch(self.outerLayout.rowCount(), 1)
        self.activeLayout.setRowStretch(self.activeLayout.rowCount(), 1)
        self.controlLayout.setRowStretch(self.controlLayout.rowCount(), 1)

        # configure update timer to refresh the data
        self.parent.hardwareManager.add_refresh_function(
            self.refresh_controller
        )

    def update_statusLabel(self, event):
        self.statusLabel.setText(event[10:])
        

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

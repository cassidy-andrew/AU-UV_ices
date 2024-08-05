import sys
import spectools
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
    QDialog,
    QScrollArea,
    QComboBox
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


class SpecMplCanvas(FigureCanvasQTAgg):
    def __init__(self, parent=None):
        self.fig, self.axes = spectools.plot_absorbance([],
            return_fig_and_ax=True)
        super(SpecMplCanvas, self).__init__(self.fig)


class ScanMplCanvas(FigureCanvasQTAgg):
    def __init__(self, parent=None):
        self.fig, self.axes = spectools.plot_scans([], "Lambda", "Keith/nA",
            return_fig_and_ax=True)
        super(ScanMplCanvas, self).__init__(self.fig)


class spectrumDisplayTab():
    def __init__(self, debug):
        self.debug = debug
        # Create an outer layout
        self.outerLayout = QVBoxLayout()
        # Create a layout for the plot and spectrum list
        self.topLayout = QHBoxLayout()
        # Create a layout for the plot
        self.plotLayout = QVBoxLayout()
        # Create a layout for the spectrum list
        self.listLayout = QVBoxLayout()
        self.listButtonsLayout = QHBoxLayout()
        # Create a layout for the buttons
        self.bottomLayout = QHBoxLayout()

        # ---------------------------
        # Plot
        # ---------------------------

        self.sc = SpecMplCanvas(self)
        self.sc.setMinimumWidth(800)
        self.sc.setMinimumHeight(600)
        self.toolbar = NavigationToolbar(self.sc)
        self.xlims = [100, 700]
        self.ylims = [-0.1, 1.1]
        self.sc.axes[0].set_ylim(self.ylims)
        self.sc.axes[0].set_xlim(self.xlims)

        self.plotLayout.addWidget(self.toolbar)
        self.plotLayout.addWidget(self.sc)
        self.added_spectrum = False

        # ---------------------------
        # Spectrum Menu
        # ---------------------------
        # a place to store our spectra
        self.all_spectra = []

        # display list of spectra
        self.speclist = QListWidget()
        self.speclist.setMinimumWidth(400)

    
        # button for adding spectra
        self.add_spec_btn = QPushButton("Add Spectrum")
        self.listButtonsLayout.addWidget(self.add_spec_btn)
        self.add_spec_btn.pressed.connect(self.add_spectrum)

        self.remove_spec_btn = QPushButton("Remove Highlighted Spectra")
        self.remove_spec_btn.pressed.connect(lambda: self.remove_spectra(
            self.speclist.selectedItems()))
        self.listButtonsLayout.addWidget(self.remove_spec_btn)

        self.listLayout.addLayout(self.listButtonsLayout)
        self.listLayout.addWidget(self.speclist)
        
        # ---------------------------
        # Bottom Buttons
        # ---------------------------
        self.eb_clear = QPushButton("Clear Plot")
        self.eb_clear.pressed.connect(self.clear_plot)
        self.bottomLayout.addWidget(self.eb_clear)
        
        self.eb_sdata = QPushButton("Export Selected Data")
        self.eb_sdata.pressed.connect(self.export_sdata)
        self.bottomLayout.addWidget(self.eb_sdata)

        self.eb_adata = QPushButton("Export All Data")
        self.eb_adata.pressed.connect(self.export_adata)
        self.bottomLayout.addWidget(self.eb_adata)

        # ---------------------------
        # Nest the inner layouts into the outer layout
        # ---------------------------
        
        self.outerLayout.addLayout(self.topLayout)
        self.outerLayout.addLayout(self.bottomLayout)
        self.topLayout.addLayout(self.plotLayout)
        self.topLayout.addLayout(self.listLayout)

    def add_spectrum(self):
        """
        Makes a new guiSpectrum object and adds it to the list of spectra to be
        displayed in the spectrum list.
        """
        # make the guiSpectrum object
        item_index = len(self.all_spectra)
        guiSpec = guiSpectrum(item_index, self, self.debug)
        self.all_spectra.append(guiSpec)
        self.refresh_spectrum_list()

    def refresh_spectrum_list(self):
        self.speclist.clear()
        for guiSpec in self.all_spectra:
            guiSpec.make_list_item()
            self.speclist.addItem(guiSpec.slItem)
            self.speclist.setItemWidget(guiSpec.slItem, guiSpec.slItemWidget)

    def update_plot(self):
        """
        Re draw the spectrum plot
        """
        plot_data = []
        for guiSpec in self.all_spectra:
            if guiSpec.spec.data is not None:
                plot_data.append(guiSpec.spec)

        self.xlims = self.sc.axes[0].get_xlim()
        self.ylims = self.sc.axes[0].get_ylim()

        self.sc.axes[0].cla()
        self.sc.axes[1].cla()

        spectools.plot_absorbance(plot_data, ax1=self.sc.axes[0])

        self.sc.axes[0].set_ylim(self.ylims)
        self.sc.axes[0].set_xlim(self.xlims)
        self.sc.draw()

    def clear_plot(self):
        print('clear plot is to be implemented')

    def export_sdata(self):
        print('export data is to be implemented')

    def export_adata(self):
        print('export data is to be implemented')

    def remove_spectra(self, items):
        for item in items:
            for guiSpec in self.all_spectra:
                if guiSpec.uniqueID == item.toolTip():
                    self.all_spectra.remove(guiSpec)
        self.refresh_spectrum_list()
        self.update_plot()
    

class guiSpectrum():
    """
    A class to hold the functions and attributes needed to combine a spectrum
    with the GUI. It contains spec, a spectools Spectrum object, but also many
    other functions and methods to access and display its data. For example,
    update_name from this object lets you update the Spectrum, as well as the
    graphical elements at the same time.
    """
    def __init__(self, index, parentWindow, debug):
        self.parentWindow = parentWindow
        self.debug = debug
        # create the spectools Spectrum, give it a basic name
        self.spec = spectools.Spectrum(debug=debug)
        proposed_name = f"Spectrum {index}"
        for spec in self.parentWindow.all_spectra:
            if spec.spec.name == proposed_name:
                proposed_name += " again"
        self.uniqueID = "Spectrum ID: "+ datetime.now().strftime("%d%H%M%S%f")
        self.spec.change_name(proposed_name)
        self.guiBkgds = []
        self.guiSamples = []

        # create the edit window and assign the button to showing it
        self.editwindow = EditSpecWindow(self)

    def isOK(self, hide, recalculate=False, reupdate_plot=True):
        """
        The user is done editing, now perform actions to finish up behind the
        scenes.
        """
        # update plot
        if len(self.spec.bkgds) > 0:
            if recalculate:
                self.spec.average_scans()
            if reupdate_plot:
                self.parentWindow.update_plot()
            self.parentWindow.added_spectrum = True

        # update list check box
        self.slCheckBox.setText(self.spec.name)
        # update edit window name
        self.editwindow.setWindowTitle(f'Edit Spectrum: {self.spec.name}')
        # hide the edit window
        if hide == True:
            self.editwindow.hide()

    def getFiles(self, dtype=None):
        """
        Choose a file, a background or a sample
        """
        fnames = QFileDialog.getOpenFileNames()
        if len(fnames[0]) > 0 and dtype == 'bkgd':
            # add each file
            for fname in fnames[0]:
                this_bkgd = self.spec.add_bkgd(fname)
                this_guiBkgd = guiScan(self, this_bkgd, self.debug)
                self.guiBkgds.append(this_guiBkgd)
            # update list to current bkgds
            self.refreshBkgdList()
        elif len(fnames[0]) > 0 and dtype == 'sample':
            # add each file
            for fname in fnames[0]:
                this_sample = self.spec.add_sample(fname)
                this_guiSample = guiScan(self, this_sample, self.debug)
                self.guiSamples.append(this_guiSample)
            # update list to current bkgds
            self.refreshSampleList()
        self.editwindow.update_plot(
            xaxis=self.editwindow.xaxisControl.currentText(),
            yaxis=self.editwindow.yaxisControl.currentText(),
            keep_axlims=False)

    def refreshBkgdList(self):
        """
        Refresh the displayed background list
        """
        self.editwindow.bkgdList.clear()
        for guiBkgd in self.guiBkgds:
            guiBkgd.make_list_item()
            self.editwindow.bkgdList.addItem(guiBkgd.sclItem)
            self.editwindow.bkgdList.setItemWidget(guiBkgd.sclItem,
                                          guiBkgd.sclItemWidget)

    def refreshSampleList(self):
        """
        Refresh the displayed sample list
        """
        self.editwindow.sampleList.clear()
        for guiSample in self.guiSamples:
            guiSample.make_list_item()
            self.editwindow.sampleList.addItem(guiSample.sclItem)
            self.editwindow.sampleList.setItemWidget(guiSample.sclItem,
                                            guiSample.sclItemWidget)

    def removeFiles(self, items, dtype=None):
        """
        Remove backgroudns or samples
        """
        if dtype == 'bkgd':
            for item in items:
                self.spec.remove_bkgd(item.toolTip())
                for guiBkgd in self.guiBkgds:
                    if guiBkgd.scan.fname == item.toolTip():
                        self.guiBkgds.remove(guiBkgd)
            # update list to current bkgds
            self.refreshBkgdList()
        elif dtype == 'sample':
            for item in items:
                self.spec.remove_sample(item.toolTip())
                for guiSample in self.guiSamples:
                    if guiSample.scan.fname == item.toolTip():
                        self.guiSamples.remove(guiSample)

            # update list to current samples
            self.refreshSampleList()

    def update_color(self):
        """
        Change the color of a spectrum from a selector panel
        """
        color = None
        dialog = ColorPickerDialog()
        reply = dialog.exec()
        if reply == QDialog.Accepted:
            color = dialog.getColor().name()
        self.spec.change_color(color)
        self.editwindow.colorLabel.setText(self.spec.color)
        self.isOK(hide=False) 

    def cycle_color(self):
        """
        Change the color of the spectrum from a pre-set cycle
        """
        self.spec.cycle_color()
        self.editwindow.colorLabel.setText(self.spec.color)
        self.isOK(hide=False) 

    def update_linestyle(self, linestyle):
        """
        Change the linestyle of the spectrum
        """
        self.spec.change_linestyle(linestyle)
        self.isOK(hide=False)

    def update_linewidth(self, linewidth):
        """
        Change the linewidth of the spectrum
        """
        self.spec.change_linewidth(linewidth)
        self.isOK(hide=False)

    def update_offset(self, offset):
        """
        Change the offset of the spectrum
        """
        self.spec.change_offset(offset)
        self.isOK(hide=False)

    def update_name(self, name):
        """
        Change the name of the spectrum
        """
        # update Spectrum
        self.spec.change_name(name)
        # update list check box
        self.slCheckBox.setText(self.spec.name)
        # update edit window name
        self.editwindow.setWindowTitle(f'Edit Spectrum: {self.spec.name}')
        self.isOK(hide=False)

    def flip_visibility(self):
        """
        Change the visibility of the spectrum in plotting
        """
        # change the spectools Spectrum
        self.spec.flip_visibility()
        # update plot
        self.isOK(hide=False) #self.parentWindow.update_plot()

    def make_list_item(self):
        """
        """
        # the name and visibility check box
        self.slCheckBox = QCheckBox(self.spec.name)
        self.slCheckBox.setChecked(True)
        self.slCheckBox.stateChanged.connect(self.flip_visibility)
        # the color cycler
        self.slColorCycleButton = QPushButton("cycle color")
        self.slColorCycleButton.clicked.connect(self.cycle_color)
        # The edit window and button
        self.slEditButton = QPushButton("edit")
        self.slEditButton.clicked.connect(self.editwindow.show) 
        self.item_layout = QHBoxLayout()
        self.item_layout.addWidget(self.slCheckBox)
        self.item_layout.addWidget(self.slColorCycleButton)
        self.item_layout.addWidget(self.slEditButton)
        self.slItem = QListWidgetItem()
        self.slItemWidget = QWidget()
        #self.sclItem = QListWidgetItem()
        #self.sclItemWidget = QWidget()
        self.slItem.setToolTip(self.uniqueID)
        self.slItemWidget.setLayout(self.item_layout)
        self.slItem.setSizeHint(self.slItemWidget.sizeHint())

class guiScan():
    """
    A class to hold the functions and attributes needed to display a SingleScan
    object.
    """
    def __init__(self, parentSpectrum, scan, debug):
        self.parentSpectrum = parentSpectrum
        self.scan = scan
        self.listName = scan.fname[scan.fname.rfind("/")+1:]

        #self.sclItem = QListWidgetItem()
        #self.sclItemWidget = QWidget()
        
        # the name and visibility check box
        self.sclCheckBox = QCheckBox(self.listName)
        self.sclCheckBox.setChecked(True)
        self.sclCheckBox.stateChanged.connect(self.flip_visibility)

        # the color cycler
        self.sclColorCycleButton = QPushButton("cycle color")
        self.sclColorCycleButton.clicked.connect(self.cycle_color)

    def make_list_item(self):
        """
        """
        self.item_layout = QHBoxLayout()
        self.item_layout.addWidget(self.sclCheckBox)
        self.item_layout.addWidget(self.sclColorCycleButton)
        self.sclItem = QListWidgetItem()
        self.sclItemWidget = QWidget()
        self.sclItem.setToolTip(self.scan.fname)
        self.sclItemWidget.setLayout(self.item_layout)
        self.sclItem.setSizeHint(self.sclItemWidget.sizeHint())

    def flip_visibility(self):
        """
        Change the visibility of the spectrum in plotting
        """
        # change the spectools Spectrum
        self.scan.flip_visibility()
        # update plot
        self.parentSpectrum.editwindow.update_plot(
            xaxis=self.parentSpectrum.editwindow.xaxisControl.currentText(),
            yaxis=self.parentSpectrum.editwindow.yaxisControl.currentText(),
            keep_axlims=True)

    def cycle_color(self):
        """
        Change the color of the spectrum from a pre-set cycle
        """
        self.scan.cycle_color()
        self.parentSpectrum.editwindow.update_plot(
            xaxis=self.parentSpectrum.editwindow.xaxisControl.currentText(),
            yaxis=self.parentSpectrum.editwindow.yaxisControl.currentText(),
            keep_axlims=True)
        #self.isOK(hide=False) 

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


class ChangelogWindow(QWidget):
    def __init__(self, guispec):
        super().__init__()
        self.guiSpec = guispec
        self.setWindowTitle(f"Spectrum {self.guiSpec.spec.name} Changelog")

        self.label = ScrollLabel(self)
        self.label.setText(self.guiSpec.spec.changelog)
        self.label.setGeometry(0, 0, 1000, 600)

    def show_changelog_window(self):
        self.label.setText(self.guiSpec.spec.changelog)
        self.show()


class EditSpecWindow(QWidget):
    def __init__(self, guiSpec):
        super().__init__()
        # make sure we know what spectrum this edit window belongs to
        self.guiSpec = guiSpec
        
        # configure window basics
        self.setWindowTitle(f'Edit Spectrum: {self.guiSpec.spec.name}')
        self.eOuterLayout = QVBoxLayout()
        self.eTopLayout = QHBoxLayout()
        self.paramsLayout = QFormLayout()
        self.plotLayout = QVBoxLayout()
        self.scansLayout = QFormLayout()

        # -----------------------------------
        # create widgets in the edit window
        # -----------------------------------
        
        # Name edit
        self.nameLineEdit = QLineEdit()
        self.nameLineEdit.setText(self.guiSpec.spec.name)
        self.nameLineEdit.editingFinished.connect(
            lambda: self.guiSpec.update_name(self.nameLineEdit.text()))

        # color picker
        self.colorLabel = QLabel(self.guiSpec.spec.color)
        self.colorButton = QPushButton("choose color")
        self.colorButton.clicked.connect(self.guiSpec.update_color)
        self.colorLayout = QHBoxLayout()
        self.colorLayout.addWidget(self.colorLabel)
        self.colorLayout.addWidget(self.colorButton)

        # offset
        self.ewOffsetLineEdit = QDoubleSpinBox()
        self.ewOffsetLineEdit.setRange(-20.0, 20.0)
        self.ewOffsetLineEdit.setDecimals(4)
        self.ewOffsetLineEdit.setSingleStep(0.001)
        self.ewOffsetLineEdit.setValue(self.guiSpec.spec.offset)
        self.ewOffsetLineEdit.valueChanged.connect(
            lambda: self.guiSpec.update_offset(self.ewOffsetLineEdit.value()))

        # linestyle
        self.ewLSComboBox = QComboBox()
        self.ewLSComboBox.addItem("solid")
        self.ewLSComboBox.addItem("dotted")
        self.ewLSComboBox.addItem("dashed")
        self.ewLSComboBox.addItem("dashdot")
        self.ewLSComboBox.currentTextChanged.connect(
            self.guiSpec.update_linestyle)

        # linewidth
        self.linewidthLineEdit = QDoubleSpinBox()
        self.linewidthLineEdit.setRange(0.1, 20.0)
        self.linewidthLineEdit.setDecimals(1)
        self.linewidthLineEdit.setSingleStep(1.0)
        self.linewidthLineEdit.setValue(self.guiSpec.spec.linewidth)
        self.linewidthLineEdit.valueChanged.connect(
            lambda: self.guiSpec.update_linewidth(
                self.linewidthLineEdit.value()))

        # plot axis control
        self.xaxisControl = QComboBox()
        self.xaxisControl.addItem("Lambda")
        self.xaxisControl.addItem("Keith/nA")
        self.xaxisControl.addItem("Ch1/volts")
        self.xaxisControl.addItem("Ch2/volts")
        self.xaxisControl.addItem("Ch3/volts")
        self.xaxisControl.addItem("Z_Motor")
        self.xaxisControl.addItem("Beam_current")
        self.xaxisControl.addItem("temperature")
        self.xaxisControl.addItem("GC_Pres")
        self.xaxisControl.addItem("Time")
        self.xaxisControl.addItem("UBX_x")
        self.xaxisControl.addItem("UBX_y")
        self.xaxisControl.addItem("nor_signal")
        self.xaxisControl.addItem("wavelength")
        self.xaxisControl.addItem("av_signal")
        
        self.yaxisControl = QComboBox()
        self.yaxisControl.addItem("Lambda")
        self.yaxisControl.addItem("Keith/nA")
        self.yaxisControl.addItem("Ch1/volts")
        self.yaxisControl.addItem("Ch2/volts")
        self.yaxisControl.addItem("Ch3/volts")
        self.yaxisControl.addItem("Z_Motor")
        self.yaxisControl.addItem("Beam_current")
        self.yaxisControl.addItem("temperature")
        self.yaxisControl.addItem("GC_Pres")
        self.yaxisControl.addItem("Time")
        self.yaxisControl.addItem("UBX_x")
        self.yaxisControl.addItem("UBX_y")
        self.yaxisControl.addItem("nor_signal")
        self.yaxisControl.addItem("wavelength")
        self.yaxisControl.addItem("av_signal")
        self.yaxisControl.setCurrentIndex(1)

        # background files
        self.bkgdList = QListWidget()
        self.bkgdAddButton = QPushButton("Add Files")
        self.bkgdAddButton.clicked.connect(
            lambda: self.guiSpec.getFiles('bkgd'))
        self.bkgdRmButton = QPushButton("Remove Selected Files")
        self.bkgdRmButton.clicked.connect(
            lambda: self.guiSpec.removeFiles(self.bkgdList.selectedItems(),
                                             'bkgd'))

        # sample files
        self.sampleList = QListWidget()
        self.sampleAddButton = QPushButton("Add Files")
        self.sampleAddButton.clicked.connect(
            lambda: self.guiSpec.getFiles('sample'))
        self.sampleRmButton = QPushButton("Remove Selected Files")
        self.sampleRmButton.clicked.connect(
            lambda: self.guiSpec.removeFiles(self.sampleList.selectedItems(),
                                     'sample'))

        # apply and ok buttons
        self.applyButton = QPushButton("Apply")
        self.applyButton.clicked.connect(
            lambda: self.guiSpec.isOK(hide=False, recalculate=True))
        self.okButton = QPushButton("OK")
        self.okButton.clicked.connect(
            lambda: self.guiSpec.isOK(hide=True, recalculate=True))
        self.changelogButton = QPushButton("View Changelog")

        # create the changelog window and assign the button showing it
        self.clogwindow = ChangelogWindow(self.guiSpec)
        self.changelogButton.clicked.connect(
            self.clogwindow.show_changelog_window)

        #self.slEditButton.clicked.connect(self.editwindow.show)
        self.xaxisControl.currentTextChanged.connect(
            lambda:self.update_plot(
                xaxis=self.xaxisControl.currentText(),
                yaxis=self.yaxisControl.currentText(),
                keep_axlims=False))
        self.yaxisControl.currentTextChanged.connect(
            lambda:self.update_plot(
                xaxis=self.xaxisControl.currentText(),
                yaxis=self.yaxisControl.currentText(),
                keep_axlims=False))
        
        # regular edit options
        self.paramsLayout.addRow("Spectrum Name:", self.nameLineEdit)
        self.paramsLayout.addRow("Spectrum Color:", self.colorLayout)
        self.paramsLayout.addRow("Spectrum Offset:", self.ewOffsetLineEdit)
        self.paramsLayout.addRow("Spectrum Line Style:", self.ewLSComboBox)
        self.paramsLayout.addRow("Spectrum Line Width:", self.linewidthLineEdit)

        # plot axis controls
        self.scansLayout.addRow("Plot x-axis:", self.xaxisControl)
        self.scansLayout.addRow("Plot y-axis:", self.yaxisControl)
        
        # Background spectrum list
        self.bkgdListLayout = QVBoxLayout()
        self.bkgdButtonLayout = QHBoxLayout()
        self.bkgdButtonLayout.addWidget(self.bkgdAddButton)
        self.bkgdButtonLayout.addWidget(self.bkgdRmButton)
        self.bkgdListLayout.addLayout(self.bkgdButtonLayout)
        self.bkgdListLayout.addWidget(self.bkgdList)
        self.scansLayout.addRow("Background Files:", self.bkgdListLayout)
        
        # Sample spectrum list
        self.sampleListLayout = QVBoxLayout()
        self.sampleButtonLayout = QHBoxLayout()
        self.sampleButtonLayout.addWidget(self.sampleAddButton)
        self.sampleButtonLayout.addWidget(self.sampleRmButton)
        self.sampleListLayout.addLayout(self.sampleButtonLayout)
        self.sampleListLayout.addWidget(self.sampleList)
        self.scansLayout.addRow("Sample Files:", self.sampleListLayout)

        # buttons for OK and Apply
        self.applyLayout = QHBoxLayout()
        self.applyLayout.addWidget(self.okButton)
        self.applyLayout.addWidget(self.changelogButton)
        self.applyLayout.addWidget(self.applyButton)

        # title
        self.plotLabel = QLabel("Spectrum Components Plot", self)
        #self.plotLabel.setSizePolicy(QSizePolicy.Expanding,
        #                              QSizePolicy.Expanding)
        self.plotLabel.setAlignment(Qt.AlignCenter)
        self.plotLabel.setFont(QFont('Arial', 30))

        # the plot
        self.compCanvas = ScanMplCanvas(self)
        self.compCanvas.setMinimumWidth(800)
        self.compCanvas.setMinimumHeight(600)
        self.etoolbar = NavigationToolbar(self.compCanvas)
        self.exlims = [100, 700]
        self.eylims = [-0.1, 1.1]
        self.compCanvas.axes.set_ylim(self.eylims)
        self.compCanvas.axes.set_xlim(self.exlims)

        self.plotLayout.addWidget(self.plotLabel)
        self.plotLayout.addWidget(self.etoolbar)
        self.plotLayout.addWidget(self.compCanvas)

        # set the layout to the window
        self.eTopLayout.addLayout(self.paramsLayout)
        self.eTopLayout.addLayout(self.plotLayout)
        self.eTopLayout.addLayout(self.scansLayout)
        self.eOuterLayout.addLayout(self.eTopLayout) #self.paramsLayout)
        self.eOuterLayout.addLayout(self.applyLayout)
        self.holderwidget = QWidget()
        self.eOuterLayout.addWidget(self.holderwidget)
        self.setLayout(self.eOuterLayout)

    def update_plot(self, xaxis, yaxis, keep_axlims=True):
        """
        Re-draw the scan plot
        """
        all_guiScans = self.guiSpec.guiBkgds + self.guiSpec.guiSamples
        plot_data = []

        # get the data we want to plot
        # visibility check is donw within the spectools.plot_scans function
        # so we don't have to worry about it here
        for guiScan in all_guiScans:
            if guiScan.scan.data is not None:
                plot_data.append(guiScan.scan)

        # get our current axis limits to revert back if desired
        if keep_axlims:
            self.xlims = self.compCanvas.axes.get_xlim()
            self.ylims = self.compCanvas.axes.get_ylim()

        # redraw
        self.compCanvas.axes.cla()
        spectools.plot_scans(plot_data, xaxis, yaxis, ax=self.compCanvas.axes,
                             fig=self.compCanvas.fig)
        if keep_axlims:
            self.compCanvas.axes.set_ylim(self.ylims)
            self.compCanvas.axes.set_xlim(self.xlims)
        self.compCanvas.draw()

    def show_edit_window(self):
        """
        Shows the window where the user can edit the spectrum.
        """
        self.show()
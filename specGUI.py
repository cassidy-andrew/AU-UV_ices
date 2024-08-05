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
    QColor
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
        """# configure the layout of the new item in the list
        item_layout = QHBoxLayout()
        item_layout.addWidget(guiSpec.slCheckBox)
        item_layout.addWidget(guiSpec.slColorCycleButton)
        item_layout.addWidget(guiSpec.slEditButton)
        #item_layout.addWidget(guiSpec.slDetailsButton)
        # put the layout into the item widget of the guiSpectrum
        guiSpec.slItemWidget.setLayout(item_layout)
        guiSpec.slItem.setSizeHint(guiSpec.slItemWidget.sizeHint())
        # put the item widget of the guiSpectrum into the list
        self.speclist.addItem(guiSpec.slItem)
        self.speclist.setItemWidget(guiSpec.slItem, guiSpec.slItemWidget)"""

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
        print(self.all_spectra)
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
        self.uniqueID = "Spectrum ID: "+ datetime.now().strftime("%d%m%Y%H%M%S")
        self.spec.change_name(proposed_name)
        self.guiBkgds = []
        self.guiSamples = []
        # -----------------------------------
        # create widgets in the spectrum list
        # -----------------------------------
        
        
        # The details button
        #self.slDetailsButton = QPushButton("details")
        #self.slDetailsButton.clicked.connect(self.show_details)

        # -----------------------------------
        # create widgets in the edit window
        # -----------------------------------
        
        # Name edit
        self.ewNameLineEdit = QLineEdit()
        self.ewNameLineEdit.setText(self.spec.name)
        self.ewNameLineEdit.editingFinished.connect(
            lambda: self.update_name(self.ewNameLineEdit.text()))

        # color picker
        self.ewColorLabel = QLabel(self.spec.color)
        self.ewColorButton = QPushButton("choose color")
        self.ewColorButton.clicked.connect(self.update_color)
        self.ewColorLayout = QHBoxLayout()
        self.ewColorLayout.addWidget(self.ewColorLabel)
        self.ewColorLayout.addWidget(self.ewColorButton)

        # offset
        self.ewOffsetLineEdit = QDoubleSpinBox()
        self.ewOffsetLineEdit.setRange(-20.0, 20.0)
        self.ewOffsetLineEdit.setDecimals(4)
        self.ewOffsetLineEdit.setSingleStep(0.001)
        self.ewOffsetLineEdit.setValue(self.spec.offset)
        self.ewOffsetLineEdit.valueChanged.connect(
            lambda: self.update_offset(self.ewOffsetLineEdit.value()))

        # linestyle
        self.ewLSComboBox = QComboBox()
        self.ewLSComboBox.addItem("solid")
        self.ewLSComboBox.addItem("dotted")
        self.ewLSComboBox.addItem("dashed")
        self.ewLSComboBox.addItem("dashdot")
        self.ewLSComboBox.currentTextChanged.connect(self.update_linestyle)
        """self.ewLSLineEdit = QLineEdit()
        self.ewLSLineEdit.setText(self.spec.linestyle)
        self.ewLSLineEdit.editingFinished.connect(
            lambda: self.update_linestyle(self.ewLSLineEdit.text()))"""

        # linewidth
        self.ewLWidthLineEdit = QDoubleSpinBox()
        self.ewLWidthLineEdit.setRange(0.1, 20.0)
        self.ewLWidthLineEdit.setDecimals(1)
        self.ewLWidthLineEdit.setSingleStep(1.0)
        self.ewLWidthLineEdit.setValue(self.spec.linewidth)
        self.ewLWidthLineEdit.valueChanged.connect(
            lambda: self.update_linewidth(self.ewLWidthLineEdit.value()))

        # background files
        self.ewBkgdList = QListWidget()
        self.ewBkgdAddButton = QPushButton("Add Files")
        self.ewBkgdAddButton.clicked.connect(lambda: self.getFiles('bkgd'))
        self.ewBkgdRmButton = QPushButton("Remove Selected Files")
        self.ewBkgdRmButton.clicked.connect(
            lambda: self.removeFiles(self.ewBkgdList.selectedItems(), 'bkgd'))

        # sample files
        self.ewSampleList = QListWidget()
        self.ewSampleAddButton = QPushButton("Add Files")
        self.ewSampleAddButton.clicked.connect(lambda: self.getFiles('sample'))
        self.ewSampleRmButton = QPushButton("Remove Selected Files")
        self.ewSampleRmButton.clicked.connect(
            lambda: self.removeFiles(self.ewSampleList.selectedItems(),
                                     'sample'))

        # apply and ok buttons
        self.ewApplyButton = QPushButton("Apply")
        self.ewApplyButton.clicked.connect(lambda: self.isOK(hide=False, recalculate=True))
        self.ewOKButton = QPushButton("OK")
        self.ewOKButton.clicked.connect(lambda: self.isOK(hide=True, recalculate=True))
        self.ewChangelogButton = QPushButton("View Changelog")

        # create the changelog window and assign the button showing it
        self.clogwindow = ChangelogWindow(self)
        self.ewChangelogButton.clicked.connect(self.clogwindow.show_changelog_window)

        # create the edit window and assign the button to showing it
        self.editwindow = EditSpecWindow(self)
        #self.slEditButton.clicked.connect(self.editwindow.show)        

    def isOK(self, hide, recalculate=False):
        """
        The user is done editing, now perform actions to finish up behind the
        scenes.
        """
        # update plot
        if len(self.spec.bkgds) > 0:
            if recalculate:
                self.spec.average_scans()
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

    def refreshBkgdList(self):
        """
        Refresh the displayed background list
        """
        self.ewBkgdList.clear()
        for guiBkgd in self.guiBkgds:
            guiBkgd.make_list_item()
            self.ewBkgdList.addItem(guiBkgd.sclItem)
            self.ewBkgdList.setItemWidget(guiBkgd.sclItem,
                                          guiBkgd.sclItemWidget)

    def refreshSampleList(self):
        """
        Refresh the displayed sample list
        """
        self.ewSampleList.clear()
        for guiSample in self.guiSamples:
            guiSample.make_list_item()
            self.ewSampleList.addItem(guiSample.sclItem)
            self.ewSampleList.setItemWidget(guiSample.sclItem,
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
        self.ewColorLabel.setText(self.spec.color)
        self.isOK(hide=False) 

    def cycle_color(self):
        """
        Change the color of the spectrum from a pre-set cycle
        """
        self.spec.cycle_color()
        self.ewColorLabel.setText(self.spec.color)
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
        #self.parentSpectrum.editwindow.update_plot()

    def cycle_color(self):
        """
        Change the color of the spectrum from a pre-set cycle
        """
        self.scan.cycle_color()
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
        self.guispec = guispec
        self.setWindowTitle(f"Spectrum {self.guispec.spec.name} Changelog")

        self.label = ScrollLabel(self)
        self.label.setText(self.guispec.spec.changelog)
        self.label.setGeometry(0, 0, 1000, 600)

    def show_changelog_window(self):
        self.label.setText(self.guispec.spec.changelog)
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
        self.eParamsLayout = QFormLayout()
        self.ePlotLayout = QVBoxLayout()
        self.eScansLayout = QFormLayout()
        
        # regular edit options
        self.eParamsLayout.addRow("Spectrum Name:", self.guiSpec.ewNameLineEdit)
        self.eParamsLayout.addRow("Spectrum Color:", self.guiSpec.ewColorLayout)
        self.eParamsLayout.addRow("Spectrum Offset:", self.guiSpec.ewOffsetLineEdit)
        self.eParamsLayout.addRow("Spectrum Line Style:", self.guiSpec.ewLSComboBox)
        self.eParamsLayout.addRow("Spectrum Line Width:", self.guiSpec.ewLWidthLineEdit)
        
        # Background spectrum list
        self.eBkgdListLayout = QVBoxLayout()
        self.eBkgdButtonLayout = QHBoxLayout()
        self.eBkgdButtonLayout.addWidget(self.guiSpec.ewBkgdAddButton)
        self.eBkgdButtonLayout.addWidget(self.guiSpec.ewBkgdRmButton)
        self.eBkgdListLayout.addLayout(self.eBkgdButtonLayout)
        self.eBkgdListLayout.addWidget(self.guiSpec.ewBkgdList)
        self.eScansLayout.addRow("Background Files:", self.eBkgdListLayout)
        
        # Sample spectrum list
        self.eSampleListLayout = QVBoxLayout()
        self.eSampleButtonLayout = QHBoxLayout()
        self.eSampleButtonLayout.addWidget(self.guiSpec.ewSampleAddButton)
        self.eSampleButtonLayout.addWidget(self.guiSpec.ewSampleRmButton)
        self.eSampleListLayout.addLayout(self.eSampleButtonLayout)
        self.eSampleListLayout.addWidget(self.guiSpec.ewSampleList)
        self.eScansLayout.addRow("Sample Files:", self.eSampleListLayout)

        # buttons for OK and Apply
        self.eApplyLayout = QHBoxLayout()
        self.eApplyLayout.addWidget(self.guiSpec.ewOKButton)
        self.eApplyLayout.addWidget(self.guiSpec.ewChangelogButton)
        self.eApplyLayout.addWidget(self.guiSpec.ewApplyButton)

        # the plot
        self.esc = SpecMplCanvas(self)
        self.esc.setMinimumWidth(800)
        self.esc.setMinimumHeight(600)
        self.etoolbar = NavigationToolbar(self.esc)
        self.exlims = [100, 700]
        self.eylims = [-0.1, 1.1]
        self.esc.axes[0].set_ylim(self.eylims)
        self.esc.axes[0].set_xlim(self.exlims)

        self.ePlotLayout.addWidget(self.etoolbar)
        self.ePlotLayout.addWidget(self.esc)

        # set the layout to the window
        self.eTopLayout.addLayout(self.eParamsLayout)
        self.eTopLayout.addLayout(self.ePlotLayout)
        self.eTopLayout.addLayout(self.eScansLayout)
        self.eOuterLayout.addLayout(self.eTopLayout) #self.eParamsLayout)
        self.eOuterLayout.addLayout(self.eApplyLayout)
        self.holderwidget = QWidget()
        self.eOuterLayout.addWidget(self.holderwidget)
        self.setLayout(self.eOuterLayout)

    def show_edit_window(self):
        """
        Shows the window where the user can edit the spectrum.
        """
        self.show()
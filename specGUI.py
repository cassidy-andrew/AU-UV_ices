import sys
import spectools

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
    QDialog
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
        # Create a layout for the buttons
        self.bottomLayout = QHBoxLayout()

        # ---------------------------
        # Plot
        # ---------------------------

        self.sc = SpecMplCanvas(self)
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
        # button for adding spectra
        self.add_spec_btn = QPushButton("Add Spectrum")
        self.listLayout.addWidget(self.add_spec_btn)
        self.add_spec_btn.pressed.connect(lambda: self.add_spectrum(self.debug))

        # display list of spectra
        self.speclist = QListWidget()
        self.speclist.setMinimumWidth(300)
        self.listLayout.addWidget(self.speclist)
        
        # ---------------------------
        # Bottom Buttons
        # ---------------------------
        self.eb_clear = QPushButton("Clear Plot")
        self.eb_clear.pressed.connect(self.clear_plot)
        self.bottomLayout.addWidget(self.eb_clear)

        self.eb_remove = QPushButton("Remove Selected Data")
        self.eb_remove.pressed.connect(self.remove_data)
        self.bottomLayout.addWidget(self.eb_remove)
        
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

    def add_spectrum(self, debug):
        """
        Makes a new guiSpectrum object and adds it to the list of spectra to be
        displayed in the spectrum list.
        """
        # make the guiSpectrum object
        item_index = len(self.all_spectra)
        guiSpec = guiSpectrum(item_index, self, debug)
        self.all_spectra.append(guiSpec)
        # configure the layout of the new item in the list
        item_layout = QHBoxLayout()
        item_layout.addWidget(guiSpec.slCheckBox)
        item_layout.addWidget(guiSpec.slColorCycleButton)
        item_layout.addWidget(guiSpec.slEditbutton)
        # put the layout into the item widget of the guiSpectrum
        guiSpec.slItemWidget.setLayout(item_layout)
        guiSpec.slItem.setSizeHint(guiSpec.slItemWidget.sizeHint())
        # put the item widget of the guiSpectrum into the list
        self.speclist.addItem(guiSpec.slItem)
        self.speclist.setItemWidget(guiSpec.slItem, guiSpec.slItemWidget)

    def update_plot(self):
        """
        Re draw the spectrum plot
        """
        plot_data = []
        for guiSpec in self.all_spectra:
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

    def remove_data(self):
        print('remove data is to be implemented')
    

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
        # create the spectools Spectrum, give it a basic name
        self.spec = spectools.Spectrum(debug=debug)
        self.spec.change_name(f"Spectrum {index}")
        # -----------------------------------
        # create widgets in the spectrum list
        # -----------------------------------
        self.slItem = QListWidgetItem()
        self.slItemWidget = QWidget()
        # the name and visibility check box
        self.slCheckBox = QCheckBox(self.spec.name)
        self.slCheckBox.setChecked(True)
        self.slCheckBox.stateChanged.connect(self.flip_visibility)
        # the color cycler
        self.slColorCycleButton = QPushButton("cycle color")
        self.slColorCycleButton.clicked.connect(self.cycle_color)
        # The edit window and button
        self.slEditbutton = QPushButton("edit")

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
        self.ewLSLineEdit = QLineEdit()
        self.ewLSLineEdit.setText(self.spec.linestyle)
        self.ewLSLineEdit.editingFinished.connect(
            lambda: self.update_linestyle(self.ewLSLineEdit.text()))

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
        self.ewApplyButton.clicked.connect(lambda: self.isOK(hide=False))
        self.ewOKButton = QPushButton("OK")
        self.ewOKButton.clicked.connect(lambda: self.isOK(hide=True))

        # create the edit window and assign the button to showing it
        self.editwindow = EditSpecWindow(self)
        self.slEditbutton.clicked.connect(self.editwindow.show)
        

    def isOK(self, hide):
        """
        The user is done editing, now perform actions to finish up behind the
        scenes.
        """
        # update plot
        if len(self.spec.bkgd_files) > 0:
            self.spec.average_scans()
            self.parentWindow.update_plot()
            self.parentWindow.added_spectrum = True

        # update list check box
        self.slCheckBox.setText(self.spec.name)
        # update edit window name
        self.editwindow.setWindowTitle(f'Edit {self.spec.name}')
        # hide the edit window
        if hide == True:
            self.editwindow.hide()

    def getFiles(self, dtype=None):
        """
        Choose a file, a background or a sample
        """
        fnames = QFileDialog.getOpenFileNames()
        print(fnames)
        if len(fnames[0]) > 0 and dtype == 'bkgd':
            # add each file
            for fname in fnames[0]:
               self.spec.add_bkgd(fname)

            # update list to current bkgds
            self.refreshBkgdList()
        elif len(fnames[0]) > 0 and dtype == 'sample':
            # add each file
            for fname in fnames[0]:
               self.spec.add_sample(fname)

            # update list to current bkgds
            self.refreshSampleList()

    def refreshBkgdList(self):
        """
        Refresh the displayed background list
        """
        self.ewBkgdList.clear()
        for fname in self.spec.bkgd_files:
            this_item = QListWidgetItem()
            this_item.setToolTip(fname)
            this_item.setText(fname[fname.rfind("/")+1:])
            self.ewBkgdList.addItem(this_item)

    def refreshSampleList(self):
        """
        Refresh the displayed sample list
        """
        self.ewSampleList.clear()
        for fname in self.spec.sample_files:
            this_item = QListWidgetItem()
            this_item.setToolTip(fname)
            this_item.setText(fname[fname.rfind("/")+1:])
            self.ewSampleList.addItem(this_item)

    def removeFiles(self, items, dtype=None):
        """
        Remove backgroudns or samples
        """
        if dtype == 'bkgd':
            for item in items:
                self.spec.remove_bkgd(item.toolTip())

            # update list to current bkgds
            self.refreshBkgdList()
        elif dtype == 'sample':
            for item in items:
                self.spec.remove_sample(item.toolTip())

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
        self.isOK(hide=False)

    def flip_visibility(self):
        """
        Change the visibility of the spectrum in plotting
        """
        # change the spectools Spectrum
        self.spec.flip_visibility()
        # update plot
        self.parentWindow.update_plot()


class EditSpecWindow(QWidget):
    def __init__(self, guiSpec):
        super().__init__()
        # make sure we know what spectrum this edit window belongs to
        self.guiSpec = guiSpec
        
        # configure window basics
        self.setWindowTitle(f'Edit Spectrum {self.guiSpec.spec.name}')
        outerLayout = QVBoxLayout()
        pagelayout = QFormLayout()
        
        # regular edit options
        pagelayout.addRow("Spectrum Name:", self.guiSpec.ewNameLineEdit)
        pagelayout.addRow("Spectrum Color:", self.guiSpec.ewColorLayout)
        pagelayout.addRow("Spectrum Offset:", self.guiSpec.ewOffsetLineEdit)
        pagelayout.addRow("Spectrum Line Style:", self.guiSpec.ewLSLineEdit)
        pagelayout.addRow("Spectrum Line Width:", self.guiSpec.ewLWidthLineEdit)
        
        # Background spectrum list
        bkgdListLayout = QVBoxLayout()
        bkgdButtonLayout = QHBoxLayout()
        bkgdButtonLayout.addWidget(self.guiSpec.ewBkgdAddButton)
        bkgdButtonLayout.addWidget(self.guiSpec.ewBkgdRmButton)
        bkgdListLayout.addLayout(bkgdButtonLayout)
        bkgdListLayout.addWidget(self.guiSpec.ewBkgdList)
        pagelayout.addRow("Background Files:", bkgdListLayout)
        
        # Sample spectrum list
        sampleListLayout = QVBoxLayout()
        sampleButtonLayout = QHBoxLayout()
        sampleButtonLayout.addWidget(self.guiSpec.ewSampleAddButton)
        sampleButtonLayout.addWidget(self.guiSpec.ewSampleRmButton)
        sampleListLayout.addLayout(sampleButtonLayout)
        sampleListLayout.addWidget(self.guiSpec.ewSampleList)
        pagelayout.addRow("Sample Files:", sampleListLayout)

        # buttons for OK and Apply
        applyLayout = QHBoxLayout()
        applyLayout.addWidget(self.guiSpec.ewOKButton)
        applyLayout.addWidget(self.guiSpec.ewApplyButton)

        # set the layout to the window
        outerLayout.addLayout(pagelayout)
        outerLayout.addLayout(applyLayout)
        self.holderwidget = QWidget()
        outerLayout.addWidget(self.holderwidget)
        self.setLayout(outerLayout)

    def show_edit_window(self):
        """
        Shows the window where the user can edit the spectrum.
        """
        self.show()
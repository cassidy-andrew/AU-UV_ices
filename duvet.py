import sys
import spectools
import deptools

import matplotlib
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import (
    FigureCanvasQTAgg,
    NavigationToolbar2QT as NavigationToolbar
)
matplotlib.use('QtAgg')
plt.style.use('./au-uv.mplstyle')

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
    QTabWidget
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

class DepMplCanvas(FigureCanvasQTAgg):
    def __init__(self, parent=None):
        self.fig, self.axes = plt.subplots(1, 1)
        self.fig.set_size_inches(16/2.5, 9/2.5)
        self.axes.set_ylim(0, 1)
        self.axes.set_xlim(0, 1)
        super(DepMplCanvas, self).__init__(self.fig)

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        # ---------------------------------------------------------------------
        # Setup window and tabs
        # ---------------------------------------------------------------------
        self.setWindowTitle("DUVET: Danish UV End-station Tool")
        # define the top-level layout of the window
        self.layout = QVBoxLayout()
        # define the tab widget that will exist in the top level layout
        self.tabs = QTabWidget()
        # define the individual tab placeholder widgets
        self.specTab = QWidget()
        self.depTab = QWidget()

        # ---------------------------------------------------------------------
        # Setup spectrum display tab
        # ---------------------------------------------------------------------

        # create the spectrum display
        self.SDT = spectrumDisplayTab()
        # set the layout of the spectrum display tab placeholder widget
        self.specTab.setLayout(self.SDT.outerLayout)

        # ---------------------------------------------------------------------
        # Setup deposition fitting tab
        # ---------------------------------------------------------------------

        self.DFT = depositionFittingTab()
        self.depTab.setLayout(self.DFT.outerLayout)
        # ---------------------------------------------------------------------
        # Finalize main window
        # ---------------------------------------------------------------------

        # add the individual tabs to the tabs widget
        self.tabs.addTab(self.specTab, "Spectrum Display")
        self.tabs.addTab(self.depTab, "Deposition Fitting")

        # Set the window's main layout
        self.layout.addWidget(self.tabs)
        self.setLayout(self.layout)


class depositionFittingTab():
    def __init__(self):
        self.outerLayout = QVBoxLayout()
        # Create a layout for the plot and scan list
        self.topLayout = QHBoxLayout()
        # Create a layout for the plot
        self.plotLayout = QVBoxLayout()
        # Create a layout for the scan
        self.scanLayout = QVBoxLayout()
        # Create a layout for the buttons
        self.bottomLayout = QHBoxLayout()

        # ---------------------------
        # Plot
        # ---------------------------

        self.sc = DepMplCanvas(self)
        self.toolbar = NavigationToolbar(self.sc)

        self.plotLayout.addWidget(self.toolbar)
        self.plotLayout.addWidget(self.sc)
        #self.sc.axes.plot([0,1,2,3,4], [10,1,20,3,40])

        # ---------------------------
        # Spectrum Menu
        # ---------------------------
        
        # button for adding a scan
        self.add_scan_btn = QPushButton("Add Scan")
        self.add_scan_btn.pressed.connect(self.add_scan)
        #self.scanLayout.addWidget(self.add_scan_btn)

        # display list of spectra
        #self.speclist = QListWidget()
        #self.listLayout.addWidget(self.speclist)

        # ---------------------------
        # Bottom Buttons
        # ---------------------------
        self.eb_clear = QPushButton("Clear Plot")
        self.eb_clear.pressed.connect(self.clear_plot)
        self.bottomLayout.addWidget(self.eb_clear)

        self.eb_adata = QPushButton("Export Fit Parameters")
        self.eb_adata.pressed.connect(self.export_adata)
        self.bottomLayout.addWidget(self.eb_adata)

        # ---------------------------
        # Nest the inner layouts into the outer layout
        # ---------------------------
        self.topLayout.addLayout(self.plotLayout)
        #self.topLayout.addLayout(self.scanLayout)
        #self.topLayout.addWidget(self.add_scan_btn)
        
        self.outerLayout.addLayout(self.topLayout)
        self.outerLayout.addLayout(self.bottomLayout)
        

    def add_scan(self):
        """
        Add a timescan
        """
        print("to be implimented")

    def clear_plot(self):
        print('clear plot is to be implemented')

    def export_sdata(self):
        print('export data is to be implemented')

    def export_adata(self):
        print('export data is to be implemented')

    def remove_data(self):
        print('remove data is to be implemented')
        


class spectrumDisplayTab():
    def __init__(self):
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
        #self.sc.axes[0].set_ylim((0, 1))
        #self.sc.axes[0].set_xlim((110, 340))

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
        self.add_spec_btn.pressed.connect(self.add_spectrum)
        self.listLayout.addWidget(self.add_spec_btn)

        # display list of spectra
        self.speclist = QListWidget()
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

    def add_spectrum(self):
        """
        Makes a new guiSpectrum object and adds it to the list of spectra to be
        displayed in the spectrum list.
        """
        # make the guiSpectrum object
        item_index = len(self.all_spectra)
        guiSpec = guiSpectrum(item_index, self)
        self.all_spectra.append(guiSpec)
        # configure the layout of the new item in the list
        item_layout = QHBoxLayout()
        item_layout.addWidget(guiSpec.slCheckBox)
        item_layout.addWidget(guiSpec.slEditbutton)
        # put the layout into the item widget of the guiSpectrum
        guiSpec.slItemWidget.setLayout(item_layout)
        guiSpec.slItem.setSizeHint(guiSpec.slItemWidget.sizeHint())
        # put the item widget of the guiSpectrum into the list
        self.speclist.addItem(guiSpec.slItem)
        self.speclist.setItemWidget(guiSpec.slItem, guiSpec.slItemWidget)

    def update_plot(self):
        plot_data = []
        for guiSpec in self.all_spectra:
            plot_data.append(guiSpec.spec)

        # if the figure is empty, don't assign limits
        #contained_artists = self.sc.fig.get_children()
        #print(contained_artists)
        if self.added_spectrum:
            ylims = self.sc.axes[0].get_ylim()
            xlims = self.sc.axes[0].get_xlim()
            
        self.sc.axes[0].cla()
        self.sc.axes[1].cla()
        #self.sc.fig, self.sc.axes = spectools.plot_absorbance(plot_data,
        #                                              return_fig_and_ax=True)
        spectools.plot_absorbance(plot_data, ax1=self.sc.axes[0])
        if self.added_spectrum:
            self.sc.axes[0].set_ylim(ylims)
            self.sc.axes[0].set_xlim(xlims)
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
    def __init__(self, index, parentWindow):
        self.parentWindow = parentWindow
        # create the spectools Spectrum, give it a basic name
        self.spec = spectools.Spectrum(debug=True)
        self.spec.change_name(f"Spectrum {index}")
        # create widgets in the spectrum list
        self.slItem = QListWidgetItem()
        self.slItemWidget = QWidget()
        self.slCheckBox = QCheckBox(self.spec.name)
        self.slCheckBox.setChecked(True)
        self.slCheckBox.stateChanged.connect(self.flip_visibility)
        self.slEditbutton = QPushButton("edit")
        
        # create the edit window widgets
        self.ewNameLineEdit = QLineEdit()
        self.ewNameLineEdit.setText(self.spec.name)
        self.ewNameLineEdit.editingFinished.connect(
            lambda: self.update_name(self.ewNameLineEdit.text()))

        self.ewColorLineEdit = QLineEdit()
        self.ewColorLineEdit.setText(self.spec.color)
        self.ewColorLineEdit.editingFinished.connect(
            lambda: self.update_color(self.ewColorLineEdit.text()))

        self.ewOffsetLineEdit = QDoubleSpinBox()
        self.ewOffsetLineEdit.setRange(-20.0, 20.0)
        self.ewOffsetLineEdit.setDecimals(4)
        self.ewOffsetLineEdit.setSingleStep(0.001)
        self.ewOffsetLineEdit.setValue(self.spec.offset)
        self.ewOffsetLineEdit.valueChanged.connect(
            lambda: self.update_offset(self.ewOffsetLineEdit.value()))

        self.ewLSLineEdit = QLineEdit()
        self.ewLSLineEdit.setText(self.spec.linestyle)
        self.ewLSLineEdit.editingFinished.connect(
            lambda: self.update_linestyle(self.ewLSLineEdit.text()))

        self.ewBkgdList = QListWidget()
        self.ewBkgdAddButton = QPushButton("Add Files")
        self.ewBkgdAddButton.clicked.connect(lambda: self.getFiles('bkgd'))
        self.ewBkgdRmButton = QPushButton("Remove Selected Files")
        self.ewBkgdRmButton.clicked.connect(
            lambda: self.removeFiles(self.ewBkgdList.selectedItems(), 'bkgd'))

        self.ewSampleList = QListWidget()
        self.ewSampleAddButton = QPushButton("Add Files")
        self.ewSampleAddButton.clicked.connect(lambda: self.getFiles('sample'))
        self.ewSampleRmButton = QPushButton("Remove Selected Files")
        self.ewSampleRmButton.clicked.connect(
            lambda: self.removeFiles(self.ewSampleList.selectedItems(),
                                     'sample'))

        self.ewApplyButton = QPushButton("Apply")
        self.ewApplyButton.clicked.connect(lambda: self.isOK(hide=False))
        self.ewOKButton = QPushButton("OK")
        self.ewOKButton.clicked.connect(lambda: self.isOK(hide=True))

        # create the edit window. The edit window is always present in memory,
        # just shown or hidden when the user presses buttons to open or close.
        # this lets it retain its data each time and be consistent.
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
            self.added_spectrum = True

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
        self.ewBkgdList.clear()
        for fname in self.spec.bkgd_files:
            this_item = QListWidgetItem()
            this_item.setToolTip(fname)
            this_item.setText(fname[fname.rfind("/")+1:])
            self.ewBkgdList.addItem(this_item)

    def refreshSampleList(self):
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

    def update_color(self, color):
        """
        """
        self.spec.change_color(color)
        self.isOK(hide=False)

    def update_linestyle(self, linestyle):
        """
        """
        self.spec.change_linestyle(linestyle)
        self.isOK(hide=False)

    def update_offset(self, offset):
        """
        """
        self.spec.change_offset(offset)
        self.isOK(hide=False)

    def update_name(self, name):
        """
        Change the name of the spectrum as well as 
        """
        # update Spectrum
        self.spec.change_name(name)
        self.isOK(hide=False)

    def flip_visibility(self):
        # change the spectools Spectrum
        self.spec.flip_visibility()
        # update plot
        self.parentWindow.update_plot()

class EditSpecWindow(QWidget):
    def __init__(self, guiSpec):
        super().__init__()
        self.guiSpec = guiSpec
        # configure window basics
        self.setWindowTitle(f'Edit Spectrum {self.guiSpec.spec.name}')
        # configure the window form
        outerLayout = QVBoxLayout()
        pagelayout = QFormLayout()
        pagelayout.addRow("Spectrum Name:", self.guiSpec.ewNameLineEdit)
        pagelayout.addRow("Spectrum Color:", self.guiSpec.ewColorLineEdit)
        pagelayout.addRow("Spectrum Offset:", self.guiSpec.ewOffsetLineEdit)
        pagelayout.addRow("Spectrum Line Style:", self.guiSpec.ewLSLineEdit)
        bkgdListLayout = QVBoxLayout()
        bkgdButtonLayout = QHBoxLayout()
        bkgdButtonLayout.addWidget(self.guiSpec.ewBkgdAddButton)
        bkgdButtonLayout.addWidget(self.guiSpec.ewBkgdRmButton)
        bkgdListLayout.addLayout(bkgdButtonLayout)
        bkgdListLayout.addWidget(self.guiSpec.ewBkgdList)
        pagelayout.addRow("Background Files:", bkgdListLayout)
        sampleListLayout = QVBoxLayout()
        sampleButtonLayout = QHBoxLayout()
        sampleButtonLayout.addWidget(self.guiSpec.ewSampleAddButton)
        sampleButtonLayout.addWidget(self.guiSpec.ewSampleRmButton)
        sampleListLayout.addLayout(sampleButtonLayout)
        sampleListLayout.addWidget(self.guiSpec.ewSampleList)
        pagelayout.addRow("Sample Files:", sampleListLayout)
        
        applyLayout = QHBoxLayout()
        applyLayout.addWidget(self.guiSpec.ewOKButton)
        applyLayout.addWidget(self.guiSpec.ewApplyButton)

        outerLayout.addLayout(pagelayout)
        outerLayout.addLayout(applyLayout)
        #outerLayout.addWidget(self.guiSpec.ewOKButton)
        # create holderwidget and set the layout
        self.holderwidget = QWidget()
        outerLayout.addWidget(self.holderwidget)
        self.setLayout(outerLayout)

    def show_edit_window(self):
        """
        Shows the window where the user can edit the spectrum.
        """
        self.show()



if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
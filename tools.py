import numpy as np
import pandas as pd
import glob

from os.path import join
from os import listdir
from sys import float_info

import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.ticker import FormatStrFormatter

import scipy.constants as constants
from cycler import cycler


# When we want to plot a spectrum we need to choose the scans
# Each scan has a background, and a sample

class SingleScan:
    """
    Represents one scan
    
    Parameters belonging to the fully constructed object:
        
    bkgd : (pandas.DataFrame) The background scan
    data : (pandas.DataFrame) The calibrated data
    sample : (pandas.DataFrame) The sample scan
    """
    def __init__(self, bkgd_fname, sample_fname):
        """
        Parameters required to construct the object:
        
        bkgd_fname : (str) the path to the background file for this scan
        sample_fname : (str) the path to the sample file for this scan
        """
        # get the raw data ready to go
        self._setup_scan_files(bkgd_fname, sample_fname)
        
        # use the raw data to create the calibrated scan data
        self._calibrate_scan()
        
    def _setup_scan_files(self, bkgd_fname, sample_fname):
        """
        Reads the raw data files and formats them correctly, adding necessary
        columns and unit conversions.
        
        bkgd_fname : (str) the path to the background file for this scan
        sample_fname : (str) the path to the sample file for this scan
        """
        column_names = ['Lambda', 'Keith/nA', 'Ch1/volts',
                        'Ch2/volts', 'Ch3/volts', 'Z_Motor','Beam_current',
                        'temperature', 'GC_Pres', 'Time', 'UBX_x', 'UBX_y']
    
        # handle the background
        bkgd = pd.read_csv(bkgd_fname, header=[15], delimiter=r"\s+")
        bkgd.columns = column_names
        bkgd['nor_signal'] = ((180/bkgd['Beam_current']) * \
                                  bkgd['Keith/nA'])
        bkgd['wavelength'] = bkgd['Lambda']
        bkgd['av_BkGd_signal'] = (bkgd['nor_signal'] + \
                                      bkgd['nor_signal'])/2
        
        # handle the sample
        if sample_fname == None:
            # if there is no sample for this background, just set everything
            # to zeros.
            sample = bkgd.copy(deep=True)
            # assign the correct column names
            #sample.columns = column_names
            sample['wavelength'] = sample['Lambda']
            sample['nor_signal'] = np.zeros(len(sample['wavelength']))
            sample['av_sample_signal'] = np.zeros(len(sample['wavelength']))
        else:
            # otherwise, do the same calculations as for the background
            sample = pd.read_csv(sample_fname, header=[15], delimiter=r"\s+")
            sample.columns = column_names
            sample['nor_signal'] = ((180/sample['Beam_current']) * \
                                    sample['Keith/nA'])
            sample['wavelength'] = sample['Lambda']
            sample['av_sample_signal'] = (sample['nor_signal'] + \
                                        sample['nor_signal'])/2
        
        # assign the formatted scans to object parameters
        self.bkgd = bkgd
        self.sample = sample
        
    
    def _calibrate_scan(self):
        """
        Calibrates the scan using the scan's background and sample.
        """
        # a place for the calibrated data to go
        df = pd.DataFrame()
        
        if (self.sample['av_sample_signal'] == 0).all():
            # if there was no sample signal, set everything to zero
            df['absorbance'] = self.sample['av_sample_signal']
        else:
            # otherwise, calculate absorbance, 
            # making sure not to take a log of -ve numbers
            ratio1 = self.bkgd['av_BkGd_signal']/ \
                     self.sample['av_sample_signal']
            df['absorbance'] = np.log10(ratio1, where=((ratio1)>0)) 
        
        df['wavelength'] = self.bkgd['wavelength']
        
        self.data = df
        
        
class Spectrum:
    """
    Represents a spectrum, so the average of one or more scans
    
    Parameters belonging to the fully constructed object:
        
        bkgds : (list)
        color : (str) the hex color used for plotting this spectrum.
        data : (pandas.DataFrame) the data belonging to this
               spectrum, averaged together from its corresponding
               scans.
        name : (str) the name of this spectrum, which will be shown
               in plot legends.
        samples (list)
        scans : (list) a list of SingleScan objects that will be
                averaged together to make this spectrum
        offset : (float) by how much the spectrum should be offset
                 in the plot_absorbance() plot, in absorbance units.
                 Defaults to 0.0
        visible : (boolean) whether the spectrum should appear in
                  the plot generated by plot_absorbance() or not.
                  Defaults to True/.
    """
    def __init__(self):
        """                
        """
        # declare parameters
        self.name = ""
        self.visible = True
        self.offset = 0.0
        self.color = "#000000"
        self.scans = []
        self.bkgds = []
        self.samples = []
        self.data = None
        
    def average_scans(self):
        """
        Averages the scans relating to this spectrum.
        """
        # match backgrounds and spectra
        
        # create scan objects
        
        # average the scan objects
        
        #self.data = averaged
    
    def change_name(self, new_name):
        """
        Changes the name of this spectrum
        
        new_name : (str) the new name for this spectrum
        """
        self.name = new_name
    
    def add_bkgd(self, bkgd_fname):
        """
        Adds a background file to this spectrum's list of backgrounds
        
        bkgd_fname : (str) the path to the background file being added
        """
        self.bkgds.append(bkgd_fname)
        
    def add_sample(self, sample_fname):
        """
        Adds a sample file to this spectrum's list of samples
        
        sample_fname : (str) the path to the background file being added
        """
        self.sample.append(sample_fname)
        
    def remove_bkgd(self, bkgd_name):
        """
        Removes a background from this spectrum's list of backgrounds
        
        bkgd_name : (str) the name of the background being removed
        """
        return None
        
    def remove_sample(self, sample_name):
        """
        Removes a sample from this spectrum's list of samples
        
        sample_name : (str) the name of the spectrum being removed
        """
        return None
        
    def flip_visibility(self):
        """
        Changes the visibility of the spectrum when plotting. If 
        the self.visible parameter is false, the plot_absorbance
        function will skip plotting this spectrum.
        """
        if self.visible:
            self.visible = False
        else:
            self.visible = True
            
    def change_offset(self, offset):
        """
        Gives the spectrum an offset value. When plotted in the 
        plot_absorbance function, the offset value will simply be
        added to the spectrum's absorbance values. This allows the
        user to vertically shift the spectrum if needed.
        
        offset : (float) the offset for the spectrum, in absorbance
                 units
        """
        self.offset = offset
        
        
    def change_color(self, new_color):
        """
        """
        self.color = new_color
            
            
def plot_absorbance(spectra, xlim=None, ylim=None):
    """
    Takes spectra and plots them, with absorbance on the y axis and
    wavelength in nanometers on the x axis.
    
    spectra : (list) a list of Spectrum objects. See Spectrum class
              in this file.
    xlim : (tuple) the x limits of the graph. This should be a tuple
           containing two float values, in nanometer units.
    ylim : (tuple) the y limits of the graph. This should be a tuple
           containing two float values, in absorbance units.
    """
    
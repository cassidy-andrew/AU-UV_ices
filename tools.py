import numpy as np
import pandas as pd

from sys import float_info

import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.ticker import FormatStrFormatter

import scipy.constants as constants
from scipy.optimize import curve_fit


def scattering_baseline(wl, a, b, c):
    """
    The rayleigh scattering baseline, as outlined in equation 11 of 
    Ioppolo et al. 2021: https://doi.org/10.1051/0004-6361/202039184
    """
    return c*np.log(1/(1-a*(wl**-4))) + b

def preventDivisionByZero(some_array):
    """
    Function to prevent zero values in an array. It does so by replacing
    zero values in the input array by a very small value close to zero.
    """
    corrected_array = some_array.copy()
    for i, entry in enumerate(some_array):
        # If element is zero, set to some small value
        if abs(entry) < float_info.epsilon:
            corrected_array[i] = float_info.epsilon
    
    return corrected_array

def WLtoE(wl):
    """
    Converting wavelength (nm) to energy (eV). Takes parameter wl, which is
    some array of wavelength values in nanometers.
    """
    # Prevent division by zero error
    wl = preventDivisionByZero(wl)

    # E = h*c/wl            
    h = constants.h         # Planck constant
    c = constants.c         # Speed of light
    J_eV = constants.e      # Joule-electronvolt relationship
    
    wl_nm = wl * 10**(-9)   # convert wl from nm to m
    E_J = (h*c) / wl_nm     # energy in units of J
    E_eV = E_J / J_eV       # energy in units of eV
    
    return E_eV  

def EtoWL(E):
    """
    Converting energy (eV) to wavelength (nm). Takes parameter E, which is
    some array of energy values in electron volts.
    """
    # Prevent division by zero error
    E = preventDivisionByZero(E)
    
    # Calculates the wavelength in nm
    return constants.h * constants.c / (constants.e * E) * 10**9


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
        
        baseline_p : (list) parameters from the fit of the rayleigh scattering
                     baseline. None until subtract_baseline() has been run.
        bkgds : (list) a list of background files that make up the scans.
        color : (str) the hex color used for plotting this spectrum.
        data : (pandas.DataFrame) the data belonging to this
               spectrum, averaged together from its corresponding
               scans.
        fit : (dict) The fitted spectrum after calling `fit_peaks()`.
        name : (str) the name of this spectrum, which will be shown
               in plot legends.
        offset : (float) by how much the spectrum should be offset
                 in the plot_absorbance() plot, in absorbance units.
                 Defaults to 0.0.
        peaks : (list) a list of the peak positions in the spectrum. Is None
                prior to calling `fit_peaks()`.
        residuals : (pandas.DataFrame) The residuals after fitting with
                    `fit_peaks()`.
        samples : (list) a list of sample files that make up the scans.
        scans : (list) a list of SingleScan objects that will be
                averaged together to make this spectrum.
        visible : (boolean) whether the spectrum should appear in
                  the plot generated by plot_absorbance() or not.
                  Defaults to True.
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
        self.peaks = None
        self.fit = None
        self.residuals = None
        self.baseline_p = None
        
    def average_scans(self):
        """
        Averages the scans relating to this spectrum.
        """
        scans = []
        
        for i in range(0, len(self.bkgds)):
            # match backgrounds and spectra
            this_bkgd = self.bkgds[i]
            suffix = this_bkgd[-3:]
            # look for samples with a matching suffix
            samples = [s for s in self.samples if suffix in s]
            # samples is now a list, but there should only be 1 or 0 items
            if len(samples) == 0:
                this_sample = None
            else:
                this_sample = samples[0]

            # create scan objects
            this_scan = SingleScan(this_bkgd, this_sample)
            scans.append(this_scan)
            
        # average the scan objects
        data = pd.DataFrame()
        # just copy the wavelength values from the first background
        data['wavelength'] = scans[0].bkgd['wavelength']
        # calculate the average absorbance
        absorbances = []
        for scan in scans:
            absorbances.append(scan.data['absorbance'])
        averaged = pd.concat(absorbances, axis=1).mean(axis=1)
        data['absorbance'] = averaged
        
        self.scans = scans
        self.data = data
    
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
        self.samples.append(sample_fname)
        
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
        self.visible = not self.visible
            
    def change_offset(self, new_offset):
        """
        Gives the spectrum an offset value. When plotted in the 
        plot_absorbance function, the offset value will simply be
        added to the spectrum's absorbance values. This allows the
        user to vertically shift the spectrum if needed.
        
        offset : (float) the offset for the spectrum, in absorbance
                 units
        """
        self.offset = new_offset
        
        
    def change_color(self, new_color):
        """
        Changes the color used for plotting this spectrum
        """
        self.color = new_color
        
        
    def save_to_csv(self, path):
        """
        Saves the spectrum data to a csv file
        
        path : (str) the path where you want to save the file
        """
        self.data.to_csv(path, index=False)
        
    
    def subtract_baseline(self, regions, p0=None):
        """
        Performs a baseline subtraction on the spectrum.
        
        p0 : (list) initial guesses for the rayleigh scattering parameters.
        regions : (list) regions in wavelength where the spectrum should be
                  flat. This should be a list of pairs of numbers. For example,
                  [(550, 566),(585, 610)] would say that between 550 and 566 nm,
                  and between 585 and 610 nm, the spectrum should be flat. These
                  ranges will then have a line fitted to them, and that line 
                  will be subtracted from the overall spectrum.
        """
        # select the regions that will be fit
        dfs = []
        for region in regions:
            lolim = region[0]
            uplim = region[1]
            dfs.append(self.data[(self.data['wavelength'] > lolim) &
                                (self.data['wavelength'] < uplim)])
        # concat the regions into one dataframe
        fit_df = pd.concat(dfs, join="inner", ignore_index=True)
        
        # fit the dataframe with the rayleigh scattering baseline
        if "raw_absorbance" in self.data:
            """p = np.polyfit(x=fit_df['wavelength'],
                           y=fit_df['raw_absorbance'], deg=2)"""
            p, pcov = curve_fit(f=scattering_baseline,
                                xdata=fit_df['wavelength'],
                                ydata=fit_df["raw_absorbance"],
                                p0=p0)
        else:
            """p = np.polyfit(x=fit_df['wavelength'],
                           y=fit_df['absorbance'], deg=2)"""
            p, pcov = curve_fit(f=scattering_baseline,
                                xdata=fit_df['wavelength'],
                                ydata=fit_df["absorbance"],
                                p0=p0)
        self.baseline_p = p
        # fitted line
        #y = [p[0]*x**2 +p[1]*x + p[2] for x in self.data['wavelength']]
        y = scattering_baseline(self.data['wavelength'], p[0], p[1], p[2])
        self.data['baseline'] = y
        # subtract the fitted baseline
        if "raw_absorbance" in self.data:
            subtracted = [a1-a2 for a1,a2 in zip(self.data['raw_absorbance'],y)]
        else:
            subtracted = [a1-a2 for a1, a2 in zip(self.data['absorbance'], y)]
            # save the raw absorbance, and update the data
            self.data['raw_absorbance'] = self.data['absorbance']
        self.data['absorbance'] = subtracted
        
    def fit_peaks(self, verbose=False, n_guassians=None):
        """
        Finds and fits the peaks in the spectrum by fitting the spectrum with 
        some number of asymmetric Gaussian functions. The locations of the peaks
        as well as the fitted spectrum are returned, but also added to a peaks
        and fit parameter of the object.
        
        Parameters:
        
        n_gaussians : (int) the number of gaussians to fit, between 1 and 10.
                      If None (default), all numbers 1 through 10 will be tried
                      and the best fit will be returned.
        verbose : (boolean) If true, prints debug and progress statements.
                  Defaults to False.
        """
        # check if raw_absorbance exists, and the baseline substraction is done
        
        best_fit = None
        peaks = []
        residuals = None
        self.peaks = peaks
        self.fit = best_fit
        self.residuals = residuals
        
        
class StichedSpectrum(Spectrum):
    """
    Represents a stiched spectrum, so the combination of two spectra
    
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
    def __init__(self, spec1, spec2):
        """
        """
        self.data = self._stich(spec1, spec2)
        # keep the color of spec1; spec2 is added to spec1 from the user POV
        self.color = spec1.color
        # these are combined from the two spectra
        self.name = spec1.name + "-" + spec2.name
        self.samples = spec1.samples + spec2.samples
        self.scans = spec1.scans + spec2.scans
        self.bkgds = spec1.bkgds + spec2.bkgds
        # these get reset
        self.offset = 0
        self.visible = True
        
    def _stich(self, spec1, spec2):
        """
        Stiches two Spectrum objects together. The two objects should
        have overlapping data.
        """
        overlaps = []
        # find the overlapping region, which we assume is at the start of spec2
        for i in range(0, len(spec2.data)):
            # What wavelength is at this index in spec2?
            this_wl = spec2.data['wavelength'][i]
            # check to see if this wavelength is in spec1
            try:
                # j is the index in spec1 of this wavelength
                j = list(spec1.data['wavelength']).index(this_wl)
                overlaps.append({'wavelength':this_wl,
                                 'abs1':spec1.data['absorbance'][j],
                                 'abs2':spec2.data['absorbance'][i]})
            except:
                # we stop once the overlap ends
                break
        df = pd.DataFrame(overlaps)
        
        # find a stich offset to minimize the variation between them.
        # this value should just be the average difference
        diffs = [a-b for a, b in zip(df['abs1'], df['abs2'])]
        offset = sum(diffs) / len(diffs)

        # add the offset to spec2
        spec2.offset = offset
        df['abs2'] = df['abs2'] + offset
        spec2fixed = spec2.data.copy()
        spec2fixed['absorbance'] = spec2fixed['absorbance'] + offset

        # change the overlapping region to be the average of each
        df['absorbance'] = [(a1+a2)/2 for a1, a2, in zip(df['abs1'],df['abs2'])]

        # combine the dataframes
        j1 = list(spec1.data['wavelength']).index(df['wavelength'][0])
        j2 = len(df)
        new_df = pd.concat([spec1.data[:j1], df, spec2fixed[j2:]],
                           join="inner", ignore_index=True)

        return new_df


def plot_absorbance(spectra, xlim=None, ylim=None, peaks=None, plot_fit=True):
    """
    Takes spectra and plots them, with absorbance on the y axis and
    wavelength in nanometers on the x axis. Also wavelength in eV on the
    top x axis for fun.
    
    spectra : (list) a list of Spectrum objects. See Spectrum class
              in this file.
    plot_fit : (boolean) To plot the fit to the data as well as its residuals,
               if the spectra have been fitted.
    xlim : (tuple) the x limits of the graph. This should be a tuple
           containing two float values, in nanometer units.
    ylim : (tuple) the y limits of the graph. This should be a tuple
           containing two float values, in absorbance units.
    """
    plt.style.use('./au-uv.mplstyle')
    
    fig, ax1 = plt.subplots(1, 1)
    #fig.set_size_inches(7, 5)
    
    if xlim:
        ax1.set_xlim(xlim)
    if ylim:
        ax1.set_ylim(ylim)
    
    for spec in spectra:
        if spec.visible:
            ax1.plot(spec.data['wavelength'], 
                     spec.data['absorbance']+spec.offset,
                     color=spec.color, label=spec.name)
            
    # plot peak positions
    if peaks != None:
        for peak in peaks:
            ax1.axvline(x=peak[0])
            
    # Create the second x-axis on which the energy in eV will be displayed
    ax2 = ax1.secondary_xaxis('top', functions=(WLtoE, EtoWL))
    ax2.set_xlabel('Wavelength (eV)')

    # Get ticks from ax1 (wavelengths)
    wl_ticks = ax1.get_xticks()
    wl_ticks = preventDivisionByZero(wl_ticks)

    # Based on the ticks from ax1 (wavelengths), calculate the corresponding
    # energies in eV
    E_ticks = WLtoE(wl_ticks)

    # Set the ticks for ax2 (Energy)
    ax2.set_xticks(E_ticks)

    # Allow for two decimal places on ax2 (Energy)
    ax2.xaxis.set_major_formatter(FormatStrFormatter('%.2f'))

    ax1.set_ylabel("Absorbance")
    ax1.set_xlabel("Wavelength (nm)")
    ax1.grid()
    ax1.legend()
    plt.close()
    return fig

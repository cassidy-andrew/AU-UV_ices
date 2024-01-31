import numpy as np
from numpy import inf
import pandas as pd

from sys import float_info

import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.ticker import FormatStrFormatter

import scipy.constants as constants
from scipy.optimize import curve_fit

#import gaussians

def scattering(wl, m, k):
    """
    The rayleigh scattering function, as outlined in equation 11 of 
    Ioppolo et al. 2021: https://doi.org/10.1051/0004-6361/202039184
    """
    return k*np.log(1/(1-m*(wl**-4)))

def gaussian(x, a1,c1,s1):
    """
    A single gaussian function, centered at c1 with standard deviation s1, and
    amplitude a1.
    """
    return (a1/(s1*(np.sqrt(2*np.pi)))) * np.exp((-1.0/2.0)*(((x-c1)/s1)**2))

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

def lighten_color(color, amount=0.5):
    """
    Lightens the given color by multiplying (1-luminosity) by the given amount.
    Input can be matplotlib color string, hex string, or RGB tuple.
    
    Original Author: ihincks on Github
    https://gist.github.com/ihincks/6a420b599f43fcd7dbd79d56798c4e5a

    Examples:
    >> lighten_color('g', 0.3)
    >> lighten_color('#F034A3', 0.6)
    >> lighten_color((.3,.55,.1), 0.5)
    """
    import matplotlib.colors as mc
    import colorsys
    try:
        c = mc.cnames[color]
    except:
        c = color
    c = colorsys.rgb_to_hls(*mc.to_rgb(c))
    return colorsys.hls_to_rgb(c[0], 1 - amount * (1 - c[1]), c[2])


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
        fit_components : (list) a list of dictionaries which make up the fit
                         components after `fit_peaks()` is called. Each 
                         dictionary has the following components: parameters,
                         and absorbance. The `parameters` are the three values
                         which describe the gaussian: amplitude, center, and
                         standard deviation. The `absorbance` has the y values
                         of the gaussian corresponding to the `data` parameter's
                         wavelength values.
        fit_results : (dict) A dictionary of the best fit results after
                      `fit_peaks()` is called. It consists of the following
                      components: redchi2, p, pcov, best_fit. `redchi2` is the
                      reduced chi square value of the fit. `p` is the fit
                      parameters. `pcov` is the covariance matrix of those
                      parameters. `best_fit` are the absorbance values
                      calculated to fit the data.
        name : (str) the name of this spectrum, which will be shown
               in plot legends.
        offset : (float) by how much the spectrum should be offset
                 in the plot_absorbance() plot, in absorbance units.
                 Defaults to 0.0.
        peaks : (list) a list of the peak positions in the spectrum. Is None
                prior to calling `fit_peaks()`.
        peak_errors : (list) a list of the standard deviation peak errors. Is
                      None prior to calling `fit_peaks()`
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
        self.baseline_p = None
        self.peaks = None
        self.peak_errors = None
        self.fit_components = []
        self.fit_results = None
        self._comps = None
        
    def average_scans(self):
        """
        Averages the scans relating to this spectrum.
        """
        scans = []
        
        # pair backgrounds and samples into SingleScan objects
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
            
        # average the SingleScan objects
        # make a dataframe to put the averaged data in
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
        
        
    def export(self, path):
        """
        Saves the spectrum object. Its data will be saved to a csv file.
        
        path : (str) the path where you want to save the file. This should be a
               directory.
        """
        self.data.to_csv(path+"/data.csv", index=False)
        
    
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
        
    def _fit_function(self, x, *P):
        """
        
        """
        # y will hold our spectrum
        y = np.zeros(len(x))
        
        # initialize our parameter space. At this point, P contains all
        # parameters for all components of the fit. We need to sort them out.
        # parameters relating to custom components are first
        if self._comps is not None:
            self._n_comps = len(self._comps)
        else:
            self._n_comps = 0
        # parameters relating to scattering are second
        if self._do_scattering:
            self._n_scatt = 2
        else:
            self._n_scatt = 0
        # remaining parameters are relating to the gaussians. We make new lists
        # for the parameters below:        
        # parameters relating to our custom components
        C = P[:self._n_comps]
        # parameters relating to our scattering
        S = P[self._n_comps:self._n_comps+self._n_scatt]
        # parameters realting to our gaussians
        G = P[self._n_comps+self._n_scatt:]
        
        # add the custom components terms to our y values
        if self._do_comps:
            y += sum([c*comp['absorbance'] for c, comp in zip(C, self._comps)])
            
        # add the scattering terms to our y values
        if self._do_scattering:
            y += scattering(x, *S)
        
        # add the gaussian terms to our y values
        n_gaussians = len(G) // 3
        # splits all gaussian parameters B into lists of 3 parameters
        gauss_guesses = [G[i*3:(i+1)*3] for i in range((len(G)+3-1)//3)]
        for gguess in gauss_guesses:
            y += gaussian(x, *gguess)
            
        return y
        
    def fit_peaks(self, verbose=False, guesses=None, ng_lower=1, ng_upper=7,
                  do_scattering=False, fit_lim=(120, 340), custom_components=None):
        """
        Finds and fits the peaks in the spectrum by fitting the spectrum with 
        some number of asymmetric Gaussian functions. The locations of the peaks
        as well as the fitted spectrum are returned, but also added to a peaks
        and fit parameter of the object. The best fit is saved as a column in
        the spectrum's `data` DataFrame parameter.
        
        Parameters:
        
        do_scattering : (boolean) Whether or not to fit using the rayleigh
                      scattering function as a part of the fit.
        fit_lim_low : (float) the lower limit on the wavelength range used in
                      fitting. Defults to 120.
        guesses: (list) a list of dictionaries containing the guesses to your
                 fit. The dictionaries must be of the form: {'lower':, 'guess':,
                 'upper':} where 'guess' is your guess for the value of a fit
                 parameter, and 'lower' and 'upper' are lower and upper limits
                 respectively. Guesses for gaussian fit parameters must be in
                 groups of three; a, c, and s, where a is the amplitude of the
                 gaussian, c is the center wavelength, and s is the standard
                 deviation. If you have `do_baseline` to True, you should
                 include an additional two parameters *at the start* of p0.
                 These parameters are m and k, where m controls the steepness of
                 the scattering curve, and k controls the amplitude. If you have
                 any custom components, you must include guesses for the
                 amplitudes of those components at the start of the list, before
                 your guesses for the baseline.
        ng_lower : (int) The lower limit on the number of gaussians to try and
                   fit with. Defaults to 1.
        ng_upper : (int) The upper limit on the number of gaussians to try and
                   fit with. Defaults to 7. Higher numbers will take longer and
                   may be unstable.
        verbose : (boolean) If true, prints debug and progress statements.
                  Defaults to False.
        """
        # we only want to fit where the data are good
        fit_df = self.data[(self.data['wavelength'] > fit_lim[0]) &
                           (self.data['wavelength'] < fit_lim[1])].copy()
        #self.fit_df = fit_df
        # do the fit
        # this method is computationally expensive and bad. It will be fixed in
        # the future... :/
        
        if not guesses:
            print("you must provide guesses!! >:O")
            return None
            
        # unwrap guesses and bounds
        p0 = []
        lower_bounds = []
        upper_bounds = []
        for guess in guesses:
            p0.append(guess['guess'])
            lower_bounds.append(guess['lower'])
            upper_bounds.append(guess['upper'])
        bounds = (lower_bounds, upper_bounds)

        # check if we are fitting the rayleigh scattering or not
        if do_scattering:
            self._do_scattering = True
            # if we are doing the baseline, there are 2 extra parameters
            # we need to modify our indices in some places by 2
            #ib = 2
            self._n_scatt = 2
        else:
            self._do_scattering = False
            #ib = 0
            self._n_scatt = 0
            
        # initialize the function based on what custom components we are using
        errors = []
        if custom_components is not None:
            self._comps = []
            self._do_comps = True
            for comp in custom_components:
                self._comps.append(comp[(comp['wavelength'] > fit_lim[0]) &
                                   (comp['wavelength'] < fit_lim[1])].copy())
            #ib = len(self._comps)
            self._n_comps = len(self._comps)
            if not p0:
                errors.append("You must provide your own guesses" +
                              " if you are using custom components!!!! >:O")
            if len(errors) > 0:
                for error in errors:
                    print(error)
                return None
        else:
            self._comps = None
            self._do_comps = False
            self._n_comps = 0

        # a place to store our fit results
        fit_results = []
        # do the fitting with different numbers of gaussians
        for n in range(ng_lower, ng_upper):
            if verbose:
                print("Attempting fit with {0} gaussians".format(n))
            #try:
            """if bounds is None:
                these_bounds = (0, 340)
            else:
                these_bounds = (bounds[0][:ib+n*3], bounds[1][:ib+n*3])
                #print(these_bounds)"""
            these_p0 = p0[:self._n_comps+self._n_scatt+n*3]
            these_bounds = (bounds[0][:self._n_comps+self._n_scatt+n*3],
                            bounds[1][:self._n_comps+self._n_scatt+n*3])
            #print(these_p0)
            #print(these_bounds)
            p, pcov = curve_fit(f=self._fit_function,
                                xdata=fit_df['wavelength'], 
                            ydata=fit_df["absorbance"]+self.offset,
                            p0=these_p0, bounds=these_bounds)
            best_fit = self._fit_function(fit_df['wavelength'], *p)
            redchi2 = (((best_fit-fit_df['absorbance'])**2)
                       /best_fit).sum() / (len(p))
            fit_results.append({'redchi2':redchi2, 'n':n,
                                'best_fit':best_fit, 'p':p, 'pcov':pcov})
            if verbose:
                print("success! reduced chi2: {0:.2f}".format(redchi2))
            #except:
            #    continue
                
        # evaluate which of our fits was best, based on the reduced chi square
        best_chi2 = 1000
        best_i = 0
        for i in range(0, len(fit_results)):
            this_diff = np.abs(1-fit_results[i]['redchi2'])
            best_diff = np.abs(1-best_chi2)
            if this_diff < best_diff:
                #if fit_results[i]['redchi2'] < best_chi2:
                best_i = i
                best_chi2 = fit_results[i]['redchi2']

        if verbose:
            print("The best fit was achieved with " +
                  "{0}".format(fit_results[best_i]['n']) +
                  " gaussians and a reduced chi2 of"+
                  " {0:.2f}".format(fit_results[best_i]['redchi2']))
        
        # manage the fit parameters in a different function to avoid bloat
        #print(fit_results[best_i])
        self._manage_fit_parameters(fit_results[best_i], fit_df)
            
    def _manage_fit_parameters(self, fit_result, fit_df):
        """
        Takes the fit results from the fitting function, and organizes them in
        a way the user will want to interact with. Assigns those results to
        object parameters which can easily be exported later.
        """
        # Take care of adding the absorbance and residual values to self.data.
        # self.data has a different wavelength range than our fitted absorbance
        # values. But fit_df does not. So, add the fitted absorbance to fit_df
        # and then merge fit_df into self.data so that the wavelengths line up.
        fit_df['best_fit'] = fit_result['best_fit']
        # add the best fit to self.data, but if it already exists
        # get rid of it first.
        if 'best_fit' in self.data:
            self.data = self.data.drop(columns=['best_fit'])
        self.data = self.data.merge(fit_df, how='left')
        # un-offset the fit, to match self.data['absorbance'] and give accurate
        # residuals
        self.data['best_fit'] = self.data['best_fit'] - self.offset
        # calculate residuals
        self.data['residuals'] = self.data['absorbance']-self.data['best_fit']
        
        #self.fit_results = fit_result
        # we will use these to calculate our peaks later
        p = fit_result['p']
        pcov = fit_result['pcov']
        perr = np.sqrt(np.diag(pcov))
        
        # make a list of all the parameters an their errors
        all_params = []
        for i in range(0, len(p)):
            all_params.append({'value':p[i], 'error':perr[i]})
        
        # parameters relating to our custom components
        C = all_params[:self._n_comps]
        # parameters relating to our scattering
        S = all_params[self._n_comps:self._n_comps+self._n_scatt]
        # parameters realting to our gaussians
        G = all_params[self._n_comps+self._n_scatt:]
        
        # Extract the guassian peak positions and their errors. 
        peaks = []
        for i in range(1, len(G), 3):
            peaks.append({'peak':G[i]['value'], 'peak_error':G[i]['error']})

        self.peaks = peaks
        
        # save the general fit results
        self.fit_results = {'reduced_chi_square':fit_result['redchi2'],
                            'n_gaussians':fit_result['n'],
                            'n_custom_components':self._n_comps,
                            'fitted_scattering':self._do_scattering,
                            'custom_component_parameters':C,
                            'scattering_parameters':S,
                            'gaussian_parameters':G,
                            'p':p,
                            'pcov':pcov}
        
        # save the individual components that make up the fit
        self.fit_components = []
        # handle the custom components
        if self._do_comps:
            for i in range(0, self._n_comps):
                this_comp = self._comps[i]
                this_ab = [C[i]['value']*ab for ab in this_comp['absorbance']]
                self.fit_components.append({'parameters':C[i],
                                        'wavelength':this_comp['wavelength'],
                                        'absorbance':this_ab})
        # handle the scattering
        if self._do_scattering:
            self.fit_components.append({'parameters':S,
                                        'wavelength':self.data['wavelength'],
                                        'absorbance':scattering(x,S[0]['value'],
                                                                S[1]['value'])})
        # handle the gaussians
        ps = [G[i*3:(i+1)*3] for i in range((len(G)+3-1)//3)]
        for params in ps:
            # each item in ps is a list of three numbers, for one gaussian
            values = []
            for parameter in params:
                values.append(parameter['value'])
            this_gaussian = gaussian(self.data['wavelength'], *values)
            self.fit_components.append({'parameters':params,
                                        'wavelength':self.data['wavelength'],
                                        'absorbance':this_gaussian-self.offset})
        
        
        
class StitchedSpectrum(Spectrum):
    """
    Represents a stitched spectrum, so the combination of two spectra
    
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
    
def plot_fit(spec, xlim=None, ylim=None, plot_peaks=False,
             plot_fit_components=True, figsize=(7,5), fig=None, ax1=None,
             save_path=None, plot_residuals=True, res_lims=(-0.0075, 0.0075)):
    """
    Takes a single spectrum which has been fit using the `fit_peaks()` function,
    and plots the results of the fit, with absorbance on the y axis and
    wavelength in nanometers on the x axis.
    
    plot_fit_components : (boolean)
    plot_peaks : (boolean) whether or not to plot vertical lines at the centers
                 of the fitted peaks. Defaults to False.
    spec : (Spectrum or StichedSpectrum) The fited spectrum to be plotted.
    xlim : (tuple) the x limits of the graph. This should be a tuple
           containing two float values, in nanometer units.
    ylim : (tuple) the y limits of the graph. This should be a tuple
           containing two float values, in absorbance units.
    """
    plt.style.use('./au-uv.mplstyle')
    
    # make sure the passed spectrum has been fit
    if spec.peaks is None:
        print("The spectrum you passed hasn't been fit yet!")
        return None
    
    # setup the axes
    if plot_residuals:
        fig, ax = plt.subplots(2, 1, gridspec_kw={'height_ratios': [3, 1]},
                               sharex=True)
        ax1 = ax[0]
        axr = ax[1]
        
    if ax1 is None:
        fig, ax1 = plt.subplots(1, 1)
        fig.set_size_inches(figsize[0], figsize[1])
    
    if xlim:
        ax1.set_xlim(xlim)
    if ylim:
        ax1.set_ylim(ylim)
        
    # plot the data
    ax1.plot(spec.data['wavelength'], spec.data['absorbance']+spec.offset,
             color=spec.color, label=spec.name)
    # calculate a color for the fit
    fit_color = lighten_color(spec.color, amount=1.2)
    # plot the fit
    ax1.plot(spec.data['wavelength'], spec.data['best_fit']+spec.offset,
             color=fit_color, linestyle='--', label=spec.name+" Best Fit")
    # plot the peaks as vertical lines if desired
    if plot_peaks:
        for peak in spec.peaks:
            ax1.axvline(peak['peak'], linestyle='-.',
                       color=lighten_color(spec.color, amount=1.1))
    # plot shaded gaussian fit components if desired
    if plot_fit_components:
        for component in spec.fit_components:
            ax1.plot(component['wavelength'],
                     [spec.offset+c for c in component['absorbance']],
                     color='xkcd:grey', linestyle='-')
            ax1.fill_between(component['wavelength'], 0,
                             [spec.offset+c for c in component['absorbance']],
                             color='xkcd:grey', alpha=.2)
            
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
    if plot_residuals:
        axr.set_xlabel("Wavelength (nm)")
        axr.plot(spec.data['wavelength'], spec.data['residuals'],
                 color=spec.color, label='Residuals')
        if spec.data['residuals'].min() <= 0:
            rymin = spec.data['residuals'].min()*1.4
        else:
            rymin = spec.data['residuals'].min()*0.6
        if spec.data['residuals'].max() <= 0:
            rymax = spec.data['residuals'].max()*0.6
        else:
            rymax = spec.data['residuals'].max()*1.4
        axr.set_ylim(rymin, rymax)
        axr.legend()
        if res_lims is not None:
            axr.set_ylim(res_lims[0], res_lims[1])
        
    #ax1.grid()
    ax1.legend()
    
    fig.tight_layout()
    fig.subplots_adjust(hspace=0.1)
    
    if save_path:
        plt.savefig(save_path, bbox_inches='tight')

    return ax1, axr


def plot_absorbance(spectra, xlim=None, ylim=None, peaks=None, plot_fit=False,
                    plot_peaks=False, plot_fit_components=False, figsize=(7,5),
                    raw=False, fig=None, ax1=None, save_path=None):
    """
    Takes spectra and plots them, with absorbance on the y axis and
    wavelength in nanometers on the x axis. Also wavelength in eV on the
    top x axis for fun.
    
    spectra : (list) a list of Spectrum objects. See Spectrum class
              in this file.
    plot_fit : (boolean) To plot the fit to the data as well as its residuals,
               if the spectra have been fitted.
    raw : (boolean) If True, plots the raw data instead of the calibrated data.
          Defaults to False.
    xlim : (tuple) the x limits of the graph. This should be a tuple
           containing two float values, in nanometer units.
    ylim : (tuple) the y limits of the graph. This should be a tuple
           containing two float values, in absorbance units.
    """
    plt.style.use('./au-uv.mplstyle')
    
    if ax1 is None:
        fig, ax1 = plt.subplots(1, 1)
        fig.set_size_inches(figsize[0], figsize[1])
    
    if xlim:
        ax1.set_xlim(xlim)
    if ylim:
        ax1.set_ylim(ylim)
    
    for spec in spectra:
        if spec.visible:
            if raw:
                ax1.plot(spec.data['wavelength'], 
                         spec.data['raw_absorbance']+spec.offset,
                         color=spec.color, label=spec.name)
            else:
                ax1.plot(spec.data['wavelength'], 
                         spec.data['absorbance']+spec.offset,
                         color=spec.color, label=spec.name)
        if plot_fit:
            ax1.plot(spec.data['wavelength'],
                     spec.data['best_fit']+spec.offset,
                     color=lighten_color(spec.color, amount=1.2),
                     linestyle='--', label=spec.name+" Best Fit")
        if plot_peaks:
            for peak in spec.peaks:
                ax1.axvline(peak, linestyle='-.',
                           color=lighten_color(spec.color, amount=1.1))
        if plot_fit_components:
            for component in spec.fit_components:
                ax1.plot(spec.data['wavelength'],
                         component['absorbance']+spec.offset,
                         color='xkcd:grey', linestyle='-')
                ax1.fill_between(spec.data['wavelength'], 0,
                                 component['absorbance']+spec.offset,
                                 color='xkcd:grey', alpha=.2)

            
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
    #ax1.grid()
    ax1.legend()
    
    if save_path:
        plt.savefig(save_path, bbox_inches='tight')

    return ax1

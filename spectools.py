import numpy as np
from numpy import inf
import pandas as pd
from datetime import datetime

import warnings
from sys import float_info

import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.ticker import FormatStrFormatter
import matplotlib.ticker as ticker
from matplotlib.ticker import AutoMinorLocator
from matplotlib.legend import _get_legend_handles_labels as get_handles

import scipy.constants as constants
from scipy.optimize import curve_fit


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
    Represents a single scan.
    """
    def __init__(self, fname, df=None, debug=False):
        self.debug = debug
        self.name = fname[fname.rfind("/")+1:]
        self.fname = fname
        if df is None:
            self.data = self._setup_scan(fname)
        else:
            self.data = df
        # initialize color
        self.lenccycle = 10
        self.cmap = plt.cm.rainbow(np.linspace(0, 1, self.lenccycle))
        self.cindex = np.random.randint(0, self.lenccycle)
        self.color = mpl.colors.rgb2hex(self.cmap[self.cindex])
        self.visible = True

    def _setup_scan(self, fname):
        """
        Reads the raw data files and formats them correctly, adding necessary
        columns and unit conversions.
        
        fname : (str) the path to the file for this scan
        """
        column_names = ['Lambda', 'Keith/nA', 'Ch1/volts',
                        'Ch2/volts', 'Ch3/volts', 'Z_Motor','Beam_current',
                        'temperature', 'GC_Pres', 'Time', 'UBX_x', 'UBX_y']
    
        # read the data
        scan = pd.read_csv(fname, header=[15], delimiter=r"\s+")
        scan.columns = column_names
        # do some calculations
        scan['nor_signal'] = ((180/scan['Beam_current']) * scan['Keith/nA'])
        scan['wavelength'] = scan['Lambda']
        scan['av_signal'] = (scan['nor_signal'] + scan['nor_signal'])/2
        
        return(scan)

    def cycle_color(self):
        """
        Changes the color based on a color cycle
        """
        old_color = self.color
        if self.cindex == self.lenccycle-1:
            self.cindex = 0
        else:
            self.cindex += 1
        self.color = mpl.colors.rgb2hex(self.cmap[self.cindex])

    def flip_visibility(self):
        """
        Changes the visibility of the scan when plotting. If 
        the self.visible parameter is false, the plot_absorbance
        function will skip plotting this spectrum.
        """
        self.visible = not self.visible

        
class Spectrum:
    """
    Represents a spectrum, so the average of one or more scans
    
    Parameters belonging to the fully constructed object:
        
        baseline_p : (list) parameters from the fit of the rayleigh scattering
                     baseline. None until subtract_baseline() has been run.
        bkgd : (pandas.DataFrame) The averaged background data.
        bkgd_files : (list) a list of background files that make up the scans.
        changelog : (str) a string which contains the history of the data. Every
                    time a function is called, a line is written to describe
                    what happened and at what time. This is then added to the
                    header of a file during export.
        cindex : (int) the index of the current position in the color cycle for
                 color cycling.
        color : (str) the hex color used for plotting this spectrum.
        data : (pandas.DataFrame) the data belonging to this
               spectrum, averaged together from its corresponding
               scans.
        debug : (boolean) whether or not to run the functions of this Specturm
                in debug mode, where additional information is printed to the
                console as attributes are changed.
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
        linestyle : (str) the linestyle for matplotlib plotting.
        linewidth: (int) the line width for matplotlib plotting.
        name : (str) the name of this spectrum, which will be shown
               in plot legends.
        offset : (float) by how much the spectrum should be offset
                 in the plot_absorbance() plot, in absorbance units.
                 Defaults to 0.0.
        peaks : (list) a list of the peak positions in the spectrum. Is None
                prior to calling `fit_peaks()`.
        peak_errors : (list) a list of the standard deviation peak errors. Is
                      None prior to calling `fit_peaks()`
        sample : (pandas.DataFrame) The averaged sample data.
        sample_files : (list) a list of sample files that make up the scans.
        scans : (list) a list of SingleScan objects that will be
                averaged together to make this spectrum.
        visible : (boolean) whether the spectrum should appear in
                  the plot generated by plot_absorbance() or not.
                  Defaults to True.
    """
    def __init__(self, debug=False):
        """                
        """
        # declare parameters
        self.debug=debug
        self.changelog = ""
        self.description = ""
        self.name = ""
        self.oldname = ""
        # give default color
        self.lenccycle = 10 # length of the color cycle
        self.cmap = plt.cm.rainbow(np.linspace(0, 1, self.lenccycle))
        self.cindex = np.random.randint(0, self.lenccycle)
        self.color = mpl.colors.rgb2hex(self.cmap[self.cindex])
        # plotting parameters (alliteration yay)
        self.linestyle = 'solid'
        self.linewidth = 2
        self.visible = True
        self.offset = 0.0
        # data parameters
        self.bkgds = []
        self.samples = []
        self.data = None
        # fitting parameters
        self.baseline_p = None
        self.peaks = None
        self.peak_errors = None
        self.fit_components = []
        self.fit_results = None
        self._comps = None

        # note that this object was made, and with what time (done in _log)
        self._log(f"initialized spectrum with debug={self.debug}")

    def _fit_function(self, x, *P):
        """
        The fit function. It is a linear combination of several optional
        components: custom components which can be any array-like object, a 
        rayleigh scattering term, and any number of gaussian functions. The
        number of gaussian functions is determined by the number of parameters
        passed to the function. Passed parameters must be in the order of: 
        scale factors for the custom components, parameters for the scattering
        function, and parameters for the gaussians. 
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

    def _log(self, message):
        """
        Log a change to the object. Write the message to the changelog, and
        print the message to the terminal if debug is true.
        """
        now = datetime.now()
        current_time = now.strftime("%d-%m-%Y %H:%M:%S")
        self.changelog += current_time + " " + message + "\n"
        if self.debug:
            # printed message specifies which spectrum we are dealing with
            print(current_time + " Spectrum " + self.oldname + " " + message)
            self.oldname = self.name

    def _make_guesses(self, ng_upper, wavelengths):
        """
        Generate guesses for fit parameters if none are provided. Custom
        component scale values will be initialized to 1. Scattering parameters
        will be k=1, m=1. Gaussians will have amplitude 1, standard deviation 5,
        and central positions evenly distributed in wavelength space.
        """
        guesses = []
        # handle custom components
        if self._do_comps:
            for n in range(0, self._n_comps):
                guesses.append({'lower':0, 'guess':1, 'upper':np.inf})
                
        if self._do_scattering:
            guesses.append({'lower':0, 'guess':1, 'upper':np.inf}) # m
            guesses.append({'lower':0, 'guess':1, 'upper':np.inf}) # k
            
        centers = np.linspace(wavelengths.iloc[0],wavelengths.iloc[-1],ng_upper)
        for n in range(0, ng_upper):
            # amplitude
            guesses.append({'lower':0, 'guess':1, 'upper':np.inf}) 
            # center
            guesses.append({'lower':0, 'guess':centers[n], 'upper':np.inf})
            # standard deviation
            guesses.append({'lower':0, 'guess':5, 'upper':np.inf})
            
        return guesses

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
        for i in range(0, len(G), 3):
            G[i]['parameter'] = 'amplitude'
            G[i+1]['parameter'] = 'center'
            G[i+2]['parameter'] = 'std'
            peaks.append({'peak':G[i+1]['value'], 'peak_error':G[i+1]['error']})

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
            self.fit_components.append({
                'parameters':S,
                'wavelength':self.data['wavelength'],
                'absorbance':scattering(self.data['wavelength'],
                                        S[0]['value'],
                                        S[1]['value'])
            })
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

    def add_bkgd(self, bkgd_fname):
        """
        Adds a background file to this spectrum's list of backgrounds
        
        bkgd_fname : (str) the path to the background file being added
        """
        this_bkgd = SingleScan(bkgd_fname)
        self.bkgds.append(this_bkgd)
        self._log(f'added bkgd file {bkgd_fname}')
        return this_bkgd
        
    def add_sample(self, sample_fname):
        """
        Adds a sample file to this spectrum's list of samples
        
        sample_fname : (str) the path to the background file being added
        """
        this_sample = SingleScan(sample_fname)
        self.samples.append(this_sample)
        self._log(f'added sample file {sample_fname}')
        return this_sample

    def average_scans(self):
        """
        Averages the scans relating to this spectrum. First all backgrounds are
        averaged together. Then all samples are averaged together. Then the
        absorbance is calculated, taking the base 10 log of the ratio of the
        background and scan signal. The result is put in a pandas dataframe and
        stored in the .data parameter.
        """
        scans = []
        self._log("began scan averaging")
        
        # handle the backgrounds
        bkgd_dfs = []
        for bkgd in self.bkgds:
            bkgd_dfs.append(bkgd.data)
        # average the backgrounds together
        self.bkgd = pd.concat(bkgd_dfs).reset_index().groupby("index").mean(numeric_only=True)

        self._log("finished background processing")
        
        # handle the samples
        sample_dfs = []
        #self.samples = []
        if len(self.samples) == 0:
            # if there is no sample just set everything to zeros.
            sample_df = self.bkgd.copy(deep=True)
            sample_df['wavelength'] = sample_df['Lambda']
            sample_df['nor_signal'] = np.zeros(len(sample_df['wavelength']))
            sample_df['av_signal'] = np.zeros(len(sample_df['wavelength']))
            sample_dfs.append(sample_df)
            self.samples.append(SingleScan("none", df=sample_df))
        else:
            for sample in self.samples:
                sample_dfs.append(sample.data)
        # average the samples together
        self.sample = pd.concat(sample_dfs).reset_index().groupby("index").mean(numeric_only=True)

        self._log("finished sample processing")

        # a place for the calibrated data to go
        df = pd.DataFrame()
        df = df.astype('int32')

        if (self.sample['av_signal'] == 0).all():
            # if there was no sample signal, set everything to zero
            df['absorbance'] = self.sample['av_signal']
        else:
            # otherwise, calculate absorbance,
            # making sure not to take a log of -ve numbers
            ratio1 = self.bkgd['av_signal'] / self.sample['av_signal']
            df['absorbance'] = np.log10(ratio1, where=(np.array(ratio1)>0))

        df['wavelength'] = self.bkgd['wavelength']

        self.data = df
        self._log(f"finished absorbance calculation using {len(bkgd_dfs)} " +
                  f"bkgds and {len(sample_dfs)} samples")

    def change_color(self, new_color):
        """
        Changes the color used for plotting this spectrum
        """
        old_color = self.color
        self.color = new_color
        self._log(f'changed color from {old_color} to {self.color}')

    def change_index(self, new_index):
        """
        Changes the index of this spectrum for use in the DUVET GUI
        
        new_index : (int) the new index for this spectrum
        """
        self.index = new_index
        
    def change_linestyle(self, new_style):
        """
        Changes the linestyle of this spectrum
        
        new_style : (str) the matplotlib linestyle for this spectrum
        """
        old_style = self.linestyle
        self.linestyle = new_style
        self._log(f'linestyle changed from {old_style} '+f'to {self.linestyle}')

    def change_linewidth(self, new_width):
        """
        Changes the line width of this spectrum
        
        new_linewidth : (int) the matplotlib line width for this
                            spectrum
        """
        old_width = self.linewidth
        self.linewidth = new_width
        self._log(f'linewidth changed from {old_width} '+f'to {self.linewidth}')

    def change_name(self, new_name):
        """
        Changes the name of this spectrum
        
        new_name : (str) the new name for this spectrum
        """
        self.oldname = self.name
        self.name = new_name
        self._log(f'changed name to {self.name}')

    def change_offset(self, new_offset):
        """
        Gives the spectrum an offset value. When plotted in the 
        plot_absorbance function, the offset value will simply be
        added to the spectrum's absorbance values. This allows the
        user to vertically shift the spectrum if needed.
        
        offset : (float) the offset for the spectrum, in absorbance
                 units
        """
        old_offset = self.offset
        self.offset = new_offset
        self._log(f'changed offset from {old_offset} to '+ f'{self.offset}')        

    def cycle_color(self):
        """
        Changes the color based on a color cycle
        """
        old_color = self.color
        if self.cindex == self.lenccycle-1:
            self.cindex = 0
        else:
            self.cindex += 1
        self.color = mpl.colors.rgb2hex(self.cmap[self.cindex])
        self._log(f'changed color from {old_color} to {self.color}')        

    def export(self, path=None):
        """
        Export the data and attributes
        """
        if self.description == "":
            print(f"You must provide a description to spectrum {self.name} " +
                  "before you may export its data! You can do this with the " +
                  "Spectrum.update_description() function.")
            return None

        if path is None:
            path = f"./{self.name}.txt"

        print(f"path after check {path}")
            
        self._log(f"began data export to file {path}")

        bkgd_files = []
        for bkgd in self.bkgds:
            bkgd_files.append(bkgd.fname)
        sample_files = []
        for sample in self.samples:
            sample_files.append(sample.fname)
        
        with open(path, "w") as f:
            f.write("#----------------------------------------------------\n")
            f.write("# Spectrum Description\n")
            f.write("#----------------------------------------------------\n")
            f.write(f"Name: {self.name}\n")
            f.write("\n")
            f.write(f"{self.description}\n")
            f.write("\n")
            f.write(f"Background Files: {bkgd_files}\n")
            f.write(f"Sample Files: {sample_files}\n")
            f.write("\n")
            f.write("#----------------------------------------------------\n")
            f.write("# Object and Plotting Attributes\n")
            f.write("#----------------------------------------------------\n")
            f.write(f"Debug: {self.debug}\n")
            f.write(f"Offset: {self.offset}\n")
            f.write(f"Visible: {self.visible}\n")
            f.write(f"Color: {self.color}\n")
            #f.write(f"Color Index: {self.cindex}\n")
            f.write(f"Linestyle: {self.linestyle}\n")
            f.write(f"Linewidth: {self.linewidth}\n")
            f.write("\n")
            f.write("#----------------------------------------------------\n")
            f.write("# Fit Parameters\n")
            f.write("#----------------------------------------------------\n")
            f.write(f"Baseline parameters: {self.baseline_p}\n")
            f.write(f"Peak positions: {self.peaks}\n")
            f.write(f"Peak errors: {self.peak_errors}\n")
            f.write(f"Fit results: {self.fit_results}\n")
            f.write("\n")
            f.write("#----------------------------------------------------\n")
            f.write("# Changelog\n")
            f.write("#----------------------------------------------------\n")
            f.write(self.changelog)
            f.write("\n")
            f.write("#----------------------------------------------------\n")
            f.write("# Spectroscopic Data\n")
            f.write("#----------------------------------------------------\n")
            if self.data is not None:
                self.data.to_csv(f, index=False, header=True)

    def fit_peaks(self, verbose=False, guesses=None, ng=None,
                  ng_lower=None, ng_upper=None, do_scattering=False,
                  fit_lim=(120, 340), custom_components=None):
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
        ng : (tuple or int) The number of gaussians to use in the fit, or lower
             and upper limits on how many gaussians to use in the fit.
        ng_lower : (int) [Depreciated] The lower limit on the number of
                   gaussians to try and fit with.
        ng_upper : (int) [Depreciated] The upper limit on the number of
                   gaussians to try and fit with.
        verbose : (boolean) If true, prints debug and progress statements.
                  Defaults to False.
        """
        self._log("initializing fitting procuedure with fit limits " +
                  f"{fit_lim[0]} and {fit_lim[1]} nm")
        
        # we only want to fit where the data are good
        fit_df = self.data[(self.data['wavelength'] > fit_lim[0]) &
                           (self.data['wavelength'] < fit_lim[1])].copy()

        # check if we are fitting the rayleigh scattering or not
        if do_scattering:
            self._do_scattering = True
            # if we are doing the baseline, there are 2 extra parameters
            # we need to modify our indices in some places by 2
            #ib = 2
            self._n_scatt = 2
            self._log("scattering baseline will be included in the fit")
        else:
            self._do_scattering = False
            #ib = 0
            self._n_scatt = 0
            self._log("scattering baseline will not be included in the fit")
            
        # check if we are using custom components and if so, format them
        #errors = []
        if custom_components is not None:
            self._comps = []
            self._do_comps = True
            for comp in custom_components:
                # cut to the desired region
                this_comp = comp[(comp['wavelength'] > fit_lim[0]) &
                                 (comp['wavelength'] < fit_lim[1])].copy()
                
                # do we need to interpolate?
                if len(this_comp['wavelength']) == len(fit_df['wavelength']):
                    # no, continue as normal
                    fit_comp = this_comp
                    pass
                else:
                    # yes, we take the component to match the resolution of the
                    # data.
                    fit_comp = pd.DataFrame()
                    fit_comp['wavelength'] = fit_df['wavelength'].copy()
                    # values beyond the wavelength range will be 0, if any.
                    fit_comp['absorbance'] = np.interp(x=fit_comp['wavelength'],
                                                    xp=this_comp['wavelength'],
                                                    fp=this_comp['absorbance'],
                                                    left=0, right=0)
                
                # add the formatted component to the list of fitting components
                self._comps.append(fit_comp)
            #ib = len(self._comps)
            self._n_comps = len(self._comps)
            
        else:
            self._comps = None
            self._do_comps = False
            self._n_comps = 0
            
        if ng is not None:    
            if type(ng) == int:
                ng_lower = ng
                ng_upper = ng+1
            else:
                ng_lower = ng[0]
                ng_upper = ng[1]
        elif (ng_lower is not None) or (ng_upper is not None):
            warnings.warn("Defining the lower and upper limits through the "+
                          "ng_lower and ng_upper parameters is depreciated and"+
                          " will be removed in a future version. Use the ng "+
                          "parameter instead. For example, instead of writing "+
                          f"ng_lower={ng_lower}"+", " f"ng_upper={ng_upper}"+
                          " you should write "+f"ng=({ng_lower}, {ng_upper})", 
                         DeprecationWarning, stacklevel=2)
        self._log(f"fitting will use between {ng_lower} and " +
                  f"{ng_upper} gaussian functions")
        
        # manage the guesses for the fitted parameters
        if guesses is None:
            #print("you must provide guesses!! >:O")
            self._log("no guesses provided. Automatic guessing instead.")
            guesses = self._make_guesses(ng_upper, fit_df['wavelength'])
            
        # unwrap guesses and bounds
        p0 = []
        lower_bounds = []
        upper_bounds = []
        for guess in guesses:
            p0.append(guess['guess'])
            lower_bounds.append(guess['lower'])
            upper_bounds.append(guess['upper'])
        bounds = (lower_bounds, upper_bounds)

        # a place to store our fit results
        fit_results = []
        # do the fitting with different numbers of gaussians
        for n in range(ng_lower, ng_upper):
            self._log(f"Attempting fit with {n} gaussians")
            
            these_p0 = p0[:self._n_comps+self._n_scatt+n*3]
            these_bounds = (bounds[0][:self._n_comps+self._n_scatt+n*3],
                            bounds[1][:self._n_comps+self._n_scatt+n*3])

            p, pcov = curve_fit(f=self._fit_function,
                                xdata=fit_df['wavelength'], 
                            ydata=fit_df["absorbance"]+self.offset,
                            p0=these_p0, bounds=these_bounds)
            best_fit = self._fit_function(fit_df['wavelength'], *p)
            redchi2 = (((best_fit-fit_df['absorbance'])**2)
                       /best_fit).sum() / (len(p))
            fit_results.append({'redchi2':redchi2, 'n':n,
                                'best_fit':best_fit, 'p':p, 'pcov':pcov})
            self._log("fit success with reduced chi2: {0:.2f}".format(redchi2))
                
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

        self._log("The best fit was achieved with " +
                  "{0}".format(fit_results[best_i]['n']) +
                  " gaussians and a reduced chi2 of"+
                  " {0:.2f}".format(fit_results[best_i]['redchi2']))

        self._manage_fit_parameters(fit_results[best_i], fit_df)

    def flip_visibility(self):
        """
        Changes the visibility of the spectrum when plotting. If 
        the self.visible parameter is false, the plot_absorbance
        function will skip plotting this spectrum.
        """
        self.visible = not self.visible
        self._log(f'flipped visibility from {not self.visible} '+
                  f'to {self.visible}')
        
    def remove_bkgd(self, bkgd_fname):
        """
        Removes a background from this spectrum's list of backgrounds
        
        bkgd_name : (str) the name of the background being removed
        """
        for bkgd in self.bkgds:
            if bkgd.fname == bkgd_fname:
                self.bkgds.remove(bkgd)
        #self.bkgd_files.remove(bkgd_fname)
        self._log(f'removed bkgd file {bkgd_fname}')
        
    def remove_sample(self, sample_fname):
        """
        Removes a sample from this spectrum's list of samples
        
        sample_name : (str) the name of the spectrum being removed
        """
        for sample in self.samples:
            if sample.fname == sample_fname:
                self.samples.remove(sample)
        #self.sample_files.remove(sample_fname)
        self._log(f'removed sample file {sample_fname}')

    def subtract_baseline(self, lim=None, how="min"):
        """
        Performs a baseline subtraction on the spectrum. This is done just by
        shifting all values such that some chosen value is zero. There are two
        methods, determined by the how parameter.
        
        lim : (tuple or None) the limits on where the zero point is searched
              for. Defaults to None.
        how : (str) How to determine the zero point. Acceptable values are
              "min", and "right". When "min", the function will find the minimum
              absorbance value within the wavelength range set by lim, and shift
              the data such that it is zero. When "right", the rightmost
              value will be shifted such that it is zero.
        """
        # set limits for finding the shift value
        if lim is not None:
            search_df = self.data[(self.data['wavelength'] >= lim[0]) &
                                  (self.data['wavelength'] <= lim[1])]
        else:
            search_df = self.data
        
        # if this has already been run, make sure we search on unshifted data
        if 'raw_absorbance' in self.data.columns:
            key = 'raw_absorbance'
        else:
            key = 'absorbance'
        
        # do the shifting
        if how == "min":
            # get the minimum value as the shift
            shift = -1*search_df[key].min()
        elif how == "right":
            # get the rightmost value as the shift
            shift = -1*search_df[key].iloc[-1]
        else:
            print("Invalid value for the how parameter."+
                  " You entered '{0}',".format(how) + 
                  " but only 'min' or 'right' are accepted." +
                  " Run help(tools.Spectrum.subtract_baseline) for help.")
            return None
        
        # apply the shift
        shifted = [a+shift for a in self.data[key]]
        
        # remap the unshifted data to 'raw_absorbance' if needed
        if not ('raw_absorbance' in self.data.columns):  
            self.data['raw_absorbance'] = self.data['absorbance'].copy()
        # remap the shifted data to 'absorbance'
        self.data['absorbance'] = shifted

        self._log(f"baseline subtracted using the '{how}' method " +
                  f"and a shift of {shift}")

    def update_description(self, new_description):
        """
        Change the description of the spectrum
        """
        self.description = new_description
        #self._log('changed description')            
        

class StitchedSpectrum(Spectrum):
    """
    Represents a stitched spectrum, so the combination of two spectra
    
    Parameters belonging to the fully constructed object:
        
        bkgds : (list)
        color : (str) the hex color used for plotting this spectrum.
        data : (pandas.DataFrame) the data belonging to this
               spectrum, averaged together from its corresponding
               scans.
        linestyle : (str) the matplotlib linestyle for plotting.
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
    def __init__(self, specs, debug=False):
        """
        """
        # parameters independent from the list of spectra
        self.changelog = ""
        self.debug = debug
        self.offset = 0
        self.visible = True
        self.description = ""
        self.baseline_p = None
        self.peaks = None
        self.peak_errors = None
        self.fit_results = None
        
        # inherit from the first spectrum
        self.color = specs[0].color
        self.cindex = specs[0].cindex
        self.lenccycle = specs[0].lenccycle
        self.cmap = specs[0].cmap
        self.linestyle = specs[0].linestyle
        self.linewidth = specs[0].linewidth
        
        # create the name, list of samples and backgrounds
        self.name = ""
        self.samples = []
        self.bkgds = []
        for spec in specs:
            self.name += "-" + spec.name
            self.samples += spec.samples
            self.bkgds += spec.bkgds
        self.name = self.name[1:]
        self.oldname = ""

        # initialize the data
        self.data = self._stitch(specs)
        
    def _stitch_legacy(self, specs):
        """
        Stiches two Spectrum objects together. The two objects should
        have overlapping data.
        """
        # make sure spec1 is the short wavelength, spec2 is the long wavelength
        wlA = specs[0].data['wavelength'][0]
        wlB = specs[1].data['wavelength'][0]
        if wlA > wlB:
            spec1 = specs[1]
            spec2 = specs[0]
        else:
            spec1 = specs[0]
            spec2 = specs[1]
        # a place to store the overlapping region
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
        #spec2.offset = offset
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

    def _stitch(self, specs):
        # write to changelog
        specNames = []
        offsets = []
        for spec in specs:
            specNames.append(spec.name)
            offsets.append(spec.offset)
        self._log(f"began stitching with {len(specs)} spectra: {specNames}")
        if any(offsets):
            self._log("Alert! There are spectra with non-zero offsets in the " +
                      "list of spectra to be stitched. The offsets " +
                      "corresponding to the spectra in the list above, are: " +
                      f"{offsets}. The offsets will be added to the " +
                      "absorbance of their spectrum when stitching.")

        # Create a dictionary to hold the combined spectrum.
        combined = {}
    
        # Iterate through each spectrum in the list
        for spec in specs:
            wavelengths = spec.data['wavelength']
            absorptions = spec.data['absorbance'] + spec.offset
            
            # Add each data point to the combined spectrum
            for wl, ab in zip(wavelengths, absorptions):
                if wl in combined:
                    # Compare resolution if the wavelength already exists
                    current_res = np.abs(np.diff(wavelengths)).min()
                    existing_res = combined[wl]['res']
    
                    if current_res < existing_res:
                        # Update with higher resolution data
                        combined[wl]['absorbance'] = ab
                        combined[wl]['res'] = current_res
                        combined[wl]['nScans'] = len(spec.samples)
                    elif current_res == existing_res:
                        # Choose the spectrum with more scans (higher SN)
                        current_nScans = len(spec.samples)
                        existing_nScans = combined[wl]['nScans']
                        if current_nScans > existing_nScans:
                            combined[wl]['absorbance'] = ab
                            combined[wl]['res'] = current_res
                            combined[wl]['nScans'] = len(spec.samples)
                    # if they are the same, do nothing
                else:
                    # Add new wavelength entry
                    res = np.abs(np.diff(wavelengths)).min()
                    combined[wl] = {'absorbance': ab,
                                    'res': res,
                                    'nScans':len(spec.samples)}
    
        # Convert the combined spectrum dictionary back to arrays
        combined_wl = np.array(sorted(combined.keys()))
        combined_ab = np.array(
            [combined[wl]['absorbance'] for wl in combined_wl])

        new_df = pd.DataFrame({'wavelength':combined_wl,
                               'absorbance':combined_ab})
        self._log("finished stitching. The stitched spectrum now has " +
                  f"wavelength limits: [{combined_wl[0]}, {combined_wl[-1]}]")
    
        return new_df
    
def plot_fit(spec, xlim=None, ylim=None, plot_peaks=False,
             plot_fit_components=True, figsize=(7,5), fig=None, ax1=None,
             save_path=None, plot_residuals=True, res_lims=(-0.0075, 0.0075),
             do_top_axis=True, legend_loc=None, legend_loc_r=1):
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
        fig, ax = plt.subplots(2, 1, gridspec_kw={'height_ratios': [3, 1.2]},
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
             color=spec.color, label=spec.name, linestyle=spec.linestyle, 
             linewidth=spec.linethickness)
    # calculate a color for the fit
    fit_color = lighten_color(spec.color, amount=1.2)
    # plot the fit
    ax1.plot(spec.data['wavelength'], spec.data['best_fit']+spec.offset,
             color=fit_color, linestyle='--', label=spec.name+" Best Fit",
             linewidth=spec.linethickness)
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
            
    if do_top_axis:
        # Create the second x-axis on which the energy in eV will be displayed
        #plt.tick_params(axis='x',which='both',bottom=True,top=False,
        #                labelbottom=True)
        ax2 = ax1.secondary_xaxis('top', functions=(WLtoE, EtoWL))
        ax1.xaxis.set_tick_params(top=False, which="both")#, labelbottom=True)
        ax2.set_xticks([])
        ax2.set_xlabel('Energy (eV)', labelpad=8)

        # Get ticks from ax1 (wavelengths)
        wl_ticks = ax1.get_xticks()
        wl_ticks = preventDivisionByZero(wl_ticks)

        # Based on the ticks from ax1 (wavelengths), calculate the corresponding
        # energies in eV
        E_ticks = WLtoE(wl_ticks)

        # Set the ticks for ax2 (Energy)
        ax2.set_xticks(E_ticks)
        ax2.xaxis.set_major_locator(ticker.MaxNLocator(integer=True))

        # Allow for two decimal places on ax2 (Energy)
        #ax2.xaxis.set_major_formatter(FormatStrFormatter('%.2f'))

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
        axr.legend(loc=legend_loc_r)
        if res_lims is not None:
            axr.set_ylim(res_lims[0], res_lims[1])
    else:
        axr = None
        
    #ax1.grid()
    ax1.legend(loc=legend_loc)
    
    fig.tight_layout()
    fig.subplots_adjust(hspace=0.1)
    
    if save_path:
        plt.savefig(save_path, bbox_inches='tight')

    return ax1, axr

def plot_scans(scans, xaxis, yaxis, xlim=None, ylim=None, figsize=(8, 4.5),
               save_path=None, return_fig_and_ax=False, do_legend=True,
               do_titles=True, ax=None, fig=None):
    """
    Takes any number of scans and plots whatever is relevant.
    """
    plt.style.use('./au-uv.mplstyle')

    if ax is None:
        fig, ax = plt.subplots(1, 1)
        fig.set_size_inches(figsize[0], figsize[1])
        
    if xlim:
        ax.set_xlim(xlim)
    if ylim:
        ax.set_ylim(ylim)

    for scan in scans:
        if scan.visible:
            ax.plot(scan.data[xaxis], scan.data[yaxis], color=scan.color,
                    label=scan.name, linewidth=2)

    if do_titles:
        ax.set_ylabel(yaxis)
        ax.set_xlabel(xaxis)

    if do_legend:
        handels, labels = get_handles([ax])
        if handels:
            ax.legend()
    
    if save_path:
        plt.savefig(save_path, bbox_inches='tight')

    fig.tight_layout()

    if return_fig_and_ax:
        return fig, ax
    else:
        return None

def plot_absorbance(spectra, xlim=None, ylim=None, peaks=None, plot_fit=False,
                    plot_peaks=False, plot_fit_components=False, figsize=(7,5),
                    raw=False, fig=None, ax1=None, save_path=None,
                    return_fig=False, do_top_axis=True, do_legend=True,
                    do_titles=True, legend_loc=None, do_top_xlabel=True,
                    do_bottom_xlabel=True, do_ylabel=True,
                    return_fig_and_ax=False):
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
                         color=spec.color, label=spec.name,
                         linestyle=spec.linestyle, linewidth=spec.linewidth)
            else:
                ax1.plot(spec.data['wavelength'], 
                         spec.data['absorbance']+spec.offset,
                         color=spec.color, label=spec.name,
                         linestyle=spec.linestyle, linewidth=spec.linewidth)
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

    if do_top_axis:
        # Create the second x-axis on which the energy in eV will be displayed
        ax2 = ax1.secondary_xaxis('top', functions=(WLtoE, EtoWL))
        ax1.xaxis.set_tick_params(top=False, which="both")
        ax2.set_xticks([])
        
        if do_titles:
            if do_top_xlabel:
                ax2.set_xlabel('Energy (eV)', labelpad=8)

        # Get ticks from ax1 (wavelengths)
        wl_ticks = ax1.get_xticks()
        wl_ticks = preventDivisionByZero(wl_ticks)

        # Based on the ticks from ax1 (wavelengths), calculate the corresponding
        # energies in eV
        E_ticks = WLtoE(wl_ticks)

        # Set the ticks for ax2 (Energy)
        ax2.set_xticks(E_ticks)

        # Allow for two decimal places on ax2 (Energy)
        #ax2.xaxis.set_major_formatter(FormatStrFormatter('%.2f'))
        ax2.xaxis.set_major_locator(ticker.MaxNLocator(integer=True))

    if do_titles:
        if do_ylabel:
            ax1.set_ylabel("Absorbance")
        if do_bottom_xlabel:
            ax1.set_xlabel("Wavelength (nm)")
    if do_legend:
        handels, labels = get_handles([ax1])
        if handels:
            ax1.legend(loc=legend_loc)
    
    if save_path:
        plt.savefig(save_path, bbox_inches='tight')

    if return_fig_and_ax:
        axes = [ax1, ax2]
        return fig, axes
    elif return_fig:
        return fig
    else:
        return ax1

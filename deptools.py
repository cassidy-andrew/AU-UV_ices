import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit


def _sloped_depositon_curve(x, m, c, xc, w, A):
    """
    The function used to fit the deposition time scan. It is the linear
    combintation of a linear function and a sin function. The parameters are as
    follows:
    
    x : (array-like) The x values of the function, in seconds.
    m : (float) The slope of the linear component.
    c : (float) The y-intercept of the linear component.
    xc : (float) The x-shift on the sinusoidal component.
    w : (float) The 'wavelength' of the sinusoidal component. Remember that this
        is a time scan, so the units of this 'wavelength' are seconds.
    A : (float) The amplitude of the sinusoidal component.
    """
    return (m*x+c)+A*np.sin(np.pi*(x-xc)/w)


class DepositionTimeScan:
    """
    A class for fitting the deposition time scans. These are used to monitor the
    deposition of the ice, and calculate the thickness of the deposited ice.
    Calculating the thickness of the ice is the primary purpose of this class.
    The time scans can be fit, and those parameters are used to get the
    deposition rate. You can then calculate the thickness of an ice deposited at
    that rate for some amount of time.
    
    Parameters belonging to the fully constructed object:
    
    data : (pandas.DataFrame) The data of the timescan. 
    dosing_rate : (dict) The calculated dosing rate after find_dosing_rate() is
                  run. It is a dictionary with two keys: 'value' and 'error',
                  containting the value and error of the dosing rate
                  respectively. The units are in nanometers per second.
    fit_parameters : (list) A list of all the parameters fit.
    redchi2 : (float) The reduced chi square of the fit.
    refractive_index : (dict) The calculated refractive index of the deposited
                       ice. It is a dictionary with two keys: 'value' and
                       'error', containting the value and error of the
                       refractive index respectively.
    """
    def __init__(self, fname):
        """
        Parameters required to construct the object:
        """
        # read the data
        self.data = self._read_data(fname)
        # initialize other parameters
        self.dosing_rate = None
        self.fit_parameters = None
        self.redchi2 = None
        self.refractive_index = None
        
    def _read_data(self, fname):
        """
        Reads the data of a timescan.
        
        fname : (str) The path to the timescan file.
        """
        column_names = ['Time/s','Ch0/V','Ch0/volts','Ch2/volts','Ch3/volts',
                        'Z_Motor','Beam_current','temperature','Absorbance']
        df = pd.read_csv(fname, header=[2], delimiter=r"\s+")
        df.columns = column_names
        
        return df
        
    def find_dosing_rate(self, guesses=None, t_start=0, t_end=np.inf,
                         theta_radians=12, verbose=False):
        """
        Determine the refractive index of the ice and the dosing rate.
        
        guesses : (list) Guesses on the initial parameters fit to the timescan
                  curve. These must be provided as a list of dictionaries:
                  {'lower':, 'guess':, 'upper':} where 'guess' is your guess for
                  the value of a fit parameter, and 'lower' and 'upper' are
                  lower and upper limits respectively. There must be five such
                  dictionaries in the list, corresponding to the five parameters
                  of the fit function _sloped_depositon_curve(). See that
                  functions' documentation for details
                  (run help(spectools._sloped_depositon_curve)).
        t_end : (float) The end time of the deposition, in seconds after the
                timescan began. If None, assumed to be the end of the timescan.
        t_start : (float) The start time of the deposition, in seconds after the
                  timescan began. If None, assumed to be the start of the
                  timescan.
        theta_radians : (float) The angle in radians between the substrate and
                        the incident beam. Defaults to 12.
        verbose : (boolean) Whether or not to print the fitted parameters in
                  addition to the regular output. Good for debugging.
        """
        # initialize the guesses
        if guesses is None:
            guesses = [{'lower':-np.inf, 'guess':3e-6, 'upper':np.inf}, # m
                       {'lower':-np.inf, 'guess':0, 'upper':np.inf}, # c
                       {'lower':-np.inf, 'guess':100, 'upper':np.inf}, # xc
                       {'lower':0, 'guess':500, 'upper':np.inf}, # w
                       {'lower':-np.inf, 'guess':0.01, 'upper':np.inf} # A
                        ]
            
        # unwrap guesses and bounds
        p0 = []
        lower_bounds = []
        upper_bounds = []
        for guess in guesses:
            p0.append(guess['guess'])
            lower_bounds.append(guess['lower'])
            upper_bounds.append(guess['upper'])
        bounds = (lower_bounds, upper_bounds)
        #print(bounds)
        # apply limits
        fit_df = self.data[(self.data['Time/s'] > t_start) & 
                           (self.data['Time/s'] < t_end)].copy()
        
        # do the fit        
        popt, pcov = curve_fit(_sloped_depositon_curve, fit_df['Time/s'], 
                               fit_df['Ch2/volts'], p0=p0, bounds=bounds)
        perr = np.sqrt(np.diag(pcov))
        
        # extract fit parameters
        m, c, xc, w, A = popt[:5]
        m_err, c_err, xc_err, w_err, A_err = perr[:5]
        self.fit_parameters = [{'name':'m', 'value':m, 'error':m_err},
                               {'name':'c', 'value':c, 'error':c_err},
                               {'name':'xc', 'value':xc, 'error':xc_err},
                               {'name':'w', 'value':w, 'error':w_err},
                               {'name':'A', 'value':A, 'error':A_err}]
        
        # get the fitted line
        y= _sloped_depositon_curve(fit_df['Time/s'], m, c, xc, w, A)
        fit_df['fit'] = y
        
        # get the reduced chi square
        redchi2 = np.sum(((fit_df['Ch2/volts']-y)**2)/y) / 5
        self.redchi2 = redchi2
        
        # refractive index at 632.8 nm
        n2 = (c+A)/(c-A)
        n2_err = c_err*2+A_err*2
        self.refractive_index = {'value':n2, 'error':n2_err}
        
        if n2 < 1:
            print(f"Warning! The found refractive index of \033[1m{n2:.3f} +- "+ 
                  f"{n2_err:.3f}\033[0m is less than 1, which is not physical!"+
                  " Check the fit, maybe something went wrong?")
        
        theta = np.radians(theta_radians)
        theta2 = np.arcsin(theta/n2)
        d=632.8/(2*n2*np.cos(theta2))
        d_err=n2_err
        rate=d/(2*w)
        rate_err = d_err+w_err/w
        self.dosing_rate = {'value':rate, 'error':rate_err}
        
        # add the best fit back
        if 'fit' in self.data:
            self.data = self.data.drop(columns=['fit'])
        self.data = self.data.merge(fit_df, how='left')
        
        self.fit_parameters += [
            {"name":"dosing rate (nm/s)", "value":rate, "error":rate_err},
            {"name":"refractive index", "value":n2, "error":n2_err},
            {"name":"redchi2", "value":redchi2, "error":None},
        ]
        
        if verbose:
            print(f"The fit suceeded with a reduced chi square of " +
                  f"\033[1m{redchi2:.3e}\033[0m")
            print(f"The deposition rate is \033[1m{rate:.3f} +- " + 
                  f"{rate_err:.3f} nm/s\033[0m")
            print(f"The ice's index of refraction is \033[1m{n2:.3f} +- " + 
                  f"{n2_err:.3f}\033[0m")
            print("The other fitted values are:")
            for p in self.fit_parameters[:5]:
                print(p)
                
    def find_thickness(self, dep_time, verbose=False):
        """
        Finds the thickness of some other ice deposited the same exact way, but
        for a different amount of time.
        
        dep_time : (float) the time in seconds for deposition of the ice.
        """
        t = self.dosing_rate['value'] * dep_time
        t_err = t*(self.dosing_rate['error']/self.dosing_rate['value'])
        if verbose:
            print(f"The ice deposited for {dep_time} seconds will be " + 
                  f"\033[1m{t:.3f} +- {t_err:.3f} nm \033[0mthick.")
        return t, t_err
    
    def find_deposition_time(self, thickness, verbose=False):
        """
        Finds the time required to deposit an ice of some thickness, with all
        else being the same.
        
        thickness: (float) the thickness of the desired ice in nanometers.
        """
        t = thickness / self.dosing_rate['value']
        t_err = t*(self.dosing_rate['error']/self.dosing_rate['value'])
        if verbose:
            print(f"The ice deposited to {thickness} nm will take " +
                  f"\033[1m{t:.3f} +- {t_err:.3f} seconds\033[0m.")
        return t, t_err
        
    def export(self, path):
        """
        Export the fitted parameters of the timescan to a csv. The csv file will
        have three columns. One for the name of the parameter, one for the value
        and one for the error.
        
        path : (str) The desired path for the saved csv file.
        """
        df = pd.DataFrame(self.fit_parameters)
        df.to_csv(path, index=False)
        
    def plot_timescan(self, ax=None, figsize=(16/2.5,9/2.5), xlim=None,
                      plot_fit=True, save_path=None):
        """
        Makes a plot of the timescan channel 2 data, as well as the fit if
        desired.
        
        ax : (matplotlib.axes) The axis to plot on, if desired. Defaults to None
             where a new axis will be created.
        figsize : (tuple) The figuresize in inches. Defaults to (16/2.5, 9/2.5)
        plot_fit : (boolean) whether or not to plot the fit. Defaults to True
        save_path : (str) The path to save the figure if desired. Defaults to
                    None.
        xlim : (tuple or 2-item list) the x axis limits of the plot. Defaults to
               None, and matplotlib will find them automatically.
        """
        plt.style.use('./au-uv.mplstyle')
        # setup axis, if one isn't provided already
        if ax is None:
            fig, ax = plt.subplots(1, 1)
            fig.set_size_inches(figsize[0], figsize[1])
        
        ax.plot(self.data['Time/s'], self.data['Ch2/volts'],
                label="Data", color="black")
        
        # plot the fit, but only if desired and it exists
        if plot_fit and ('fit' in self.data):
            ax.plot(self.data['Time/s'], self.data['fit'],
                    label="Fit", color="red")
        
        ax.set_xlabel("Time (seconds)")
        ax.set_ylabel("Ch2 Signal (volts)")
        ax.legend()
        
        if xlim:
            ax.set_xlim(xlim[0], xlim[1])
        if save_path:
            plt.savefig(save_path, bbox_inches='tight')
        
        return ax

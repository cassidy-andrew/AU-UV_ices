import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
from scipy.ndimage.filters import gaussian_filter
from scipy.signal import argrelextrema


def _sloped_depositon_curve(t, m, c, tc, w, A):
    """
    The function used to fit the deposition time scan. It is the linear
    combintation of a linear function and a sin function. The parameters are as
    follows:
    
    t : (array-like) The x values of the function, in seconds.
    m : (float) The slope of the linear component.
    c : (float) The y-intercept of the linear component.
    tc : (float) The x-shift on the sinusoidal component.
    w : (float) The 'wavelength' of the sinusoidal component. Remember that this
        is a time scan, so the units of this 'wavelength' are seconds.
    A : (float) The amplitude of the sinusoidal component.
    """
    return (m*t+c)+A*np.sin(np.pi*(t-tc)/w)

def _sloped_depositon_curve_n(t, m, c, tc, w, n):
    """
    The function used to fit the deposition time scan. It is the linear
    combintation of a linear function and a sin function. The parameters are as
    follows:
    
    t : (array-like) The x values of the function, in seconds.
    m : (float) The slope of the linear component.
    c : (float) The y-intercept of the linear component.
    tc : (float) The x-shift on the sinusoidal component.
    w : (float) The 'wavelength' of the sinusoidal component. Remember that this
        is a time scan, so the units of this 'wavelength' are seconds.
    n : (float) The index of refraction of the ice.
    """
    return (m*t+c)+(c*((n-1)/(n+1)))*np.sin(np.pi*(t-tc)/w)


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
    deposition_rate : (dict) The calculated deposition rate after
                      find_deposition_rate() is run. It is a dictionary with two
                      keys: 'value' and 'error', containting the value and error
                      of the deposition rate respectively. The units are in
                      nanometers per second.
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
        self.deposition_rate = None
        self.fit_parameters = None
        self.redchi2 = None
        self.refractive_index = None
        self.Rmin = None
        self.Rmax = None
        
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

    def find_deposition_rate(self, guesses=None, t_start=0, t_end=np.inf,
                         theta_degrees=22, verbose=False, do_smoothing=True):
        """
        Determine the refractive index of the ice and the deposition rate.
        
        do_smoothing : (boolean) whether or not to apply gaussian smoothing to
                       the data before fitting. Defaults to True.
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
        theta_degrees : (float) The angle in degrees between the substrate and
                        the incident beam. Defaults to 22.
        verbose : (boolean) Whether or not to print the fitted parameters in
                  addition to the regular output. Good for debugging.
        """
        # initialize the guesses
        if guesses is None:
            guesses = [{'lower':-np.inf, 'guess':3e-6, 'upper':np.inf}, # m
                       {'lower':-np.inf, 'guess':0, 'upper':np.inf}, # c
                       {'lower':-np.inf, 'guess':200, 'upper':np.inf}, # tc
                       {'lower':0, 'guess':300, 'upper':np.inf}, # w
                       {'lower':0, 'guess':0.1, 'upper':100} # A
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

        # smooth if needed, and apply time limits
        if do_smoothing:
            # apply time limits
            fit_df = self.data[(self.data['Time/s'] > t_start) & 
                           (self.data['Time/s'] < t_end)].copy()
            # smooth
            fit_df['smoothed Ch2'] = gaussian_filter(fit_df['Ch2/volts'],
                                                     sigma=7, mode='nearest')
            # we fit to this
            fit_y = fit_df['smoothed Ch2']
        else:
            # apply time limits
            fit_df = self.data[(self.data['Time/s'] > t_start) & 
                           (self.data['Time/s'] < t_end)].copy()
            # we fit to this
            fit_y = fit_df['Ch2/volts']
        
        # do the fit        
        popt, pcov = curve_fit(_sloped_depositon_curve, fit_df['Time/s'], 
                               fit_y, p0=p0, bounds=bounds)
        perr = np.sqrt(np.diag(pcov))
        
        # extract fit parameters
        m, c, tc, w, A = popt[:5]
        m_err, c_err, tc_err, w_err, A_err = perr[:5]
        self.fit_parameters = [{'name':'m', 'value':m, 'error':m_err},
                               {'name':'c', 'value':c, 'error':c_err},
                               {'name':'tc', 'value':tc, 'error':tc_err},
                               {'name':'w', 'value':w, 'error':w_err},
                               {'name':'A', 'value':A, 'error':A_err}]
        
        # get the fitted line
        y= _sloped_depositon_curve(fit_df['Time/s'], m, c, tc, w, A)
        fit_df['fit'] = y
        n = A
        n_err = A_err
        
        # get the reduced chi square
        redchi2 = np.sum(((fit_df['Ch2/volts']-y)**2)/y) / 5
        self.redchi2 = redchi2

        # find the maximum and minimum signal
        maxima = argrelextrema(np.array(y), np.greater)[0]
        minima = argrelextrema(np.array(y), np.less)[0]
        specifier = -1
        try:
            maxSignal_x = fit_df['Time/s'].iloc[maxima[specifier]]
            maxSignal_y = y.iloc[maxima[specifier]]
        except:
            print("Warning: No R_max found from fit, taking simple maximum")
            maxSignal_y = max(y)
            maxSignal_x = fit_df['Time/s'].iloc[np.argmax(y)]
        try:
            minSignal_x = fit_df['Time/s'].iloc[minima[specifier]]
            minSignal_y = y.iloc[minima[specifier]]
        except:
            print("Warning: No R_min found from fit, taking simple minimum")
            minSignal_y = min(y)
            minSignal_x = fit_df['Time/s'].iloc[np.argmin(y)]

        self.Rmax = (maxSignal_x, maxSignal_y)
        self.Rmin = (minSignal_x, minSignal_y)

        # Find the index of refraction Based on Born & Wolf
        n1 = 1      # index of refraction of vacuum
        n3 = 1.377  # index of refraction of MgF2 substrate, at 632.8 nm
        k = ((n1-n3)/(n1+n3))*(np.sqrt(minSignal_y/maxSignal_y))
        
        n = np.sqrt(n1*n3*((1-k)/(1+k)))
        self.refractive_index = {'value':n, 'error':None}

        # apply snell's law
        theta = np.radians(theta_degrees)
        theta2 = np.arcsin(n1*np.sin(theta)/n)
        
        # see equation 8 of Ioppolo et al. (2021) A&A 646, A172.
        # https://doi.org/10.1051/0004-6361/202039184
        # for this. But instead of getting the thickness directly using the full
        # equation, we skip the N term and divide by the period. This gives us
        # the deposition rate (number of pattern repititions N=deptime/period).
        d=632.8/(2*n*np.cos(theta2))
        d_err=n_err/n
        rate=d/(2*w)
        rate_err = np.sqrt((d_err/d)**2 + (w_err/w)**2)
        self.deposition_rate = {'value':rate, 'error':rate_err}
        
        # add the best fit back
        if 'fit' in self.data:
            self.data = self.data.drop(columns=['fit'])
        self.data = self.data.merge(fit_df, how='left')
        
        self.fit_parameters += [
            {"name":"deposition rate (nm/s)", "value":rate, "error":rate_err},
            {"name":"refractive index", "value":n, "error":n_err},
            {"name":"redchi2", "value":redchi2, "error":None},
        ]
        
        if verbose:
            print(f"The fit suceeded with a reduced chi square of " +
                  f"\033[1m{redchi2:.3e}\033[0m")
            print(f"The deposition rate is \033[1m{rate:.3f} +- " + 
                  f"{rate_err:.3f} nm/s\033[0m")
            print(f"The ice's index of refraction is \033[1m{n:.3f} +- " + 
                  f"{n_err:.3f}\033[0m")
            print("The other fitted values are:")
            for p in self.fit_parameters[:4]:
                print(f"'{p['name']}' : "+
                      f"{p['value']:.3f} "+
                      f"+- {p['error']:.3f}")
                
    def find_thickness(self, dep_time, verbose=False):
        """
        Finds the thickness of some other ice deposited the same exact way, but
        for a different amount of time.
        
        dep_time : (float) the time in seconds for deposition of the ice.
        """
        t = self.deposition_rate['value'] * dep_time
        t_err = t*(self.deposition_rate['error']/self.deposition_rate['value'])
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
        t = thickness / self.deposition_rate['value']
        t_err = t*(self.deposition_rate['error']/self.deposition_rate['value'])
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
        
def plot_timescan(dep, ax=None, figsize=(16/2.5,9/2.5), xlim=None,
                  plot_fit=True, save_path=None, plot_smoothed=True,
                  return_fig_and_ax=False):
    """
    Makes a plot of the timescan channel 2 data, as well as the fit if
    desired.

    ax : (matplotlib.axes) The axis to plot on, if desired. Defaults to None
         where a new axis will be created.
    dep : (DepositionTimeScan) The time scan to be plotted.
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

    ax.plot(dep.data['Time/s'], dep.data['Ch2/volts'],
            label="Data", color="black")
    
    if plot_smoothed and ('smoothed Ch2' in dep.data):
        ax.plot(dep.data['Time/s'], dep.data['smoothed Ch2'],
                label="Smoothed Data", color="blue", linewidth=6, alpha=0.3)

    # plot the fit, but only if desired and it exists
    if plot_fit and ('fit' in dep.data):
        ax.plot(dep.data['Time/s'], dep.data['fit'],
                label="Fit", color="red")
        # show the minimum and maximums used for the fit, if any
        if (dep.Rmin is not None) and (dep.Rmax is not None):
            ax.plot(dep.Rmin[0], dep.Rmin[1], marker='o', markersize=10,
                    color='red', alpha=0.6)
            ax.plot(dep.Rmax[0], dep.Rmax[1], marker='o', markersize=10,
                    color='red', alpha=0.6)

            xlim = ax.get_xlim()
            x_offset = (xlim[1] - xlim[0]) * 0.02
            ylim = ax.get_ylim()
            y_offset = (ylim[1] - ylim[0]) * 0.04
            ax.text(dep.Rmin[0]+x_offset, dep.Rmin[1]-y_offset*2,
                    r"$R_{min}$", color='red')
            ax.text(dep.Rmax[0]+x_offset, dep.Rmax[1]+y_offset/2,
                    r"$R_{max}$", color='red')
            # make sure the text fits in the y limits of the plot
            ax.set_ylim(ylim[0]-y_offset*2, ylim[1]+y_offset*2)
            

    ax.set_xlabel("Time (seconds)");
    ax.set_ylabel("Signal (volts)");
    ax.legend(framealpha=0);

    if xlim:
        ax.set_xlim(xlim[0], xlim[1])
    if save_path:
        plt.savefig(save_path, bbox_inches='tight')

    if return_fig_and_ax:
        return fig, ax
    else:
        return ax


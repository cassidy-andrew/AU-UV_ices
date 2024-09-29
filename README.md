# DUVET
**D**anish **UV** **E**nd-station **T**ool

This tool is designed to help you manage data obtained at the AU-UV endstation of the ASTRID2 synchrotron at Aarhus Univeristy, in Denmark.
Its current main functionality is to read the data files produced by the endstation, calculate absorbances, and produce plots of absorbance.
It can also fit the absorbance data with gaussian functions as a first step in your data analysis.

This document provides usage examples. To being using the tools, you must have `spectools.py` in your working directory, and import it as follows:


```python
import spectools
#help(spectools)
```

You can run `help(spectools)` to see a full summary of the classes and methods. 

## Example: Reading Data

To read data, you need to know the paths to your relevant samples and backgrounds. You can have as many samples and backgrounds as you want, and they will be averaged together. For this example, I have two. 


```python
# keep things reproducable by setting the random seed.
import random
random.seed(31415)
```


```python
path = "./raw_data/SergioIoppolo-November2023/20231101/"

bkgd_short1 = path + "R73773.d01"
bkgd_short2 = path + "R73773.d02"
sample_short1 = path + "R73780.d01"
sample_short2 = path + "R73780.d02"

# build the spectrum object
spec1 = spectools.Spectrum()
spec1.change_name("R73780")
# add backgrounds
spec1.add_bkgd(bkgd_short1)
spec1.add_bkgd(bkgd_short2)
# add samples
spec1.add_sample(sample_short1)
spec1.add_sample(sample_short2)
# give it a color (is black by default)
spec1.change_color("blue")
# average the scans together
spec1.average_scans()

# make a plot of the data
spectools.plot_absorbance([spec1], figsize=(7, 5),
                      xlim=(120, 340), ylim=(-0.02, 0.7),
                      save_path="./misc_figures/one_spectrum.svg");
```


    
![png](README_files/output_5_0.png)
    
s

By running `help` on the `Spectrum` object you can see all its methods:


```python
help(spec1)
```

    Help on Spectrum in module spectools object:
    
    class Spectrum(builtins.object)
     |  Spectrum(debug=False)
     |
     |  Represents a spectrum, so the average of one or more scans
     |
     |  Parameters belonging to the fully constructed object:
     |
     |      baseline_p : (list) parameters from the fit of the rayleigh scattering
     |                   baseline. None until subtract_baseline() has been run.
     |      bkgd : (pandas.DataFrame) The averaged background data.
     |      bkgd_files : (list) a list of background files that make up the scans.
     |      changelog : (str) a string which contains the history of the data. Every
     |                  time a function is called, a line is written to describe
     |                  what happened and at what time. This is then added to the
     |                  header of a file during export.
     |      cindex : (int) the index of the current position in the color cycle for
     |               color cycling.
     |      color : (str) the hex color used for plotting this spectrum.
     |      data : (pandas.DataFrame) the data belonging to this
     |             spectrum, averaged together from its corresponding
     |             scans.
     |      debug : (boolean) whether or not to run the functions of this Specturm
     |              in debug mode, where additional information is printed to the
     |              console as attributes are changed.
     |      fit_components : (list) a list of dictionaries which make up the fit
     |                       components after `fit_peaks()` is called. Each
     |                       dictionary has the following components: parameters,
     |                       and absorbance. The `parameters` are the three values
     |                       which describe the gaussian: amplitude, center, and
     |                       standard deviation. The `absorbance` has the y values
     |                       of the gaussian corresponding to the `data` parameter's
     |                       wavelength values.
     |      fit_results : (dict) A dictionary of the best fit results after
     |                    `fit_peaks()` is called. It consists of the following
     |                    components: redchi2, p, pcov, best_fit. `redchi2` is the
     |                    reduced chi square value of the fit. `p` is the fit
     |                    parameters. `pcov` is the covariance matrix of those
     |                    parameters. `best_fit` are the absorbance values
     |                    calculated to fit the data.
     |      linestyle : (str) the linestyle for matplotlib plotting.
     |      linewidth: (int) the line width for matplotlib plotting.
     |      name : (str) the name of this spectrum, which will be shown
     |             in plot legends.
     |      offset : (float) by how much the spectrum should be offset
     |               in the plot_absorbance() plot, in absorbance units.
     |               Defaults to 0.0.
     |      peaks : (list) a list of the peak positions in the spectrum. Is None
     |              prior to calling `fit_peaks()`.
     |      peak_errors : (list) a list of the standard deviation peak errors. Is
     |                    None prior to calling `fit_peaks()`
     |      sample : (pandas.DataFrame) The averaged sample data.
     |      sample_files : (list) a list of sample files that make up the scans.
     |      scans : (list) a list of SingleScan objects that will be
     |              averaged together to make this spectrum.
     |      visible : (boolean) whether the spectrum should appear in
     |                the plot generated by plot_absorbance() or not.
     |                Defaults to True.
     |
     |  Methods defined here:
     |
     |  __init__(self, debug=False)
     |
     |  add_bkgd(self, bkgd_fname)
     |      Adds a background file to this spectrum's list of backgrounds
     |
     |      bkgd_fname : (str) the path to the background file being added
     |
     |  add_sample(self, sample_fname)
     |      Adds a sample file to this spectrum's list of samples
     |
     |      sample_fname : (str) the path to the background file being added
     |
     |  average_scans(self)
     |      Averages the scans relating to this spectrum. First all backgrounds are
     |      averaged together. Then all samples are averaged together. Then the
     |      absorbance is calculated, taking the base 10 log of the ratio of the
     |      background and scan signal. The result is put in a pandas dataframe and
     |      stored in the .data parameter.
     |
     |  change_color(self, new_color)
     |      Changes the color used for plotting this spectrum
     |
     |  change_index(self, new_index)
     |      Changes the index of this spectrum for use in the DUVET GUI
     |
     |      new_index : (int) the new index for this spectrum
     |
     |  change_linestyle(self, new_style)
     |      Changes the linestyle of this spectrum
     |
     |      new_style : (str) the matplotlib linestyle for this spectrum
     |
     |  change_linewidth(self, new_width)
     |      Changes the line width of this spectrum
     |
     |      new_linewidth : (int) the matplotlib line width for this
     |                          spectrum
     |
     |  change_name(self, new_name)
     |      Changes the name of this spectrum
     |
     |      new_name : (str) the new name for this spectrum
     |
     |  change_offset(self, new_offset)
     |      Gives the spectrum an offset value. When plotted in the
     |      plot_absorbance function, the offset value will simply be
     |      added to the spectrum's absorbance values. This allows the
     |      user to vertically shift the spectrum if needed.
     |
     |      offset : (float) the offset for the spectrum, in absorbance
     |               units
     |
     |  cycle_color(self)
     |      Changes the color based on a color cycle
     |
     |  export(self, path=None)
     |      Export the data and attributes
     |
     |  fit_peaks(self, verbose=False, guesses=None, ng=None, ng_lower=None, ng_upper=None, do_scattering=False, fit_lim=(120, 340), custom_components=None)
     |      Finds and fits the peaks in the spectrum by fitting the spectrum with
     |      some number of asymmetric Gaussian functions. The locations of the peaks
     |      as well as the fitted spectrum are returned, but also added to a peaks
     |      and fit parameter of the object. The best fit is saved as a column in
     |      the spectrum's `data` DataFrame parameter.
     |
     |      Parameters:
     |
     |      do_scattering : (boolean) Whether or not to fit using the rayleigh
     |                    scattering function as a part of the fit.
     |      fit_lim_low : (float) the lower limit on the wavelength range used in
     |                    fitting. Defults to 120.
     |      guesses: (list) a list of dictionaries containing the guesses to your
     |               fit. The dictionaries must be of the form: {'lower':, 'guess':,
     |               'upper':} where 'guess' is your guess for the value of a fit
     |               parameter, and 'lower' and 'upper' are lower and upper limits
     |               respectively. Guesses for gaussian fit parameters must be in
     |               groups of three; a, c, and s, where a is the amplitude of the
     |               gaussian, c is the center wavelength, and s is the standard
     |               deviation. If you have `do_baseline` to True, you should
     |               include an additional two parameters *at the start* of p0.
     |               These parameters are m and k, where m controls the steepness of
     |               the scattering curve, and k controls the amplitude. If you have
     |               any custom components, you must include guesses for the
     |               amplitudes of those components at the start of the list, before
     |               your guesses for the baseline.
     |      ng : (tuple or int) The number of gaussians to use in the fit, or lower
     |           and upper limits on how many gaussians to use in the fit.
     |      ng_lower : (int) [Depreciated] The lower limit on the number of
     |                 gaussians to try and fit with.
     |      ng_upper : (int) [Depreciated] The upper limit on the number of
     |                 gaussians to try and fit with.
     |      verbose : (boolean) If true, prints debug and progress statements.
     |                Defaults to False.
     |
     |  flip_visibility(self)
     |      Changes the visibility of the spectrum when plotting. If
     |      the self.visible parameter is false, the plot_absorbance
     |      function will skip plotting this spectrum.
     |
     |  remove_bkgd(self, bkgd_fname)
     |      Removes a background from this spectrum's list of backgrounds
     |
     |      bkgd_name : (str) the name of the background being removed
     |
     |  remove_sample(self, sample_fname)
     |      Removes a sample from this spectrum's list of samples
     |
     |      sample_name : (str) the name of the spectrum being removed
     |
     |  subtract_baseline(self, lim=None, how='min')
     |      Performs a baseline subtraction on the spectrum. This is done just by
     |      shifting all values such that some chosen value is zero. There are two
     |      methods, determined by the how parameter.
     |
     |      lim : (tuple or None) the limits on where the zero point is searched
     |            for. Defaults to None.
     |      how : (str) How to determine the zero point. Acceptable values are
     |            "min", and "right". When "min", the function will find the minimum
     |            absorbance value within the wavelength range set by lim, and shift
     |            the data such that it is zero. When "right", the rightmost
     |            value will be shifted such that it is zero.
     |
     |  update_description(self, new_description)
     |      Change the description of the spectrum
     |
     |  ----------------------------------------------------------------------
     |  Data descriptors defined here:
     |
     |  __dict__
     |      dictionary for instance variables
     |
     |  __weakref__
     |      list of weak references to the object
    


`Spectrum` objects have several attributes. Below are the attributes of the one we just constructed.


```python
spec1.name
```




    'R73780'




```python
spec1.color
```




    'blue'




```python
# these are the calibrated data which are used for plotting and fitting
spec1.data
```




<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>absorbance</th>
      <th>wavelength</th>
    </tr>
    <tr>
      <th>index</th>
      <th></th>
      <th></th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>-0.149512</td>
      <td>110.0</td>
    </tr>
    <tr>
      <th>1</th>
      <td>-0.169499</td>
      <td>111.0</td>
    </tr>
    <tr>
      <th>2</th>
      <td>-0.112865</td>
      <td>112.0</td>
    </tr>
    <tr>
      <th>3</th>
      <td>-0.218492</td>
      <td>113.0</td>
    </tr>
    <tr>
      <th>4</th>
      <td>-23.447676</td>
      <td>114.0</td>
    </tr>
    <tr>
      <th>...</th>
      <td>...</td>
      <td>...</td>
    </tr>
    <tr>
      <th>106</th>
      <td>0.013420</td>
      <td>216.0</td>
    </tr>
    <tr>
      <th>107</th>
      <td>0.012746</td>
      <td>217.0</td>
    </tr>
    <tr>
      <th>108</th>
      <td>0.013698</td>
      <td>218.0</td>
    </tr>
    <tr>
      <th>109</th>
      <td>0.012702</td>
      <td>219.0</td>
    </tr>
    <tr>
      <th>110</th>
      <td>0.012059</td>
      <td>220.0</td>
    </tr>
  </tbody>
</table>
<p>111 rows × 2 columns</p>
</div>




```python
# this is a value which can control a shift in absorbance of the data for
# plotting. More details on offsets are below
spec1.offset
```




    0.0




```python
# this controls if this spectrum is visible in plotting or not. This is not so
# useful when working in jupyter notebook or other code interfaces, but very
# useful in a GUI where you can use checkboxes to control what is plotted.
spec1.visible
```




    True




```python
# a list of the background files associated with this Spectrum
spec1.bkgds
```




    [<spectools.SingleScan at 0x7faa60341a30>,
     <spectools.SingleScan at 0x7faa6081c5f0>]




```python
# a list of the sample files associated with this Spectrum
spec1.samples
```




    [<spectools.SingleScan at 0x7faa61383d70>,
     <spectools.SingleScan at 0x7faa607fa360>]



## Example: Plotting Data

Above, we plotted one spectrum in blue. But the `plot_absorbance` function is designed for plotting several spectra if we want to. In this example, we build a second `Spectrum` object and plot its data alongside the one we made previously. Note that `plot_absorbance` takes a list of `Spectrum` objects to plot. This list can be as long as you like.


```python
bkgd_long1 = path + "R73775.d01"
bkgd_long2 = path + "R73775.d02"
sample_long1 = path + "R73781.d01"
sample_long2 = path + "R73781.d02"

# build long spectrum
spec2 = spectools.Spectrum()
spec2.change_name("R73781")
spec2.add_bkgd(bkgd_long1)
spec2.add_bkgd(bkgd_long2)
spec2.add_sample(sample_long1)
spec2.add_sample(sample_long2)
spec2.change_color("red")
spec2.average_scans()

spectools.plot_absorbance([spec1, spec2], figsize=(7, 5),
                      xlim=(120, 340), ylim=(-0.02, 0.7),
                      save_path="./misc_figures/two_spectrums.svg");
```


    
![png](README_files/output_17_0.png)
    


## Example: Shifting Spectrums

The spectra are not perfectly aligned. This happens normally with the endstation due to a variety of factors, and we can apply offsets when plotting to correct for this. For example below, we change the offset on the longer wavelength spectrum upwards by 0.1:


```python
spec2.change_offset(0.1)

spectools.plot_absorbance([spec1, spec2], figsize=(7, 5),
                      xlim=(120, 340), ylim=(-0.02, 0.7),
                      save_path="./misc_figures/shift_example.svg");
```


    
![png](README_files/output_19_0.png)
    


Calling the `change_offset` function always changes the offset with respect to the data's original absorbance values, not the offset values. If we call it again and pass 0.0 as our offset value, the data in the plot return to where they were originally (the offset is now set to 0, rather than having 0 added to it):


```python
spec2.change_offset(0.0)

spectools.plot_absorbance([spec1, spec2], figsize=(7, 5),
                      xlim=(120, 340), ylim=(-0.02, 0.7),
                      save_path="./misc_figures/shift_example_2.svg");
```


    
![png](README_files/output_21_0.png)
    


## Example: Stitching Spectra

Properly aligned spectra can be stitched together into a single object. This is done by creating a `SitchedSpectrum` which consists of two or more `Spectrum` objects. The `Spectrum` objects are passed to the `StitchedSpectrum` initializer in a list. There can be as many `Spectrum` objects in that list as you need, so you can stitch many spectra together at once. Below is an example where we stitch the two spectra we already made above:


```python
spec2.change_offset(0.002)
stitched = spectools.StitchedSpectrum([spec1, spec2])

spectools.plot_absorbance([stitched], figsize=(7, 5),
                      xlim=(120, 340), ylim=(-0.02, 0.7),
                      save_path="./misc_figures/stitched.svg");
```


    
![png](README_files/output_23_0.png)
    



```python
stitched.name
```




    'R73780-R73781'




```python
stitched.visible
```




    True




```python
stitched.color
```




    'blue'




```python
stitched.offset
```




    0




```python
stitched.samples
```




    [<spectools.SingleScan at 0x7faa61383d70>,
     <spectools.SingleScan at 0x7faa607fa360>,
     <spectools.SingleScan at 0x7faa575ed640>,
     <spectools.SingleScan at 0x7faa5760e990>]




```python
stitched.bkgds
```




    [<spectools.SingleScan at 0x7faa60341a30>,
     <spectools.SingleScan at 0x7faa6081c5f0>,
     <spectools.SingleScan at 0x7faa5f85eea0>,
     <spectools.SingleScan at 0x7faa57603d70>]



## Additional Information on the Stitching Algorithm

The stitching algorithm can do more than just join adjacent spectra. It was also designed to be able to splice higher resolution spectra into other, wider wavelength range spectra. It can stitch any arbitrary number of spectra at any arbitrary wavelength ranges

It operates by iterating through every wavelength point of every spectrum you provide it. At each point, it asks itself "do we already have data at this wavelength in the resultant stitched spectrum we are building?" If the answer is no, the algorithm will add that wavelength and its absorbance value to the resultant stitched spectrum. If the answer is yes, the algorithm will compare the value it already has at that wavelength to the "new" value from the spectrum it is currently looking at. If the new value was taken from a spectrum with higher resolution than the current value's spectrum, it will replace the current value with the new value. If the values were taken using the same resolution, it will check how many samples were taken in each value's spectrum. The value with a higher sample count (i.e. better signal to noise) will be chosen. 

This process prioritizes high resolution spectra, then high sample number spectra, then all other spectra. The result will be a combined spectrum using the highest available resolution and signal to noise at each wavelength range provided to it.

It does not perform any value averaging. If you, like in the above example, have two adjacent spectra taken with the same resolution and number of samples with some wavelength overlap, the stitching algorithm will use the values from the first spectrum in the list provided to it, and switch to the next spectrum when it sees data at wavelengths not in the first spectrum. It does not consider any possible offsets between the spectra, and it does not attempt to average together values in the overlapping region. If that is the behavior you want in your data reduction, you will have to do it yourself.

## Example: Changing Names


```python
stitched.change_name("Propane as deposited at 8K")

spectools.plot_absorbance([stitched], figsize=(7, 5),
                      xlim=(120, 340), ylim=(-0.02, 0.7),
                      save_path="./misc_figures/name_change.svg");
```


    
![png](README_files/output_33_0.png)
    


## Example: Changing Colors


```python
stitched.change_color("green")

spectools.plot_absorbance([stitched], figsize=(7, 5),
                      xlim=(120, 340), ylim=(-0.02, 0.7),
                      save_path="./misc_figures/color_change.svg");
```


    
![png](README_files/output_35_0.png)
    


## Example: Simple Baseline Subtraction

For the baseline subtraction, the minimum value is found in some wavelenght range passed to the function. The entire absorbance data are then shifted such that the minimum is at zero.


```python
stitched.subtract_baseline(lim=(120, 340))

spectools.plot_absorbance([stitched], figsize=(7, 5),
                      xlim=(120, 340), ylim=(-0.02, 0.7),
                      save_path="./misc_figures/baseline_subtract.svg");
```


    
![png](README_files/output_37_0.png)
    


# Fitting

DUVET includes a robust fit function which can handle gaussian fitting, rayleigh scattering, and custom fit components. This section provides the details on each of these fitting types, which can be used concurrently or separately.

But first, it is worth presenting the entire, formal fit function so that we can label our fit parameters. The function contains three terms: one for each of the possible component types (Gaussian functions, custom components, and Rayleigh scattering). The function is shown below:

$$
f(\lambda) = \sum_{i=1}^{n_g} \frac{a_i}{\sqrt{2\pi}\sigma_i} e^{-\frac{1}{2}\left(\frac{\lambda-\lambda_{0, i}}{\sigma_i}\right)^2} + \sum_{j=1}^{n_{cc}}\alpha_{j} C_{j}\left(\lambda\right) + k\ln\left(\frac{1}{1-\frac{m}{\lambda^4}}\right) + b
$$

where:
- $\lambda$ is the wavelength of the light in the spectrum
- $n_g$ is the number of Gaussian functions to fit with
- $a_i$ is the amplitude of each respective Gaussian function
- $\sigma_i$ is the standard deviation of each respective Gaussian function
- $\lambda_{0, i}$ is the central wavelength of each respective Gaussian function
- $n_{cc}$ is the number of custom components included in the fit
- $\alpha_j$ is the amplitude of each respective custom component
- $C_{j}\left(\lambda\right)$ is the respective custom component in the fit, expressed as an array of absorbance numbers with respect to wavelength
- $m$ describes the loss in transmittance due to the scattering
- $k$ is the amplitude of the Rayleigh scattering baseline
- $b$ is a constant absorbance baseline

DUVET automatically adjusts this function to include as many Gaussian functions and/or custom components as the user specifies. All of the parts of the fit function are optional. If the user specifies to use 0 Gaussian functions, that term will be ignored. If the user does not provide custom components to fit with, that term will be ignored. And Rayleigh scattering is not fit by default, and will be ignored unless the user turns it on. The user enables and disables parts of the fit function by providing arguments to the `fit_peaks` Python function of the `Spectrum` and `StitchedSpectrum` classes of the `spectools` module.

The free parameters which are fit with the function are:
- $a_i$ is the amplitude of each respective Gaussian function
- $\sigma_i$ is the standard deviation of each respective Gaussian function
- $\lambda_{0, i}$ is the central wavelength of each respective Gaussian function
- $\alpha_j$ is the amplitude of each respective custom component
- $k$ is the amplitude of the Rayleigh scattering baseline
- $m$ describes the loss in transmittance due to the scattering
- $b$ is a constant absorbance baseline

The user can optionally provide guesses to the values of these parameters. This is done by providing a list of dictionaries to the `fit_peaks` function. Each dictionary in the list corresponds to one parameter. It must include a lower limit value, a guess value, and an upper limit value.

It is important to provide the guesses in the same order as DUVET expects them. Guesses relating to the custom component amplitudes must be provided first. If no custom components are used, no guesses need to be provided to them. Second must come the guesses relating to the rayleigh scattering, in this order: $m$, $k$, $b$. Third are the guesses for the Gaussian functions. They must be given in groups of three, with each group containing $a$, $\lambda_0$, and $\sigma$ in that order.

Examples of the fitting are shown below:

## Example: Fitting with gaussians

You can fit with any arbitrary number of gaussians. If you provide your own guesses, you can only fit up to the number of functions you provide guesses for. Otherwise, you can fit as many gaussians as you want. However, the program will choose the fit with the best reduced chi square, which tends to prefer smaller numbers of free parameters.


```python
import spectools
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import random

# keep things reproducable
random.seed(31415)
# define colors for plotting
colors = ["#dcdcdc", "#2f4f4f", "#a52a2a", "#191970", "#006400", "#bdb76b", "#9acd32",
"#66cdaa", "#ff0000", "#ff8c00", "#ffd700", "#c71585", "#0000cd", "#00ff00",
"#00fa9a", "#00bfff", "#ff00ff", "#dda0dd", "#7b68ee", "#ffa07a"]

def build_spectra(path, bkgd_short1, bkgd_short2, bkgd_long1, bkgd_long2,
                  sample_short1, sample_short2, sample_long1, sample_long2,
                  color="#000001", name=None):
    """
    Builds the spectra as appropriate for this experiment
    """
    # build short spectrum
    spec1 = spectools.Spectrum()
    spec1.change_name(sample_short1[-9:-4])
    spec1.add_bkgd(bkgd_short1)
    spec1.add_bkgd(bkgd_short2)
    spec1.add_sample(sample_short1)
    spec1.add_sample(sample_short2)
    spec1.change_color(color)
    spec1.change_offset(0.0)
    spec1.average_scans()

    # build long spectrum
    spec2 = spectools.Spectrum()
    spec2.change_name(sample_long1[-9:-4])
    spec2.add_bkgd(bkgd_long1)
    spec2.add_bkgd(bkgd_long2)
    spec2.add_sample(sample_long1)
    spec2.add_sample(sample_long2)
    spec2.change_color(color)
    spec2.change_offset(0.0)
    spec2.average_scans()

    stiched = spectools.StitchedSpectrum([spec1, spec2])
    if name:
        stiched.change_name(name)
    return stiched

path = "./raw_data/SergioIoppolo-November2023/20231101/"

bkgd_short1 = path + "R73773.d01"
bkgd_short2 = path + "R73773.d02"
bkgd_long1 = path + "R73775.d01"
bkgd_long2 = path + "R73775.d02"

sample_short1 = path + "R73808.d01"
sample_short2 = path + "R73808.d02"
sample_long1 = path + "R73809.d01"
sample_long2 = path + "R73809.d02"

spec = build_spectra(path, bkgd_short1, bkgd_short2, bkgd_long1, bkgd_long2,
                        sample_short1, sample_short2, sample_long1, sample_long2,
                        color=colors[11], name="200K Propane + 50s 1keV e-")


# fix the end of the spectrum to 0
i = len(spec.data['absorbance'])
spec.change_offset(-1*spec.data['absorbance'][i-1])
```


```python
guesses = [{'lower':0, 'guess':4, 'upper':5},   # amplitude
           {'lower':0, 'guess':135, 'upper':340},   # center
           {'lower':0, 'guess':20, 'upper':340},   # standard deviation
           
           {'lower':0, 'guess':3, 'upper':5},   # amplitude
           {'lower':0, 'guess':185, 'upper':340},   # center
           {'lower':0, 'guess':20, 'upper':340},   # standard deviation
           
           {'lower':0, 'guess':2, 'upper':5},   # amplitude
           {'lower':225, 'guess':240, 'upper':250},   # center
           {'lower':0, 'guess':20, 'upper':340},   # standard deviation
           
           {'lower':0, 'guess':0.4, 'upper':5},   # amplitude
           {'lower':274, 'guess':276, 'upper':279},   # center
           {'lower':0, 'guess':20, 'upper':100},   # standard deviation
           
           {'lower':0, 'guess':0.4, 'upper':5},   # amplitude
           {'lower':296, 'guess':298, 'upper':300},   # center
           {'lower':0, 'guess':20, 'upper':100},   # standard deviation
           
           {'lower':0, 'guess':0.1, 'upper':5},   # amplitude
           {'lower':324, 'guess':326, 'upper':328},   # center
           {'lower':0, 'guess':10, 'upper':100},   # standard deviation
          ]

spec.fit_peaks(verbose=True, ng=6, guesses=guesses, fit_lim=(120, 340))
spectools.plot_fit(spec, plot_peaks=True, xlim=(120, 340),
               ylim=(0, spec.data[spec.data['wavelength']>120]['absorbance'].max()*1.1),
               plot_fit_components=True, save_path="./misc_figures/fit.svg")
```




    (<Axes: ylabel='Absorbance'>, <Axes: xlabel='Wavelength (nm)'>)




    
![png](README_files/output_41_1.png)
    



```python
spec.data
```




<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>wavelength</th>
      <th>absorbance</th>
      <th>best_fit</th>
      <th>residuals</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>110.0</td>
      <td>0.036513</td>
      <td>NaN</td>
      <td>NaN</td>
    </tr>
    <tr>
      <th>1</th>
      <td>111.0</td>
      <td>-0.002350</td>
      <td>NaN</td>
      <td>NaN</td>
    </tr>
    <tr>
      <th>2</th>
      <td>112.0</td>
      <td>0.022638</td>
      <td>NaN</td>
      <td>NaN</td>
    </tr>
    <tr>
      <th>3</th>
      <td>113.0</td>
      <td>0.014045</td>
      <td>NaN</td>
      <td>NaN</td>
    </tr>
    <tr>
      <th>4</th>
      <td>114.0</td>
      <td>0.096445</td>
      <td>NaN</td>
      <td>NaN</td>
    </tr>
    <tr>
      <th>...</th>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
    </tr>
    <tr>
      <th>226</th>
      <td>336.0</td>
      <td>0.024983</td>
      <td>0.025747</td>
      <td>-0.000763</td>
    </tr>
    <tr>
      <th>227</th>
      <td>337.0</td>
      <td>0.025773</td>
      <td>0.025454</td>
      <td>0.000320</td>
    </tr>
    <tr>
      <th>228</th>
      <td>338.0</td>
      <td>0.024884</td>
      <td>0.025194</td>
      <td>-0.000310</td>
    </tr>
    <tr>
      <th>229</th>
      <td>339.0</td>
      <td>0.024810</td>
      <td>0.024970</td>
      <td>-0.000160</td>
    </tr>
    <tr>
      <th>230</th>
      <td>340.0</td>
      <td>0.024115</td>
      <td>NaN</td>
      <td>NaN</td>
    </tr>
  </tbody>
</table>
<p>231 rows × 4 columns</p>
</div>




```python
spec.peaks
```




    [{'peak': 132.1611741407202, 'peak_error': 0.2731847265698752},
     {'peak': 181.52690419394142, 'peak_error': 0.690605496749274},
     {'peak': 247.94058589114866, 'peak_error': 0.9162816149944981},
     {'peak': 277.0422034374177, 'peak_error': 1.2625762611669944},
     {'peak': 297.91489391664334, 'peak_error': 1.3225031759728159},
     {'peak': 325.87360811741803, 'peak_error': 1.597896711501519}]




```python
spec.fit_results
```




    {'reduced_chi_square': 0.5103144021863664,
     'n_gaussians': 6,
     'n_custom_components': 0,
     'fitted_scattering': False,
     'custom_component_parameters': [],
     'scattering_parameters': [],
     'gaussian_parameters': [{'value': 2.442799062655488,
       'error': 0.17661897692225761,
       'parameter': 'amplitude'},
      {'value': 132.1611741407202,
       'error': 0.2731847265698752,
       'parameter': 'center'},
      {'value': 16.781369569150726,
       'error': 0.44411473860083905,
       'parameter': 'std'},
      {'value': 4.32676377266341,
       'error': 0.27031895450146226,
       'parameter': 'amplitude'},
      {'value': 181.52690419394142,
       'error': 0.690605496749274,
       'parameter': 'center'},
      {'value': 30.273467516154355,
       'error': 1.7714852550209894,
       'parameter': 'std'},
      {'value': 1.1974241901062608,
       'error': 0.13804794018989236,
       'parameter': 'amplitude'},
      {'value': 247.94058589114866,
       'error': 0.9162816149944981,
       'parameter': 'center'},
      {'value': 20.23187485980927, 'error': 1.373568495050898, 'parameter': 'std'},
      {'value': 0.12141719220191141,
       'error': 0.05938295294136964,
       'parameter': 'amplitude'},
      {'value': 277.0422034374177,
       'error': 1.2625762611669944,
       'parameter': 'center'},
      {'value': 7.14532897144767, 'error': 1.2594377698210129, 'parameter': 'std'},
      {'value': 0.3733466504767837,
       'error': 0.06501195642506839,
       'parameter': 'amplitude'},
      {'value': 297.91489391664334,
       'error': 1.3225031759728159,
       'parameter': 'center'},
      {'value': 11.989765800030952,
       'error': 2.0443269023581543,
       'parameter': 'std'},
      {'value': 0.07338471576859575,
       'error': 0.02136876681605398,
       'parameter': 'amplitude'},
      {'value': 325.87360811741803,
       'error': 1.597896711501519,
       'parameter': 'center'},
      {'value': 7.39148182018958,
       'error': 1.3145189915494848,
       'parameter': 'std'}],
     'p': array([2.44279906e+00, 1.32161174e+02, 1.67813696e+01, 4.32676377e+00,
            1.81526904e+02, 3.02734675e+01, 1.19742419e+00, 2.47940586e+02,
            2.02318749e+01, 1.21417192e-01, 2.77042203e+02, 7.14532897e+00,
            3.73346650e-01, 2.97914894e+02, 1.19897658e+01, 7.33847158e-02,
            3.25873608e+02, 7.39148182e+00]),
     'pcov': array([[ 3.11942630e-02,  4.03796655e-02,  7.48581857e-02,
             -4.66825348e-02,  1.05842545e-01, -3.03295355e-01,
              2.10821665e-02, -1.34423183e-01,  1.84488475e-01,
             -3.03623911e-03,  7.62481822e-03, -5.99722460e-02,
             -5.77751925e-04,  3.56616554e-03,  1.95796774e-02,
             -2.10122213e-04,  1.42011464e-02, -8.96954592e-03],
            [ 4.03796655e-02,  7.46298948e-02,  8.62435324e-02,
             -6.34923953e-02,  1.44665431e-01, -4.14583095e-01,
              2.85772143e-02, -1.84949341e-01,  2.47938659e-01,
             -4.01136270e-03,  1.02175487e-02, -7.89607057e-02,
             -7.99019680e-04,  5.43898375e-03,  2.53876801e-02,
             -2.75192881e-04,  1.86077920e-02, -1.17644198e-02],
            [ 7.48581857e-02,  8.62435324e-02,  1.97237901e-01,
             -1.06068986e-01,  2.74567649e-01, -6.79498505e-01,
              4.49103396e-02, -2.95699570e-01,  3.81781164e-01,
             -6.04574734e-03,  1.55573923e-02, -1.18644525e-01,
             -1.25705551e-03,  9.25269808e-03,  3.75731911e-02,
             -4.11201456e-04,  2.78181002e-02, -1.76005993e-02],
            [-4.66825348e-02, -6.34923953e-02, -1.06068986e-01,
              7.30723372e-02, -1.42850697e-01,  4.77870771e-01,
             -3.50881585e-02,  2.13042975e-01, -3.17734069e-01,
              5.50127094e-03, -1.33134720e-02,  1.09644537e-01,
              9.15245484e-04, -3.79086114e-03, -3.72342042e-02,
              3.89593295e-04, -2.62975958e-02,  1.65691141e-02],
            [ 1.05842545e-01,  1.44665431e-01,  2.74567649e-01,
             -1.42850697e-01,  4.76935952e-01, -9.13216510e-01,
              5.04073474e-02, -4.00049444e-01,  3.64298038e-01,
             -3.99367989e-03,  1.37719775e-02, -7.15839538e-02,
             -1.73488562e-03,  2.44891672e-02,  1.27145109e-02,
             -2.10578086e-04,  1.44770935e-02, -9.44682561e-03],
            [-3.03295355e-01, -4.14583095e-01, -6.79498505e-01,
              4.77870771e-01, -9.13216510e-01,  3.13816001e+00,
             -2.31066428e-01,  1.40836336e+00, -2.09140904e+00,
              3.60706077e-02, -8.76964176e-02,  7.18220847e-01,
              6.08547679e-03, -2.66036335e-02, -2.42979353e-01,
              2.54877369e-03, -1.72063366e-01,  1.08442406e-01],
            [ 2.10821665e-02,  2.85772143e-02,  4.49103396e-02,
             -3.50881585e-02,  5.04073474e-02, -2.31066428e-01,
              1.90572338e-02, -9.47505382e-02,  1.84819841e-01,
             -3.82452175e-03,  7.34520515e-03, -7.95112091e-02,
             -2.70392892e-04, -5.14208767e-03,  3.08779237e-02,
             -2.94213986e-04,  1.97433222e-02, -1.22685447e-02],
            [-1.34423183e-01, -1.84949341e-01, -2.95699570e-01,
              2.13042975e-01, -4.00049444e-01,  1.40836336e+00,
             -9.47505382e-02,  8.39571998e-01, -7.89757293e-01,
              5.01132222e-03, -4.38493702e-02,  4.75502595e-02,
              6.45776087e-03, -1.24160873e-01,  4.37007164e-02,
             -5.84289419e-06, -1.43988354e-03,  3.69886981e-03],
            [ 1.84488475e-01,  2.47938659e-01,  3.81781164e-01,
             -3.17734069e-01,  3.64298038e-01, -2.09140904e+00,
              1.84819841e-01, -7.89757293e-01,  1.88669041e+00,
             -4.16837742e-02,  7.76320448e-02, -8.71739740e-01,
             -1.99474096e-03, -7.40709375e-02,  3.49424775e-01,
             -3.28112745e-03,  2.20121757e-01, -1.36784475e-01],
            [-3.03623911e-03, -4.01136270e-03, -6.04574734e-03,
              5.50127094e-03, -3.99367989e-03,  3.60706077e-02,
             -3.82452175e-03,  5.01132222e-03, -4.16837742e-02,
              3.52633510e-03,  5.46471885e-02,  7.08488771e-02,
             -3.11368413e-03,  6.36016537e-02, -1.04821969e-01,
              9.33322594e-04, -6.42275346e-02,  4.33125753e-02],
            [ 7.62481822e-03,  1.02175487e-02,  1.55573923e-02,
             -1.33134720e-02,  1.37719775e-02, -8.76964176e-02,
              7.34520515e-03, -4.38493702e-02,  7.76320448e-02,
              5.46471885e-02,  1.59409882e+00,  1.04012329e+00,
             -7.44177646e-02,  1.51633464e+00, -2.22118641e+00,
              1.90584558e-02, -1.30765550e+00,  8.72509085e-01],
            [-5.99722460e-02, -7.89607057e-02, -1.18644525e-01,
              1.09644537e-01, -7.15839538e-02,  7.18220847e-01,
             -7.95112091e-02,  4.75502595e-02, -8.71739740e-01,
              7.08488771e-02,  1.04012329e+00,  1.58618350e+00,
             -5.74695575e-02,  1.27842498e+00, -1.90506550e+00,
              1.61117585e-02, -1.09778018e+00,  7.20879804e-01],
            [-5.77751925e-04, -7.99019680e-04, -1.25705551e-03,
              9.15245484e-04, -1.73488562e-03,  6.08547679e-03,
             -2.70392892e-04,  6.45776087e-03, -1.99474096e-03,
             -3.11368413e-03, -7.44177646e-02, -5.74695575e-02,
              4.22655448e-03, -7.44820639e-02,  1.30156853e-01,
             -1.23261499e-03,  8.59148957e-02, -6.09120306e-02],
            [ 3.56616554e-03,  5.43898375e-03,  9.25269808e-03,
             -3.79086114e-03,  2.44891672e-02, -2.66036335e-02,
             -5.14208767e-03, -1.24160873e-01, -7.40709375e-02,
              6.36016537e-02,  1.51633464e+00,  1.27842498e+00,
             -7.44820639e-02,  1.74901465e+00, -2.25274446e+00,
              1.71677661e-02, -1.15230076e+00,  6.89032674e-01],
            [ 1.95796774e-02,  2.53876801e-02,  3.75731911e-02,
             -3.72342042e-02,  1.27145109e-02, -2.42979353e-01,
              3.08779237e-02,  4.37007164e-02,  3.49424775e-01,
             -1.04821969e-01, -2.22118641e+00, -1.90506550e+00,
              1.30156853e-01, -2.25274446e+00,  4.17927248e+00,
             -4.00236403e-02,  2.79378757e+00, -1.97310574e+00],
            [-2.10122213e-04, -2.75192881e-04, -4.11201456e-04,
              3.89593295e-04, -2.10578086e-04,  2.54877369e-03,
             -2.94213986e-04, -5.84289419e-06, -3.28112745e-03,
              9.33322594e-04,  1.90584558e-02,  1.61117585e-02,
             -1.23261499e-03,  1.71677661e-02, -4.00236403e-02,
              4.56624195e-04, -2.97972232e-02,  2.49375867e-02],
            [ 1.42011464e-02,  1.86077920e-02,  2.78181002e-02,
             -2.62975958e-02,  1.44770935e-02, -1.72063366e-01,
              1.97433222e-02, -1.43988354e-03,  2.20121757e-01,
             -6.42275346e-02, -1.30765550e+00, -1.09778018e+00,
              8.59148957e-02, -1.15230076e+00,  2.79378757e+00,
             -2.97972232e-02,  2.55327390e+00, -1.57152613e+00],
            [-8.96954592e-03, -1.17644198e-02, -1.76005993e-02,
              1.65691141e-02, -9.44682561e-03,  1.08442406e-01,
             -1.22685447e-02,  3.69886981e-03, -1.36784475e-01,
              4.33125753e-02,  8.72509085e-01,  7.20879804e-01,
             -6.09120306e-02,  6.89032674e-01, -1.97310574e+00,
              2.49375867e-02, -1.57152613e+00,  1.72796018e+00]])}




```python
spec.fit_components
```




    [{'parameters': [{'value': 2.442799062655488,
        'error': 0.17661897692225761,
        'parameter': 'amplitude'},
       {'value': 132.1611741407202,
        'error': 0.2731847265698752,
        'parameter': 'center'},
       {'value': 16.781369569150726,
        'error': 0.44411473860083905,
        'parameter': 'std'}],
      'wavelength': 0      110.0
      1      111.0
      2      112.0
      3      113.0
      4      114.0
             ...  
      226    336.0
      227    337.0
      228    338.0
      229    339.0
      230    340.0
      Name: wavelength, Length: 231, dtype: float64,
      'absorbance': 0      0.048397
      1      0.050338
      2      0.052335
      3      0.054375
      4      0.056448
               ...   
      226    0.024115
      227    0.024115
      228    0.024115
      229    0.024115
      230    0.024115
      Name: wavelength, Length: 231, dtype: float64},
     {'parameters': [{'value': 4.32676377266341,
        'error': 0.27031895450146226,
        'parameter': 'amplitude'},
       {'value': 181.52690419394142,
        'error': 0.690605496749274,
        'parameter': 'center'},
       {'value': 30.273467516154355,
        'error': 1.7714852550209894,
        'parameter': 'std'}],
      'wavelength': 0      110.0
      1      111.0
      2      112.0
      3      113.0
      4      114.0
             ...  
      226    336.0
      227    337.0
      228    338.0
      229    339.0
      230    340.0
      Name: wavelength, Length: 231, dtype: float64,
      'absorbance': 0      0.027613
      1      0.027895
      2      0.028195
      3      0.028514
      4      0.028853
               ...   
      226    0.024115
      227    0.024115
      228    0.024115
      229    0.024115
      230    0.024115
      Name: wavelength, Length: 231, dtype: float64},
     {'parameters': [{'value': 1.1974241901062608,
        'error': 0.13804794018989236,
        'parameter': 'amplitude'},
       {'value': 247.94058589114866,
        'error': 0.9162816149944981,
        'parameter': 'center'},
       {'value': 20.23187485980927,
        'error': 1.373568495050898,
        'parameter': 'std'}],
      'wavelength': 0      110.0
      1      111.0
      2      112.0
      3      113.0
      4      114.0
             ...  
      226    336.0
      227    337.0
      228    338.0
      229    339.0
      230    340.0
      Name: wavelength, Length: 231, dtype: float64,
      'absorbance': 0      0.024115
      1      0.024115
      2      0.024115
      3      0.024115
      4      0.024115
               ...   
      226    0.024117
      227    0.024117
      228    0.024116
      229    0.024116
      230    0.024116
      Name: wavelength, Length: 231, dtype: float64},
     {'parameters': [{'value': 0.12141719220191141,
        'error': 0.05938295294136964,
        'parameter': 'amplitude'},
       {'value': 277.0422034374177,
        'error': 1.2625762611669944,
        'parameter': 'center'},
       {'value': 7.14532897144767,
        'error': 1.2594377698210129,
        'parameter': 'std'}],
      'wavelength': 0      110.0
      1      111.0
      2      112.0
      3      113.0
      4      114.0
             ...  
      226    336.0
      227    337.0
      228    338.0
      229    339.0
      230    340.0
      Name: wavelength, Length: 231, dtype: float64,
      'absorbance': 0      0.024115
      1      0.024115
      2      0.024115
      3      0.024115
      4      0.024115
               ...   
      226    0.024115
      227    0.024115
      228    0.024115
      229    0.024115
      230    0.024115
      Name: wavelength, Length: 231, dtype: float64},
     {'parameters': [{'value': 0.3733466504767837,
        'error': 0.06501195642506839,
        'parameter': 'amplitude'},
       {'value': 297.91489391664334,
        'error': 1.3225031759728159,
        'parameter': 'center'},
       {'value': 11.989765800030952,
        'error': 2.0443269023581543,
        'parameter': 'std'}],
      'wavelength': 0      110.0
      1      111.0
      2      112.0
      3      113.0
      4      114.0
             ...  
      226    336.0
      227    337.0
      228    338.0
      229    339.0
      230    340.0
      Name: wavelength, Length: 231, dtype: float64,
      'absorbance': 0      0.024115
      1      0.024115
      2      0.024115
      3      0.024115
      4      0.024115
               ...   
      226    0.024195
      227    0.024176
      228    0.024162
      229    0.024150
      230    0.024141
      Name: wavelength, Length: 231, dtype: float64},
     {'parameters': [{'value': 0.07338471576859575,
        'error': 0.02136876681605398,
        'parameter': 'amplitude'},
       {'value': 325.87360811741803,
        'error': 1.597896711501519,
        'parameter': 'center'},
       {'value': 7.39148182018958,
        'error': 1.3145189915494848,
        'parameter': 'std'}],
      'wavelength': 0      110.0
      1      111.0
      2      112.0
      3      113.0
      4      114.0
             ...  
      226    336.0
      227    337.0
      228    338.0
      229    339.0
      230    340.0
      Name: wavelength, Length: 231, dtype: float64,
      'absorbance': 0      0.024115
      1      0.024115
      2      0.024115
      3      0.024115
      4      0.024115
               ...   
      226    0.025665
      227    0.025391
      228    0.025146
      229    0.024934
      230    0.024753
      Name: wavelength, Length: 231, dtype: float64}]



## Example: Fitting with whatever you want

DUVET also lets you fit with other things than Gaussian functions. For this you can set the `custom_components` parameter in the `fit_peaks` function. The value of `custom_components` should be a list of pandas dataframes, each with at least a wavelength column labelled "wavelength" and an absorbance column labeled "absorbance". They can use any wavelength range, and the wavelength resolution does not have to match your data as DUVET can interpolate.

Let's say that for fun instead of using just the Gaussian functions in the example above, I also decide I want to include a pre-calculated linear function into the fit. I can make my custom component and add it in as shown below:


```python
# make x values for the custom component
X = np.linspace(120, 340, 300)
# make y values for the custom component
Y = [(-0.045/50)*x +0.3 for x in X]

# add the values to a dictionary, then make the dataframe
custom_dict = {
    "wavelength":X,
    "absorbance":Y
}
custom_df = pd.DataFrame(custom_dict)
```


```python
custom_df
```




<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>wavelength</th>
      <th>absorbance</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>120.000000</td>
      <td>0.192000</td>
    </tr>
    <tr>
      <th>1</th>
      <td>120.735786</td>
      <td>0.191338</td>
    </tr>
    <tr>
      <th>2</th>
      <td>121.471572</td>
      <td>0.190676</td>
    </tr>
    <tr>
      <th>3</th>
      <td>122.207358</td>
      <td>0.190013</td>
    </tr>
    <tr>
      <th>4</th>
      <td>122.943144</td>
      <td>0.189351</td>
    </tr>
    <tr>
      <th>...</th>
      <td>...</td>
      <td>...</td>
    </tr>
    <tr>
      <th>295</th>
      <td>337.056856</td>
      <td>-0.003351</td>
    </tr>
    <tr>
      <th>296</th>
      <td>337.792642</td>
      <td>-0.004013</td>
    </tr>
    <tr>
      <th>297</th>
      <td>338.528428</td>
      <td>-0.004676</td>
    </tr>
    <tr>
      <th>298</th>
      <td>339.264214</td>
      <td>-0.005338</td>
    </tr>
    <tr>
      <th>299</th>
      <td>340.000000</td>
      <td>-0.006000</td>
    </tr>
  </tbody>
</table>
<p>300 rows × 2 columns</p>
</div>



Now we have a dataframe with some absorbance values at various wavelengths. Let's use it in a fit:


```python
guesses = [{'lower':0, 'guess':1, 'upper':10}, # amplitude of our custom component
    ]

spec.fit_peaks(verbose=True, ng=0, guesses=guesses, fit_lim=(120, 340),
              custom_components=[custom_df])
spectools.plot_fit(spec, plot_peaks=True, xlim=(120, 340),
               ylim=(0, spec.data[spec.data['wavelength']>120]['absorbance'].max()*1.1),
               plot_fit_components=True, save_path="./misc_figures/fit.svg")
```




    (<Axes: ylabel='Absorbance'>, <Axes: xlabel='Wavelength (nm)'>)




    
![png](README_files/output_50_1.png)
    


As we can see from the residuals, fitting just a line to these data is not the best we could have possibly done. But, if you want to add in your own data to fit with, DUVET can handle it! In this example we created data in the form of a line, but you could just as easily have data from another experiment that you want to use. Just make sure that you format it in terms of wavelength and absorbance, and put it into a pandas dataframe. After that, DUVET doesn't care what the values are.

Once again, we can look at our `fit_results` to extract our amplitude on the custom component we fit with.


```python
spec.fit_results
```




    {'reduced_chi_square': 0.7867730503306898,
     'n_gaussians': 0,
     'n_custom_components': 1,
     'fitted_scattering': False,
     'custom_component_parameters': [{'value': 0.4670949552926718,
       'error': 0.005250810511035509}],
     'scattering_parameters': [],
     'gaussian_parameters': [],
     'p': array([0.46709496]),
     'pcov': array([[2.7571011e-05]])}




```python
spec.offset
```




    -0.024115221965496998




```python
spec.fit_components
```




    [{'parameters': {'value': 0.4670949552926718, 'error': 0.005250810511035509},
      'wavelength': 11     121.0
      12     122.0
      13     123.0
      14     124.0
      15     125.0
             ...  
      225    335.0
      226    336.0
      227    337.0
      228    338.0
      229    339.0
      Name: wavelength, Length: 219, dtype: float64,
      'absorbance': [0.10211296939607989,
       0.10169258393631649,
       0.10127219847655308,
       0.10085181301678968,
       0.10043142755702628,
       0.10001104209726287,
       0.09959065663749946,
       0.09917027117773605,
       0.09874988571797265,
       0.09832950025820925,
       0.09790911479844584,
       0.09748872933868244,
       0.09706834387891904,
       0.09664795841915563,
       0.09622757295939224,
       0.09580718749962881,
       0.09538680203986541,
       0.09496641658010202,
       0.09454603112033862,
       0.0941256456605752,
       0.09370526020081181,
       0.09328487474104839,
       0.09286448928128499,
       0.09244410382152159,
       0.09202371836175817,
       0.09160333290199478,
       0.09118294744223136,
       0.09076256198246796,
       0.09034217652270456,
       0.08992179106294115,
       0.08950140560317775,
       0.08908102014341436,
       0.08866063468365094,
       0.08824024922388755,
       0.08781986376412414,
       0.08739947830436073,
       0.08697909284459733,
       0.08655870738483393,
       0.08613832192507051,
       0.08571793646530712,
       0.0852975510055437,
       0.0848771655457803,
       0.0844567800860169,
       0.0840363946262535,
       0.08361600916649009,
       0.08319562370672669,
       0.08277523824696327,
       0.0823548527871999,
       0.08193446732743648,
       0.08151408186767307,
       0.08109369640790967,
       0.08067331094814627,
       0.08025292548838285,
       0.07983254002861946,
       0.07941215456885604,
       0.07899176910909265,
       0.07857138364932924,
       0.07815099818956583,
       0.07773061272980243,
       0.07731022727003903,
       0.07688984181027561,
       0.07646945635051222,
       0.0760490708907488,
       0.07562868543098543,
       0.07520829997122201,
       0.07478791451145861,
       0.0743675290516952,
       0.07394714359193179,
       0.07352675813216838,
       0.07310637267240498,
       0.07268598721264158,
       0.07226560175287816,
       0.07184521629311477,
       0.07142483083335135,
       0.07100444537358795,
       0.07058405991382455,
       0.07016367445406115,
       0.06974328899429774,
       0.06932290353453434,
       0.06890251807477094,
       0.06848213261500755,
       0.06806174715524413,
       0.06764136169548073,
       0.06722097623571732,
       0.06680059077595392,
       0.0663802053161905,
       0.0659598198564271,
       0.0655394343966637,
       0.06511904893690029,
       0.06469866347713689,
       0.06427827801737349,
       0.06385789255761008,
       0.06343750709784667,
       0.06301712163808326,
       0.06259673617831986,
       0.06217635071855647,
       0.061755965258793066,
       0.06133557979902966,
       0.06091519433926626,
       0.06049480887950286,
       0.06007442341973944,
       0.059654037959976036,
       0.05923365250021263,
       0.05881326704044923,
       0.05839288158068581,
       0.05797249612092241,
       0.057552110661159006,
       0.0571317252013956,
       0.0567113397416322,
       0.056290954281868796,
       0.05587056882210539,
       0.05545018336234199,
       0.05502979790257857,
       0.05460941244281518,
       0.05418902698305178,
       0.05376864152328837,
       0.05334825606352497,
       0.05292787060376156,
       0.05250748514399816,
       0.05208709968423475,
       0.05166671422447135,
       0.051246328764707944,
       0.05082594330494454,
       0.05040555784518113,
       0.04998517238541772,
       0.04956478692565432,
       0.04914440146589091,
       0.04872401600612751,
       0.04830363054636411,
       0.047883245086600704,
       0.04746285962683731,
       0.0470424741670739,
       0.046622088707310494,
       0.04620170324754709,
       0.04578131778778368,
       0.04536093232802028,
       0.044940546868256874,
       0.04452016140849347,
       0.04409977594873006,
       0.04367939048896666,
       0.043259005029203254,
       0.04283861956943985,
       0.042418234109676434,
       0.04199784864991303,
       0.04157746319014963,
       0.041157077730386224,
       0.04073669227062282,
       0.04031630681085943,
       0.039895921351096014,
       0.03947553589133261,
       0.03905515043156921,
       0.038634764971805804,
       0.038214379512042394,
       0.03779399405227899,
       0.03737360859251559,
       0.036953223132752185,
       0.036532837672988774,
       0.03611245221322537,
       0.03569206675346198,
       0.035271681293698565,
       0.03485129583393516,
       0.03443091037417176,
       0.034010524914408355,
       0.03359013945464494,
       0.03316975399488154,
       0.03274936853511814,
       0.03232898307535472,
       0.031908597615591325,
       0.03148821215582792,
       0.031067826696064508,
       0.030647441236301115,
       0.030227055776537712,
       0.029806670316774315,
       0.029386284857010902,
       0.02896589939724749,
       0.028545513937484095,
       0.02812512847772069,
       0.02770474301795728,
       0.027284357558193882,
       0.026863972098430475,
       0.02644358663866706,
       0.026023201178903662,
       0.02560281571914026,
       0.025182430259376845,
       0.024762044799613445,
       0.024341659339850042,
       0.02392127388008665,
       0.023500888420323243,
       0.023080502960559832,
       0.022660117500796436,
       0.022239732041033026,
       0.021819346581269612,
       0.021398961121506216,
       0.020978575661742813,
       0.020558190201979396,
       0.020137804742216,
       0.019717419282452596,
       0.019297033822689182,
       0.018876648362925783,
       0.01845626290316238,
       0.01803587744339897,
       0.017615491983635566,
       0.017195106523872163,
       0.01677472106410877,
       0.016354335604345363,
       0.015933950144581953,
       0.015513564684818553,
       0.015093179225055148,
       0.014672793765291734,
       0.014252408305528336,
       0.013832022845764935,
       0.013411637386001518,
       0.012991251926238118,
       0.012570866466474716,
       0.012150481006711305,
       0.011730095546947901,
       0.011309710087184505,
       0.01088932462742109,
       0.0104689391676577]}]



## Fitting Organization

When you provide guesses, it is important to do so in the right order. DUVET does not know what number you want to use as an amplitude, or standard deviation, or whatever else, but expects these values to come in a specific order. The order is: custom component amplitudes, Rayleigh scattering parameters, and Gaussian function parameters.

The example list of guesses below shows the expected order of guesses for a fit using two custom components, Rayleigh scattering correction, and three Gaussians:


```python
guesses = [# custom component parameters come first
           {'lower':0, 'guess':4, 'upper':5},   # amplitude
           {'lower':0, 'guess':2, 'upper':3},   # amplitude

           # Rayleigh scattering parameters are second
           {'lower':0, 'guess':4, 'upper':5},   # m
           {'lower':0, 'guess':4, 'upper':5},   # k
           {'lower':0, 'guess':4, 'upper':5},   # b

           # Gaussian parameters come last, grouped in threes
           {'lower':0, 'guess':4, 'upper':5},   # amplitude
           {'lower':0, 'guess':135, 'upper':340},   # center
           {'lower':0, 'guess':20, 'upper':340},   # standard deviation
           
           {'lower':0, 'guess':3, 'upper':5},   # amplitude
           {'lower':0, 'guess':185, 'upper':340},   # center
           {'lower':0, 'guess':20, 'upper':340},   # standard deviation
           
           {'lower':0, 'guess':2, 'upper':5},   # amplitude
           {'lower':225, 'guess':240, 'upper':250},   # center
           {'lower':0, 'guess':20, 'upper':340},   # standard deviation
          ]
```

DUVET organizes your guesses by first checking how many custom components you have provided to the fit function, labelling that number as $n$, and taking that many of the dictionaries in the list of guesses as the guesses on the custom component amplitudes. It then checks if you have enabled scattering fitting or not. If yes, it will take the next three dictionaries in the list of guesses as the guesses on the Rayleigh scattering parameters. It then takes the rest of the provided dictionaries in the guesses list as the guesses on the Gaussian components, if any. It groups those into threes, each with an amplitude, a center, and a standard deviation in that order.

If you do not provide guesses in the expected order, you may get a different fit function than you want, or the fit may not work at all.

## Difference in Plotting Functions

DUVET includes two plotting functions: `plot_absorbance` and `plot_fit`. They serve different purposes.

`plot_absorbance` takes a list of `Spectrum` or `StitchedSpectrum` objects and plots their absorbance vs wavelength. It is good for plotting several spectra which you wish to compare.

`plot_fit` takes a single `Spectrum` or `StitchedSpectrum` object and plots the fit which has been made to its absorbance, if any such fit has been made. It is good for seeing the components which went into the fit.

The plotting functions take similar, but different parameters. I recommend running the `help()` funciton on them to see the full list of parameters they take, and how they can be customized.

Remember also that DUVET preserves all of the data associated with your spectra as attributes of the `Spectrum` or `SitchedSpectrum` objects you have created. You can always access these attributes (see examples above), take the data, and plot them yourself if you have your own preferred plot style, or need to take additional analysis steps.

# Deposition Time Scans

Spectra are not the only data taken at the UV endstation. It is also necessary to monitor the deposition of an ice with the deposition time scans. These can then be fit, and optics principles can be used to determine the dosing rate and index of refraction of the ice. This is done using `deptools.py`, for deposition tools.


```python
import deptools
```

`deptools` has only one class: `DepositionTimeScan`. It is initialized by giving it the data file of some deposition time scan. The data can then be plotted with `plot_timescan()`


```python
# create the DepositionTimeScan object
path = "./raw_data/SergioIoppolo-November2023/20231101/T73776.dat"
dep = deptools.DepositionTimeScan(path)

# plot it
deptools.plot_timescan(dep, save_path="./misc_figures/deposition_fit.svg")
```




    <Axes: xlabel='Time (seconds)', ylabel='Ch2 Signal (volts)'>




    
![png](README_files/output_62_1.png)
    


Finding the dosing rate is then (in principle) very easy. All you need to do is run `find_dowing_rate()` and give the function a few parameters, all of which are optional for the function itself, but likely necessary to get a good fit.

The first of these is `guesses` which contains the guesses for the fitted parameters. It is structured the same way as the guesses for spectrum fitting. It should be a list where each item in the list is a dictionary containing a lower and upper limit on the parameter, and a guess. There are five parameters that are fit every time. These parameters are called `m`, `c`, `xc`, `w`, and `n`. The function being fit with these parameters is shown below:

$$
f\left(x\right) = mx + c + \left(c\frac{n-1}{n+1}\right)\sin\left(\frac{x-x_c}{w}\right)
$$

The function is the combination of a line and a sine wave. Parameters `m` and `c` describe the slope and y-intercept of the line component respectively. Parameter `n` describes the index of refraction of the deposited ice, parameter `xc` describes the x-shift $x_c$, and parameter `w` describes the 'wavelength' of the sine wave (note that the wavelength in this function has units of time). Note that the expression $\left(c\frac{n-1}{n+1}\right)$ is a constant that describes the amplitude of the sine wave. The function is not fit directly to the raw data, but rather to gaussian smoothed data. This helps avoid broken fits when the time range is small.

The next important parameters are `t_start` and `t_end` which are the start and end times of the deposition in seconds. As seen in the example file above, the entire file does not represent the deposition. In the example, the deposition starts at roughly 1020 seconds and ends at roughly 1700 seconds. Trying to use the above function to fit any of the data outside that range will either break or give a nonsense result, so these parameters are very important and should not be omitted.

The next parameter is `theta_degrees` which describes in degrees the angle of incidence between the laser and the substrate. By default this is 22 and should not be changed unless the physical setup of the chamber has been changed.

Finally, there is the parameter `verbose`, which can be true or false. If true, the function will print extra statements with the values of the fitted parameters.



```python
# importing numpy so we can set the limits on the parameters to infinity
import numpy as np

# setup our guesses. These are the same as the default guesses if none are provided
guesses = [{'lower':-np.inf, 'guess':3e-6, 'upper':np.inf}, # m
           {'lower':-np.inf, 'guess':0, 'upper':np.inf}, # c
           {'lower':-np.inf, 'guess':200, 'upper':np.inf}, # xc
           {'lower':0, 'guess':300, 'upper':np.inf}, # w
           {'lower':1, 'guess':1.2, 'upper':4.1} # n
            ]

# fit the data and get the dosing rate
dep.find_deposition_rate(guesses=guesses, t_start=1020, t_end=1700, verbose=True)
deptools.plot_timescan(dep, save_path="./misc_figures/deposition_fit.svg")
```

    The fit suceeded with a reduced chi square of [1m9.551e-05[0m
    The deposition rate is [1m0.586 +- 0.001 nm/s[0m
    The ice's index of refraction is [1m1.108 +- 0.000[0m
    The other fitted values are:
    'm' : 0.000 +- 0.000
    'c' : 0.175 +- 0.000
    'tc' : 505.946 +- 0.674
    'w' : 258.601 +- 0.213





    <Axes: xlabel='Time (seconds)', ylabel='Ch2 Signal (volts)'>




    
![png](README_files/output_64_2.png)
    


Now that you have the deposition rate, you can easily find out how much ice was deposited over some given time. This is just multiplying the rate by the deposition time, but there is a built in function to do this for you and handle the associated error more conveniently than by hand. This function is `find_thickness` and takes two parameters. The first is `dep_time`, the deposition time in seconds, and the second is `verbose`, whether or not to print extra statements. The function returns the deposited ice thickness in nanometers as well as its error.


```python
thickness, error = dep.find_thickness(dep_time=680, verbose=True)
```

    The ice deposited for 680 seconds will be [1m398.747 +- 0.561 nm [0mthick.


That is a very thick ice. In our experiments, we only wanted an ice of around 10 nm thick. The timescan above was taken just in order to measure the deposition rate, not actually do the deposition. When we deposited the ice we experimented on, we only deposited for 20 seconds.


```python
thickness, error = dep.find_thickness(dep_time=20, verbose=True)
```

    The ice deposited for 20 seconds will be [1m11.728 +- 0.017 nm [0mthick.


This gave roughly the desired thickness, as we can see here. But why not just fit the deposition scan of the ice we actually used? A deposition time of only 20 seconds is far too short to generate a fittable sine curve like the one above. Further, the user might not yet know how long they want to deposit for, only how thick of an ice they want to eventually have. The deposition rate must be found first. This is also why the program does not automatically calculate the thickness of the deposited ice when you run `find_deposition_rate()`.

But what about that user who knows what thickness of ice they want, but not how long to deposit for? `deptools` can also calculate that in much the same way as finding the thickness:


```python
time, error = dep.find_deposition_time(thickness=10, verbose=True)
```

    The ice deposited to 10 nm will take [1m17.053 +- 0.024 seconds[0m.


Finally, what about exporting all of these parameters? That is easily done with the `export` function, which will save the fitted parameters to a csv file at a specified path:


```python
dep.export("./misc_figures/deposition_fit.csv")
```

if we now read that csv file we will see:


```python
import pandas as pd

df = pd.read_csv("./misc_figures/deposition_fit.csv")
df
```




<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>name</th>
      <th>value</th>
      <th>error</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>m</td>
      <td>0.000003</td>
      <td>6.056960e-08</td>
    </tr>
    <tr>
      <th>1</th>
      <td>c</td>
      <td>0.174932</td>
      <td>8.114540e-05</td>
    </tr>
    <tr>
      <th>2</th>
      <td>tc</td>
      <td>505.945931</td>
      <td>6.737161e-01</td>
    </tr>
    <tr>
      <th>3</th>
      <td>w</td>
      <td>258.601084</td>
      <td>2.134565e-01</td>
    </tr>
    <tr>
      <th>4</th>
      <td>n</td>
      <td>1.108467</td>
      <td>1.723485e-04</td>
    </tr>
    <tr>
      <th>5</th>
      <td>deposition rate (nm/s)</td>
      <td>0.586392</td>
      <td>8.254277e-04</td>
    </tr>
    <tr>
      <th>6</th>
      <td>refractive index</td>
      <td>1.108467</td>
      <td>1.723485e-04</td>
    </tr>
    <tr>
      <th>7</th>
      <td>redchi2</td>
      <td>0.000096</td>
      <td>NaN</td>
    </tr>
  </tbody>
</table>
</div>




```python

```


```python

```

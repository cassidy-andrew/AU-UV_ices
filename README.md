# DUVET Overview
**D**anish **UV** **E**nd-station **T**ool

This tool is designed to help you manage data obtained at the AU-UV endstation of the ASTRID2 synchrotron at Aarhus Univeristy, in Denmark.
Its current main functionality is to read the data files produced by the endstation, calculate absorbances, and produce plots of absorbance.
It can also fit the absorbance data with gaussian functions as a first step in your data analysis.

## Dependencies

To use DUVET you must have python version 3.12.3 or higher.


DUVET relies on several python packages, most of which are very standard for python data analysis workflows. They are listed below, along with the version I am running in my own development environment. But I expect the latest versions of each to be compatible.

- **numpy** (version 1.26.4)
- **pandas** (version 2.2.2)
- **matplotlib** (version 3.8.4)
- **serial** (version 0.0.97)
- **scipy** (version 1.13.1)
- **PyQt5** (version 5.15.9)
- **pyqtgraph** (version 0.13.7)
- **pyqt_color_picker** (version 0.0.20)

# Reading, Calibrating, and Displaying Spectra

The tools for working with spectral data are all in the `specTools` module, which is located inside the `Tools` folder. If your working directory is the main directory of DUVET (i.e., you have duvet.py in the same folder as your current workbook or program), you can import specTools as follows:


```python
import sys
sys.path.insert(0, 'Tools')
import specTools
#help(specTools)
```

You can run `help(specTools)` to see a full summary of the classes and methods. 

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
spec1 = specTools.Spectrum()
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
specTools.plot_absorbance([spec1], figsize=(7, 5),
                      xlim=(120, 340), ylim=(-0.02, 0.7),
                      save_path="./misc_figures/one_spectrum.svg");
```


    
![png](README_files/output_8_0.png)
    


By running `help` on the `Spectrum` object you can see all its methods:


```python
help(spec1)
```

    Help on Spectrum in module specTools object:
    
    class Spectrum(builtins.object)
     |  Spectrum(debug=False, datapath=None)
     |
     |  Represents a spectrum, so the average of one or more scans
     |
     |  Parameters belonging to the fully constructed object:
     |
     |      baseline_p : (list) parameters from the fit of the rayleigh scattering
     |                   baseline. None until subtract_baseline() has been run.
     |      bkgd : (pandas.DataFrame) The averaged background data.
     |      bkgds : (list) a list of SingleSpectrum objects that make up
     |              the backgrounds.
     |      changelog : (str) a string which contains the history of the data. Every
     |                  time a function is called, a line is written to describe
     |                  what happened and at what time. This is then added to the
     |                  header of a file during export.
     |      cindex : (int) the index of the current position in the color cycle for
     |               color cycling.
     |      color : (str) the hex color used for plotting this spectrum.
     |      _comps : (list) a list of custom component dataframes used for fitting
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
     |      samples : (list) a list of SingleSpectrum objects that make up the
     |                 samples.
     |      scans : (list) a list of SingleScan objects that will be
     |              averaged together to make this spectrum.
     |      visible : (boolean) whether the spectrum should appear in
     |                the plot generated by plot_absorbance() or not.
     |                Defaults to True.
     |
     |  Methods defined here:
     |
     |  __init__(self, debug=False, datapath=None)
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
# a list of the backgrounds associated with this Spectrum
spec1.bkgds
```




    [<specTools.SingleScan at 0x7f1b9219d8b0>,
     <specTools.SingleScan at 0x7f1c18700fe0>]




```python
# a list of the samples associated with this Spectrum
spec1.samples
```




    [<specTools.SingleScan at 0x7f1b92e5a2a0>,
     <specTools.SingleScan at 0x7f1b921d71d0>]



As you can see above, printing the `bkgds` and `samples` attributes of the spectrum object gives a strange output. This is because `specTools` configures your individual scan data with `SingleSpectrum` objects. These are discussed in more detail later.

## Example: Plotting Data

Above, we plotted one spectrum in blue. But the `plot_absorbance` function is designed for plotting several spectra if we want to. In this example, we build a second `Spectrum` object and plot its data alongside the one we made previously. Note that `plot_absorbance` takes a list of `Spectrum` objects to plot. This list can be as long as you like.


```python
bkgd_long1 = path + "R73775.d01"
bkgd_long2 = path + "R73775.d02"
sample_long1 = path + "R73781.d01"
sample_long2 = path + "R73781.d02"

# build long spectrum
spec2 = specTools.Spectrum()
spec2.change_name("R73781")
spec2.add_bkgd(bkgd_long1)
spec2.add_bkgd(bkgd_long2)
spec2.add_sample(sample_long1)
spec2.add_sample(sample_long2)
spec2.change_color("red")
spec2.average_scans()

specTools.plot_absorbance([spec1, spec2], figsize=(7, 5),
                      xlim=(120, 340), ylim=(-0.02, 0.7),
                      save_path="./misc_figures/two_spectrums.svg");
```


    
![png](README_files/output_21_0.png)
    


## Example: Shifting Spectrums

The spectra are not perfectly aligned. This happens normally with the endstation due to a variety of factors, and we can apply offsets when plotting to correct for this. For example below, we change the offset on the longer wavelength spectrum upwards by 0.1:


```python
spec2.change_offset(0.1)

specTools.plot_absorbance([spec1, spec2], figsize=(7, 5),
                      xlim=(120, 340), ylim=(-0.02, 0.7),
                      save_path="./misc_figures/shift_example.svg");
```


    
![png](README_files/output_23_0.png)
    


A new column in the `data` attribute dataframe will show the offset absorbance:


```python
spec2.data
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
      <th>offset absorbance</th>
    </tr>
    <tr>
      <th>index</th>
      <th></th>
      <th></th>
      <th></th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>0.011248</td>
      <td>210.0</td>
      <td>0.111248</td>
    </tr>
    <tr>
      <th>1</th>
      <td>0.011132</td>
      <td>211.0</td>
      <td>0.111132</td>
    </tr>
    <tr>
      <th>2</th>
      <td>0.010637</td>
      <td>212.0</td>
      <td>0.110637</td>
    </tr>
    <tr>
      <th>3</th>
      <td>0.010427</td>
      <td>213.0</td>
      <td>0.110427</td>
    </tr>
    <tr>
      <th>4</th>
      <td>0.010252</td>
      <td>214.0</td>
      <td>0.110252</td>
    </tr>
    <tr>
      <th>...</th>
      <td>...</td>
      <td>...</td>
      <td>...</td>
    </tr>
    <tr>
      <th>126</th>
      <td>0.004211</td>
      <td>336.0</td>
      <td>0.104211</td>
    </tr>
    <tr>
      <th>127</th>
      <td>0.003718</td>
      <td>337.0</td>
      <td>0.103718</td>
    </tr>
    <tr>
      <th>128</th>
      <td>0.004022</td>
      <td>338.0</td>
      <td>0.104022</td>
    </tr>
    <tr>
      <th>129</th>
      <td>0.004216</td>
      <td>339.0</td>
      <td>0.104216</td>
    </tr>
    <tr>
      <th>130</th>
      <td>0.004440</td>
      <td>340.0</td>
      <td>0.104440</td>
    </tr>
  </tbody>
</table>
<p>131 rows × 3 columns</p>
</div>



Calling the `change_offset` function always changes the offset with respect to the data's original absorbance values, not the offset values. If we call it again and pass 0.0 as our offset value, the data in the plot return to where they were originally (the offset is now set to 0, rather than having 0 added to it):


```python
spec2.change_offset(0.0)

specTools.plot_absorbance([spec1, spec2], figsize=(7, 5),
                      xlim=(120, 340), ylim=(-0.02, 0.7),
                      save_path="./misc_figures/shift_example_2.svg");
```


    
![png](README_files/output_27_0.png)
    


## Example: Stitching Spectra

Properly aligned spectra can be stitched together into a single object. This is done by creating a `SitchedSpectrum` which consists of two or more `Spectrum` objects. The `Spectrum` objects are passed to the `StitchedSpectrum` initializer in a list. There can be as many `Spectrum` objects in that list as you need, so you can stitch many spectra together at once. Below is an example where we stitch the two spectra we already made above:

Note! You must first align your spectra by changing one's offset before stitching. A previous version of the stitching algorithm did this for you, but that has been depreciated.


```python
spec2.change_offset(0.002)
stitched = specTools.StitchedSpectrum([spec1, spec2])

specTools.plot_absorbance([stitched], figsize=(7, 5),
                      xlim=(120, 340), ylim=(-0.02, 0.7),
                      save_path="./misc_figures/stitched.svg");
```


    
![png](README_files/output_29_0.png)
    



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




    [<specTools.SingleScan at 0x7f1b92e5a2a0>,
     <specTools.SingleScan at 0x7f1b921d71d0>,
     <specTools.SingleScan at 0x7f1b89cb97c0>,
     <specTools.SingleScan at 0x7f1b89ce2000>]




```python
stitched.bkgds
```




    [<specTools.SingleScan at 0x7f1b9219d8b0>,
     <specTools.SingleScan at 0x7f1c18700fe0>,
     <specTools.SingleScan at 0x7f1b91f0f9e0>,
     <specTools.SingleScan at 0x7f1b89c6a6f0>]



## Additional Information on the Stitching Algorithm

The stitching algorithm can do more than just join adjacent spectra. It was also designed to be able to splice higher resolution spectra into other, wider wavelength range spectra. It can stitch any arbitrary number of spectra at any arbitrary wavelength ranges

It operates by iterating through every wavelength point of every spectrum you provide it. At each point, it asks itself "do we already have data at this wavelength in the resultant stitched spectrum we are building?" If the answer is no, the algorithm will add that wavelength and its absorbance value to the resultant stitched spectrum. If the answer is yes, the algorithm will compare the value it already has at that wavelength to the "new" value from the spectrum it is currently looking at. If the new value was taken from a spectrum with higher resolution than the current value's spectrum, it will replace the current value with the new value. If the values were taken using the same resolution, it will check how many samples were taken in each value's spectrum. The value with a higher sample count (i.e. better signal to noise) will be chosen. 

This process prioritizes high resolution spectra, then high sample number spectra, then all other spectra. The result will be a combined spectrum using the highest available resolution and signal to noise at each wavelength range provided to it.

It does not perform any value averaging. If you, like in the above example, have two adjacent spectra taken with the same resolution and number of samples with some wavelength overlap, the stitching algorithm will use the values from the first spectrum in the list provided to it, and switch to the next spectrum when it sees data at wavelengths not in the first spectrum. It does not consider any possible offsets between the spectra, and it does not attempt to average together values in the overlapping region. If that is the behavior you want in your data reduction, you will have to do it yourself.

## Example: Changing Names


```python
stitched.change_name("Some cool VUV data!")

specTools.plot_absorbance([stitched], figsize=(7, 5),
                      xlim=(120, 340), ylim=(-0.02, 0.7),
                      save_path="./misc_figures/name_change.svg");
```


    
![png](README_files/output_39_0.png)
    


## Example: Changing Colors


```python
stitched.change_color("green")

specTools.plot_absorbance([stitched], figsize=(7, 5),
                      xlim=(120, 340), ylim=(-0.02, 0.7),
                      save_path="./misc_figures/color_change.svg");
```


    
![png](README_files/output_41_0.png)
    


## Example: Simple Baseline Subtraction

For the baseline subtraction, the minimum value is found in some wavelenght range passed to the function. The entire absorbance data are then shifted such that the minimum is at zero.


```python
stitched.subtract_baseline(lim=(120, 340))

specTools.plot_absorbance([stitched], figsize=(7, 5),
                      xlim=(120, 340), ylim=(-0.02, 0.7),
                      save_path="./misc_figures/baseline_subtract.svg");
```


    
![png](README_files/output_43_0.png)
    


## `SingleSpectrum` Objects

In order to make many of the user-interface features easier to program, `specTools` stores the data from your individual data scan files (i.e. those ending in .d01, .d02, etc) in `SingleScan` objects. Each such object represents one scan, hence the name! They do not distinguish between backgrounds and samples - that is done at the level of the `Spectrum` object.

We can have a look at one of the `SingleScan`s that was created in the background earlier:


```python
this_singleScan = spec1.bkgds[0]
this_singleScan.data
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
      <th>Lambda</th>
      <th>Keith/nA</th>
      <th>Ch1/volts</th>
      <th>Ch2/volts</th>
      <th>Ch3/volts</th>
      <th>Z_Motor</th>
      <th>Beam_current</th>
      <th>temperature</th>
      <th>GC_Pres</th>
      <th>Time</th>
      <th>UBX_x</th>
      <th>UBX_y</th>
      <th>nor_signal</th>
      <th>wavelength</th>
      <th>av_signal</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>110.0</td>
      <td>-0.00049</td>
      <td>-0.00058</td>
      <td>0.0006</td>
      <td>-0.0001</td>
      <td>-12.6822</td>
      <td>180.0957</td>
      <td>-50.16</td>
      <td>0.0</td>
      <td>10:49:09</td>
      <td>-0.002211</td>
      <td>-0.001252</td>
      <td>-0.000490</td>
      <td>110.0</td>
      <td>-0.000490</td>
    </tr>
    <tr>
      <th>1</th>
      <td>111.0</td>
      <td>-0.00070</td>
      <td>-0.00058</td>
      <td>0.0006</td>
      <td>-0.0001</td>
      <td>-12.4759</td>
      <td>180.0224</td>
      <td>-50.16</td>
      <td>0.0</td>
      <td>10:49:11</td>
      <td>-0.002494</td>
      <td>-0.001280</td>
      <td>-0.000700</td>
      <td>111.0</td>
      <td>-0.000700</td>
    </tr>
    <tr>
      <th>2</th>
      <td>112.0</td>
      <td>-0.00061</td>
      <td>-0.00058</td>
      <td>0.0006</td>
      <td>-0.0001</td>
      <td>-12.2696</td>
      <td>179.9491</td>
      <td>-50.16</td>
      <td>0.0</td>
      <td>10:49:14</td>
      <td>-0.002488</td>
      <td>-0.001270</td>
      <td>-0.000610</td>
      <td>112.0</td>
      <td>-0.000610</td>
    </tr>
    <tr>
      <th>3</th>
      <td>113.0</td>
      <td>-0.00057</td>
      <td>-0.00058</td>
      <td>0.0006</td>
      <td>-0.0001</td>
      <td>-12.0632</td>
      <td>179.8666</td>
      <td>-50.16</td>
      <td>0.0</td>
      <td>10:49:16</td>
      <td>-0.002325</td>
      <td>-0.001573</td>
      <td>-0.000570</td>
      <td>113.0</td>
      <td>-0.000570</td>
    </tr>
    <tr>
      <th>4</th>
      <td>114.0</td>
      <td>0.00296</td>
      <td>-0.00058</td>
      <td>0.0007</td>
      <td>-0.0001</td>
      <td>-11.8568</td>
      <td>182.7076</td>
      <td>-50.16</td>
      <td>0.0</td>
      <td>10:49:38</td>
      <td>-0.002308</td>
      <td>-0.001689</td>
      <td>0.002916</td>
      <td>114.0</td>
      <td>0.002916</td>
    </tr>
    <tr>
      <th>...</th>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
    </tr>
    <tr>
      <th>106</th>
      <td>216.0</td>
      <td>1.55973</td>
      <td>-0.00057</td>
      <td>0.0006</td>
      <td>-0.0001</td>
      <td>9.5375</td>
      <td>183.4408</td>
      <td>-50.12</td>
      <td>0.0</td>
      <td>10:54:41</td>
      <td>-0.002736</td>
      <td>-0.001790</td>
      <td>1.530474</td>
      <td>216.0</td>
      <td>1.530474</td>
    </tr>
    <tr>
      <th>107</th>
      <td>217.0</td>
      <td>1.53702</td>
      <td>-0.00057</td>
      <td>0.0006</td>
      <td>-0.0001</td>
      <td>9.7506</td>
      <td>183.3675</td>
      <td>-50.12</td>
      <td>0.0</td>
      <td>10:54:43</td>
      <td>-0.002338</td>
      <td>-0.001720</td>
      <td>1.508793</td>
      <td>217.0</td>
      <td>1.508793</td>
    </tr>
    <tr>
      <th>108</th>
      <td>218.0</td>
      <td>1.51776</td>
      <td>-0.00057</td>
      <td>0.0006</td>
      <td>-0.0001</td>
      <td>9.9638</td>
      <td>183.3033</td>
      <td>-50.16</td>
      <td>0.0</td>
      <td>10:54:46</td>
      <td>-0.002471</td>
      <td>-0.001617</td>
      <td>1.490409</td>
      <td>218.0</td>
      <td>1.490409</td>
    </tr>
    <tr>
      <th>109</th>
      <td>219.0</td>
      <td>1.49952</td>
      <td>-0.00057</td>
      <td>0.0006</td>
      <td>-0.0001</td>
      <td>10.1770</td>
      <td>183.2117</td>
      <td>-50.12</td>
      <td>0.0</td>
      <td>10:54:48</td>
      <td>-0.002172</td>
      <td>-0.001392</td>
      <td>1.473233</td>
      <td>219.0</td>
      <td>1.473233</td>
    </tr>
    <tr>
      <th>110</th>
      <td>220.0</td>
      <td>1.47580</td>
      <td>-0.00057</td>
      <td>0.0006</td>
      <td>-0.0001</td>
      <td>10.3903</td>
      <td>183.1384</td>
      <td>-50.16</td>
      <td>0.0</td>
      <td>10:54:51</td>
      <td>-0.002110</td>
      <td>-0.001795</td>
      <td>1.450510</td>
      <td>220.0</td>
      <td>1.450510</td>
    </tr>
  </tbody>
</table>
<p>111 rows × 15 columns</p>
</div>




```python
this_singleScan.fname
```




    './raw_data/SergioIoppolo-November2023/20231101/R73773.d01'



You can see that the `.data` attribute of this `SingleScan` object is all the same data as in the file `R73773.d01` we used earlier, as one of the backgrounds of `spec1`.

All of the other functions and attributes of a `SingleScan` object are related to plotting within the "edit spectrum" windows of DUVET's graphical interface and not relevant for this tutorial.


```python
help(this_singleScan)
```

    Help on SingleScan in module specTools object:
    
    class SingleScan(builtins.object)
     |  SingleScan(fname, df=None, debug=False)
     |
     |  Represents a single scan.
     |
     |  Parameters belonging to the fully constructed object:
     |
     |  cindex : (int) the current index in color cycling
     |  cmap : (matplotlib.pyplot.colormap) the colormap for color cycling
     |  color : (str) the HEX code of the scan color for plotting
     |  data : (pandas.dataframe) the data contained in this scan's file
     |  debug : (boolean) whether or not to print debug statements. Defaults to
     |          False.
     |  fname : (str) the full file path associated with this object.
     |  lenccycle (int) the length of the color cycle for color cycling
     |  name : (str) the name of this scan
     |  visible : (boolean) whether or not to show this scan in plotting
     |
     |  Methods defined here:
     |
     |  __init__(self, fname, df=None, debug=False)
     |      Initialize self.  See help(type(self)) for accurate signature.
     |
     |  cycle_color(self)
     |      Changes the color based on a color cycle
     |
     |  flip_visibility(self)
     |      Changes the visibility of the scan when plotting. If
     |      the self.visible parameter is false, the plot_absorbance
     |      function will skip plotting this spectrum.
     |
     |  ----------------------------------------------------------------------
     |  Data descriptors defined here:
     |
     |  __dict__
     |      dictionary for instance variables
     |
     |  __weakref__
     |      list of weak references to the object
    


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

DUVET automatically adjusts this function to include as many Gaussian functions and/or custom components as the user specifies. All of the parts of the fit function are optional. If the user specifies to use 0 Gaussian functions, that term will be ignored. If the user does not provide custom components to fit with, that term will be ignored. And Rayleigh scattering is not fit by default, and will be ignored unless the user turns it on. The user enables and disables parts of the fit function by providing arguments to the `fit_peaks` Python function of the `Spectrum` and `StitchedSpectrum` classes of the `specTools` module.

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
import specTools
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
    spec1 = specTools.Spectrum()
    spec1.change_name(sample_short1[-9:-4])
    spec1.add_bkgd(bkgd_short1)
    spec1.add_bkgd(bkgd_short2)
    spec1.add_sample(sample_short1)
    spec1.add_sample(sample_short2)
    spec1.change_color(color)
    spec1.change_offset(0.0)
    spec1.average_scans()

    # build long spectrum
    spec2 = specTools.Spectrum()
    spec2.change_name(sample_long1[-9:-4])
    spec2.add_bkgd(bkgd_long1)
    spec2.add_bkgd(bkgd_long2)
    spec2.add_sample(sample_long1)
    spec2.add_sample(sample_long2)
    spec2.change_color(color)
    spec2.change_offset(0.0)
    spec2.average_scans()

    stiched = specTools.StitchedSpectrum([spec1, spec2])
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
                        color=colors[11], name="Some Cool VUV Data!")


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
specTools.plot_fit(spec, plot_peaks=True, xlim=(120, 340),
               ylim=(0, spec.data[spec.data['wavelength']>120]['absorbance'].max()*1.1),
               plot_fit_components=True, save_path="./misc_figures/fit.svg")
```




    (<Axes: ylabel='Absorbance'>, <Axes: xlabel='Wavelength (nm)'>)




    
![png](README_files/output_52_1.png)
    



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
      <th>offset absorbance</th>
      <th>best_fit</th>
      <th>residuals</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>110.0</td>
      <td>0.036513</td>
      <td>0.012398</td>
      <td>NaN</td>
      <td>NaN</td>
    </tr>
    <tr>
      <th>1</th>
      <td>111.0</td>
      <td>-0.002350</td>
      <td>-0.026466</td>
      <td>NaN</td>
      <td>NaN</td>
    </tr>
    <tr>
      <th>2</th>
      <td>112.0</td>
      <td>0.022638</td>
      <td>-0.001477</td>
      <td>NaN</td>
      <td>NaN</td>
    </tr>
    <tr>
      <th>3</th>
      <td>113.0</td>
      <td>0.014045</td>
      <td>-0.010071</td>
      <td>NaN</td>
      <td>NaN</td>
    </tr>
    <tr>
      <th>4</th>
      <td>114.0</td>
      <td>0.096445</td>
      <td>0.072330</td>
      <td>NaN</td>
      <td>NaN</td>
    </tr>
    <tr>
      <th>...</th>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
    </tr>
    <tr>
      <th>226</th>
      <td>336.0</td>
      <td>0.024983</td>
      <td>0.000868</td>
      <td>0.025747</td>
      <td>-0.000763</td>
    </tr>
    <tr>
      <th>227</th>
      <td>337.0</td>
      <td>0.025773</td>
      <td>0.001658</td>
      <td>0.025454</td>
      <td>0.000320</td>
    </tr>
    <tr>
      <th>228</th>
      <td>338.0</td>
      <td>0.024884</td>
      <td>0.000769</td>
      <td>0.025194</td>
      <td>-0.000310</td>
    </tr>
    <tr>
      <th>229</th>
      <td>339.0</td>
      <td>0.024810</td>
      <td>0.000694</td>
      <td>0.024970</td>
      <td>-0.000160</td>
    </tr>
    <tr>
      <th>230</th>
      <td>340.0</td>
      <td>0.024115</td>
      <td>0.000000</td>
      <td>NaN</td>
      <td>NaN</td>
    </tr>
  </tbody>
</table>
<p>231 rows × 5 columns</p>
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
      'absorbance': 0      2.428171e-02
      1      2.622312e-02
      2      2.821936e-02
      3      3.025993e-02
      4      3.233303e-02
                 ...     
      226    5.313555e-34
      227    2.571947e-34
      228    1.240499e-34
      229    5.961960e-35
      230    2.855218e-35
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
      'absorbance': 0      3.498052e-03
      1      3.779931e-03
      2      4.080069e-03
      3      4.399237e-03
      4      4.738200e-03
                 ...     
      226    1.265532e-07
      227    1.068651e-07
      228    9.014149e-08
      229    7.595210e-08
      230    6.392650e-08
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
      'absorbance': 0      1.901318e-12
      1      2.659979e-12
      2      3.712278e-12
      3      5.168231e-12
      4      7.177650e-12
                 ...     
      226    1.817240e-06
      227    1.463698e-06
      228    1.176060e-06
      229    9.426422e-07
      230    7.537079e-07
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
      'absorbance': 0      1.430006e-121
      1      3.732441e-120
      2      9.553046e-119
      3      2.397643e-117
      4      5.900935e-116
                 ...      
      226     1.114691e-17
      227     3.478482e-18
      228     1.064434e-18
      229     3.194046e-19
      230     9.398476e-20
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
      'absorbance': 0      5.674503e-56
      1      2.089893e-55
      2      7.643624e-55
      3      2.776217e-54
      4      1.001351e-53
                 ...     
      226    8.002159e-05
      227    6.118406e-05
      228    4.645670e-05
      229    3.502977e-05
      230    2.623042e-05
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
      'absorbance': 0      2.380748e-188
      1      1.226741e-186
      2      6.206450e-185
      3      3.083077e-183
      4      1.503752e-181
                 ...      
      226     1.549585e-03
      227     1.275689e-03
      228     1.031156e-03
      229     8.183807e-04
      230     6.377302e-04
      Name: wavelength, Length: 231, dtype: float64}]



**IMPORTANT!!** The fitting is done to the data **with the spectrum offset applied**. The justification for this is that you make your nice plot, and then likely want to fit that which you see in front of you, rather than unadjusted data. Any negative absorbance regions in unadjusted data can also give strange looking fits when then converted to offset adjusted data for plotting.

Because of this, the `fit_results` will show your fit components **with** the spectrum offset used when fitting. If you do not want this, remember to subtract it out again! Or, set the spectrum offset to 0 before fitting.

Based on user feedback, this may change in future versions.

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
specTools.plot_fit(spec, plot_peaks=True, xlim=(120, 340),
               ylim=(0, spec.data[spec.data['wavelength']>120]['absorbance'].max()*1.1),
               plot_fit_components=True, save_path="./misc_figures/fit.svg")
```




    (<Axes: ylabel='Absorbance'>, <Axes: xlabel='Wavelength (nm)'>)




    
![png](README_files/output_62_1.png)
    



```python
spec.fit_components
```




    [{'parameters': {'value': 0.38634186438109736, 'error': 0.0024388864262753756},
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
      'absorbance': [0.07382993028322771,
       0.07348222260528471,
       0.07313451492734173,
       0.07278680724939873,
       0.07243909957145575,
       0.07209139189351277,
       0.07174368421556977,
       0.07139597653762679,
       0.0710482688596838,
       0.07070056118174081,
       0.07035285350379782,
       0.07000514582585485,
       0.06965743814791185,
       0.06930973046996887,
       0.06896202279202589,
       0.06861431511408288,
       0.0682666074361399,
       0.06791889975819691,
       0.06757119208025393,
       0.06722348440231093,
       0.06687577672436795,
       0.06652806904642496,
       0.06618036136848197,
       0.06583265369053899,
       0.065484946012596,
       0.06513723833465301,
       0.06478953065671002,
       0.06444182297876704,
       0.06409411530082405,
       0.06374640762288106,
       0.06339869994493808,
       0.06305099226699509,
       0.0627032845890521,
       0.06235557691110912,
       0.062007869233166125,
       0.061660161555223136,
       0.061312453877280154,
       0.06096474619933716,
       0.06061703852139417,
       0.06026933084345119,
       0.0599216231655082,
       0.0595739154875652,
       0.05922620780962222,
       0.05887850013167923,
       0.05853079245373625,
       0.05818308477579325,
       0.05783537709785026,
       0.057487669419907295,
       0.0571399617419643,
       0.05679225406402131,
       0.05644454638607833,
       0.05609683870813533,
       0.05574913103019234,
       0.05540142335224936,
       0.05505371567430637,
       0.05470600799636339,
       0.05435830031842039,
       0.0540105926404774,
       0.05366288496253442,
       0.05331517728459143,
       0.052967469606648436,
       0.052619761928705454,
       0.052272054250762465,
       0.05192434657281949,
       0.0515766388948765,
       0.051228931216933504,
       0.05088122353899053,
       0.05053351586104753,
       0.050185808183104544,
       0.04983810050516156,
       0.049490392827218566,
       0.049142685149275576,
       0.048794977471332594,
       0.048447269793389605,
       0.048099562115446616,
       0.04775185443750363,
       0.047404146759560645,
       0.04705643908161765,
       0.04670873140367466,
       0.046361023725731684,
       0.0460133160477887,
       0.045665608369845706,
       0.04531790069190272,
       0.044970193013959735,
       0.044622485336016746,
       0.044274777658073756,
       0.04392706998013077,
       0.04357936230218778,
       0.043231654624244796,
       0.0428839469463018,
       0.04253623926835882,
       0.04218853159041583,
       0.04184082391247283,
       0.04149311623452985,
       0.04114540855658686,
       0.04079770087864388,
       0.0404499932007009,
       0.04010228552275791,
       0.03975457784481492,
       0.039406870166871937,
       0.03905916248892894,
       0.03871145481098595,
       0.03836374713304297,
       0.03801603945509998,
       0.03766833177715699,
       0.037320624099214,
       0.03697291642127101,
       0.03662520874332803,
       0.036277501065385034,
       0.035929793387442045,
       0.03558208570949906,
       0.035234378031556074,
       0.034886670353613085,
       0.03453896267567011,
       0.03419125499772712,
       0.033843547319784124,
       0.03349583964184114,
       0.03314813196389815,
       0.032800424285955164,
       0.032452716608012175,
       0.032105008930069186,
       0.031757301252126204,
       0.031409593574183214,
       0.031061885896240222,
       0.030714178218297236,
       0.030366470540354247,
       0.03001876286241126,
       0.02967105518446827,
       0.029323347506525283,
       0.0289756398285823,
       0.02862793215063932,
       0.028280224472696326,
       0.02793251679475334,
       0.027584809116810355,
       0.027237101438867362,
       0.026889393760924373,
       0.026541686082981387,
       0.026193978405038402,
       0.02584627072709541,
       0.02549856304915242,
       0.025150855371209434,
       0.02480314769326645,
       0.024455440015323456,
       0.024107732337380467,
       0.02376002465943748,
       0.023412316981494492,
       0.023064609303551507,
       0.022716901625608528,
       0.022369193947665535,
       0.02202148626972255,
       0.021673778591779564,
       0.021326070913836575,
       0.020978363235893586,
       0.020630655557950597,
       0.020282947880007608,
       0.019935240202064622,
       0.019587532524121633,
       0.019239824846178644,
       0.018892117168235665,
       0.018544409490292672,
       0.01819670181234968,
       0.0178489941344067,
       0.017501286456463712,
       0.017153578778520716,
       0.016805871100577734,
       0.016458163422634745,
       0.01611045574469175,
       0.015762748066748766,
       0.01541504038880578,
       0.015067332710862786,
       0.01471962503291981,
       0.01437191735497682,
       0.014024209677033841,
       0.013676501999090847,
       0.013328794321147855,
       0.012981086643204872,
       0.012633378965261883,
       0.01228567128731889,
       0.01193796360937591,
       0.011590255931432921,
       0.011242548253489923,
       0.010894840575546943,
       0.010547132897603955,
       0.010199425219660961,
       0.009851717541717977,
       0.009504009863774992,
       0.009156302185832013,
       0.008808594507889022,
       0.008460886829946031,
       0.00811317915200305,
       0.00776547147406006,
       0.007417763796117065,
       0.007070056118174083,
       0.006722348440231095,
       0.0063746407622881,
       0.0060269330843451185,
       0.00567922540640213,
       0.005331517728459135,
       0.004983810050516152,
       0.004636102372573168,
       0.004288394694630173,
       0.003940687016687186,
       0.0035929793387442024,
       0.0032452716608012237,
       0.0028975639828582346,
       0.0025498563049152407,
       0.002202148626972258,
       0.0018544409490292694,
       0.0015067332710862744,
       0.0011590255931432927,
       0.0008113179152003069,
       0.0004636102372573107,
       0.00011590255931432633,
       -0.00023180511862865865,
       -0.0005795127965716532,
       -0.0009272204745146383,
       -0.0012749281524576208,
       -0.0016226358304006169,
       -0.001970343508343591]}]



As we can see from the residuals, fitting just a line to these data is not the best we could have possibly done. But, if you want to add in your own data to fit with, DUVET can handle it! In this example we created data in the form of a line, but you could just as easily have data from another experiment that you want to use. Just make sure that you format it in terms of wavelength and absorbance, and put it into a pandas dataframe. After that, DUVET doesn't care what the values are.

Once again, we can look at our `fit_results` to extract our amplitude on the custom component we fit with.


```python
spec.fit_results
```




    {'reduced_chi_square': 9.9562089317253,
     'n_gaussians': 0,
     'n_custom_components': 1,
     'fitted_scattering': False,
     'custom_component_parameters': [{'value': 0.38634186438109736,
       'error': 0.0024388864262753756}],
     'scattering_parameters': [],
     'gaussian_parameters': [],
     'p': array([0.38634186]),
     'pcov': array([[5.948167e-06]])}




```python
spec.offset
```




    -0.024115221965496998




```python
spec.fit_components
```




    [{'parameters': {'value': 0.38634186438109736, 'error': 0.0024388864262753756},
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
      'absorbance': [0.07382993028322771,
       0.07348222260528471,
       0.07313451492734173,
       0.07278680724939873,
       0.07243909957145575,
       0.07209139189351277,
       0.07174368421556977,
       0.07139597653762679,
       0.0710482688596838,
       0.07070056118174081,
       0.07035285350379782,
       0.07000514582585485,
       0.06965743814791185,
       0.06930973046996887,
       0.06896202279202589,
       0.06861431511408288,
       0.0682666074361399,
       0.06791889975819691,
       0.06757119208025393,
       0.06722348440231093,
       0.06687577672436795,
       0.06652806904642496,
       0.06618036136848197,
       0.06583265369053899,
       0.065484946012596,
       0.06513723833465301,
       0.06478953065671002,
       0.06444182297876704,
       0.06409411530082405,
       0.06374640762288106,
       0.06339869994493808,
       0.06305099226699509,
       0.0627032845890521,
       0.06235557691110912,
       0.062007869233166125,
       0.061660161555223136,
       0.061312453877280154,
       0.06096474619933716,
       0.06061703852139417,
       0.06026933084345119,
       0.0599216231655082,
       0.0595739154875652,
       0.05922620780962222,
       0.05887850013167923,
       0.05853079245373625,
       0.05818308477579325,
       0.05783537709785026,
       0.057487669419907295,
       0.0571399617419643,
       0.05679225406402131,
       0.05644454638607833,
       0.05609683870813533,
       0.05574913103019234,
       0.05540142335224936,
       0.05505371567430637,
       0.05470600799636339,
       0.05435830031842039,
       0.0540105926404774,
       0.05366288496253442,
       0.05331517728459143,
       0.052967469606648436,
       0.052619761928705454,
       0.052272054250762465,
       0.05192434657281949,
       0.0515766388948765,
       0.051228931216933504,
       0.05088122353899053,
       0.05053351586104753,
       0.050185808183104544,
       0.04983810050516156,
       0.049490392827218566,
       0.049142685149275576,
       0.048794977471332594,
       0.048447269793389605,
       0.048099562115446616,
       0.04775185443750363,
       0.047404146759560645,
       0.04705643908161765,
       0.04670873140367466,
       0.046361023725731684,
       0.0460133160477887,
       0.045665608369845706,
       0.04531790069190272,
       0.044970193013959735,
       0.044622485336016746,
       0.044274777658073756,
       0.04392706998013077,
       0.04357936230218778,
       0.043231654624244796,
       0.0428839469463018,
       0.04253623926835882,
       0.04218853159041583,
       0.04184082391247283,
       0.04149311623452985,
       0.04114540855658686,
       0.04079770087864388,
       0.0404499932007009,
       0.04010228552275791,
       0.03975457784481492,
       0.039406870166871937,
       0.03905916248892894,
       0.03871145481098595,
       0.03836374713304297,
       0.03801603945509998,
       0.03766833177715699,
       0.037320624099214,
       0.03697291642127101,
       0.03662520874332803,
       0.036277501065385034,
       0.035929793387442045,
       0.03558208570949906,
       0.035234378031556074,
       0.034886670353613085,
       0.03453896267567011,
       0.03419125499772712,
       0.033843547319784124,
       0.03349583964184114,
       0.03314813196389815,
       0.032800424285955164,
       0.032452716608012175,
       0.032105008930069186,
       0.031757301252126204,
       0.031409593574183214,
       0.031061885896240222,
       0.030714178218297236,
       0.030366470540354247,
       0.03001876286241126,
       0.02967105518446827,
       0.029323347506525283,
       0.0289756398285823,
       0.02862793215063932,
       0.028280224472696326,
       0.02793251679475334,
       0.027584809116810355,
       0.027237101438867362,
       0.026889393760924373,
       0.026541686082981387,
       0.026193978405038402,
       0.02584627072709541,
       0.02549856304915242,
       0.025150855371209434,
       0.02480314769326645,
       0.024455440015323456,
       0.024107732337380467,
       0.02376002465943748,
       0.023412316981494492,
       0.023064609303551507,
       0.022716901625608528,
       0.022369193947665535,
       0.02202148626972255,
       0.021673778591779564,
       0.021326070913836575,
       0.020978363235893586,
       0.020630655557950597,
       0.020282947880007608,
       0.019935240202064622,
       0.019587532524121633,
       0.019239824846178644,
       0.018892117168235665,
       0.018544409490292672,
       0.01819670181234968,
       0.0178489941344067,
       0.017501286456463712,
       0.017153578778520716,
       0.016805871100577734,
       0.016458163422634745,
       0.01611045574469175,
       0.015762748066748766,
       0.01541504038880578,
       0.015067332710862786,
       0.01471962503291981,
       0.01437191735497682,
       0.014024209677033841,
       0.013676501999090847,
       0.013328794321147855,
       0.012981086643204872,
       0.012633378965261883,
       0.01228567128731889,
       0.01193796360937591,
       0.011590255931432921,
       0.011242548253489923,
       0.010894840575546943,
       0.010547132897603955,
       0.010199425219660961,
       0.009851717541717977,
       0.009504009863774992,
       0.009156302185832013,
       0.008808594507889022,
       0.008460886829946031,
       0.00811317915200305,
       0.00776547147406006,
       0.007417763796117065,
       0.007070056118174083,
       0.006722348440231095,
       0.0063746407622881,
       0.0060269330843451185,
       0.00567922540640213,
       0.005331517728459135,
       0.004983810050516152,
       0.004636102372573168,
       0.004288394694630173,
       0.003940687016687186,
       0.0035929793387442024,
       0.0032452716608012237,
       0.0028975639828582346,
       0.0025498563049152407,
       0.002202148626972258,
       0.0018544409490292694,
       0.0015067332710862744,
       0.0011590255931432927,
       0.0008113179152003069,
       0.0004636102372573107,
       0.00011590255931432633,
       -0.00023180511862865865,
       -0.0005795127965716532,
       -0.0009272204745146383,
       -0.0012749281524576208,
       -0.0016226358304006169,
       -0.001970343508343591]}]



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

Spectra are not the only data taken at the UV endstation. It is also necessary to monitor the deposition of an ice with the deposition time scans. These can then be fit, and optics principles can be used to determine the dosing rate and index of refraction of the ice. This is done using `depTools.py`, for deposition tools.


```python
import depTools
```

`depTools` has only one class: `DepositionTimeScan`. It is initialized by giving it the data file of some deposition time scan. The data can then be plotted with `plot_timescan()`


```python
# create the DepositionTimeScan object
path = "./raw_data/SergioIoppolo-November2023/20231101/T73776.dat"
dep = depTools.DepositionTimeScan(path)

# plot it
depTools.plot_timescan(dep, save_path="./misc_figures/deposition_fit.svg")
```




    <Axes: xlabel='Time (seconds)', ylabel='Ch2 Signal (volts)'>




    
![png](README_files/output_75_1.png)
    


Finding the dosing rate is then (in principle) very easy. All you need to do is run `find_dosing_rate()` and give the function a few parameters, all of which are optional for the function itself, but likely necessary to get a good fit.

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
depTools.plot_timescan(dep, save_path="./misc_figures/deposition_fit.svg")
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




    
![png](README_files/output_77_2.png)
    


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

But what about that user who knows what thickness of ice they want, but not how long to deposit for? `depTools` can also calculate that in much the same way as finding the thickness:


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

import sys
import os
import traceback
import inspect
import json
import time

from datetime import datetime
import pandas as pd
import numpy as np

currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, parentdir)
with open("config.json") as f:
    config_file = json.load(f)

import tempControllerITC502 as TC

from PyQt5.QtCore import QTimer, QObject

class HardwareManager():
    """
    This class interfaces with all the hardware. Hardware should be represented
    in its own modules, one for each physical controller box. Those modules are
    then imported here, and this class creates a python object to represent
    each controller box. The other functions and classes of DUVET then go
    through the hardware controller to access the hardware. This way, we avoid
    complex interlinking of the other separate classes in order to access the
    same objects representing hardware.

    This class also contains a timer, which periodically asks the hardware for
    updates.
    """
    def __init__(self, debug):
        
        #super().__init__()
        self.debug = debug
        self.polling_rate = config_file['polling_rate']

        self.temperatureController = TC.TemperatureController(debug=self.debug)
        
        # a place to store the refresh functions that should be called
        self.hardware_refresh_functions = [self.collect_data]

        self.collectionStartTime = None
        self.collectionEndTime = None
        self.data = pd.DataFrame(
            columns=['Time', 'Sample T (K)', 'Setpoint T (K)',
                     'Heater Power (%)',
                     'MC Pressure (mbar)', 'Wavelength (nm)',
                     'ITC502_P (%)', 'ITC502_I (min)', 'ITC502_D (min)']
        )
        #self._refresh()

        #self.timer = QTimer()
        #self.timer.timeout.connect(self._refresh)
        #self.timer.start(self.polling_rate)

    def _refresh(self):
        """
        Calls all the refresh functions in self.hardware_refresh_functions
        """
        for function in self.hardware_refresh_functions:
            function()

    def add_refresh_function(self, function):
        """
        Add a function to the list of those needing to be refreshed
        """
        self.hardware_refresh_functions.append(function)

    def collect_data(self):
        """
        """
        #if self.collecting:
        time = datetime.now()
        temp = self.temperatureController.get_temp()
        target_temp = self.temperatureController.get_target_temp()
        power = self.temperatureController.get_heater_power()
        pressure = None
        wavelength = None
        ITC502_P = self.temperatureController.get_P()
        ITC502_I = self.temperatureController.get_I()
        ITC502_D = self.temperatureController.get_D()
        this_dict = {'Time':time,
                     'Sample T (K)':temp,
                     'Setpoint T (K)':target_temp,
                     'Heater Power (%)':power,
                     'MC Pressure (mbar)':pressure,
                     'Wavelength (nm)':wavelength,
                     'ITC502_P (%)':ITC502_P,
                     'ITC502_I (min)':ITC502_I,
                     'ITC502_D (min)':ITC502_D,}
        # replace bad values with np.nan
        if len(self.data) >= 10:
            for key in this_dict:
                if key == 'Time':
                    pass
                elif (key!= 'Setpoint T (K)') and (this_dict[key]==target_temp):
                    # for some reason we got the setpoint, is it an error?
                    try:
                        goodData = self.data[key].notna()
                        sigma = np.std(goodData.iloc[-5:-1])
                        mean = np.mean(goodData.iloc[-5:-1])
                        diff = np.abs(this_dict[key]-goodData.iloc[-1])
                        if (diff > 5*sigma) or (np.abs(this_dict[key]-mean)>50):
                            if self.debug:
                                print(f"Bad value! diff={diff}, sigma={sigma}")
                            this_dict[key] = np.nan
                    except Exception:
                        traceback.print_exc()
                        this_dict[key] = np.nan
                if this_dict[key] == "No Signal":
                    if self.debug:
                        print("Bad value!")
                    this_dict[key] = np.nan
        self.data.loc[len(self.data)] = this_dict

        # is the dataframe too big???
        if len(self.data) > 86400:
            # if so, drop the oldest hour of data
            self.data.drop(index=self.data.index[:3600], inplace=True)
            self.data.reset_index(inplace=True)

    def start_timescan_collection(self):
        """
        """
        if self.collectionStartTime is not None:
            print("Already collecting!")
            return None
        self.collecting = True
        self.collectionStartTime = datetime.now()

    def stop_timescan_collection(self):
        """
        """
        if self.collectionStartTime is None:
            print("Already not collecting!")
            return None
        
        # export the data
        self.collectionEndTime = datetime.now()
        df = self.data[(self.data['Time']>self.collectionStartTime) &
                       (self.data['Time']<self.collectionEndTime)]
        df.to_csv(f"T{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                  index=False)
        self.collectionStartTime = None

        if self.debug:
            self.data.to_csv(
                f"DEBUG{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                index=False)

   
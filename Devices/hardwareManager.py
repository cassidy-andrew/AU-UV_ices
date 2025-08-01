import sys
import os
import traceback
import inspect
import json
import time

from collections import deque

from datetime import datetime
import pandas as pd
import numpy as np

currentdir = os.path.dirname(
    os.path.abspath(inspect.getfile(inspect.currentframe()))
)
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, parentdir)
with open("config.json") as f:
    config_file = json.load(f)

import tempControllerITC502 as TC
import ConSysInterface as CSI

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
        self.ConSysInterface = CSI.ConSysInterface(debug=self.debug)
        
        # a place to store the refresh functions that should be called
        self.hardware_refresh_functions = [self.collect_data]

        self.collectionStartTime = None
        self.collectionEndTime = None
        #self.buffer = deque(maxlen=84000)
        self.buffer = {'Time':deque(maxlen=84000),
                       'Timestamp':deque(maxlen=84000),
                       'Sample T (K)':deque(maxlen=84000),
                       'Setpoint T (K)':deque(maxlen=84000),
                       'Heater Power (%)':deque(maxlen=84000),
                       'MC Pressure (mbar)':deque(maxlen=84000),
                       'DL Pressure (mbar)':deque(maxlen=84000),
                       'Wavelength (nm)':deque(maxlen=84000),
                       'ITC502_P (%)':deque(maxlen=84000),
                       'ITC502_I (min)':deque(maxlen=84000),
                       'ITC502_D (min)':deque(maxlen=84000),}
        self.data = None

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
        wavelength = None
        ITC502_P = self.temperatureController.get_P()
        ITC502_I = self.temperatureController.get_I()
        ITC502_D = self.temperatureController.get_D()
        MC_Pressure = self.ConSysInterface.get_MC_pressure()
        DL_Pressure = self.ConSysInterface.get_DL_pressure()
        this_dict = {'Time':time,
                     'Timestamp':datetime.timestamp(time),
                     'Sample T (K)':temp,
                     'Setpoint T (K)':target_temp,
                     'Heater Power (%)':power,
                     'MC Pressure (mbar)':MC_Pressure,
                     'DL Pressure (mbar)':DL_Pressure,
                     'Wavelength (nm)':wavelength,
                     'ITC502_P (%)':ITC502_P,
                     'ITC502_I (min)':ITC502_I,
                     'ITC502_D (min)':ITC502_D,}
        # replace bad values with np.nan, but skip the first 10 so we know how
        # to even identify them
        
        for key in this_dict:
            #if len(self.buffer) >= 10:
            if len(self.buffer[key]) >= 10:
                if key == 'Time':
                    pass
                elif (key!= 'Setpoint T (K)') and (this_dict[key]==target_temp):
                    try:
                        # for some reason we got the setpoint, is it an error?
                        #arr = np.array([row[key] for row in self.buffer])
                        arr = np.array(self.buffer[key])
                        mask = ~np.isnan(arr)
                        # last non-nan indicies
                        lnnis = np.flatnonzero(mask)[-5:-1]
                        # last non-nan values
                        lnnvs = arr[lnnis]
                        sigma = np.std(lnnvs)
                        mean = np.mean(lnnvs)
                        diff = np.abs(this_dict[key]-lnnvs[-1])
                        if (diff > 5*sigma and diff > 0.2) or \
                           (np.abs(this_dict[key]-mean)>50):
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
            # add the data to the buffer
            self.buffer[key].append(this_dict[key])
        #self.buffer.append(this_dict)

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
        self.data = pd.DataFrame.from_dict(self.buffer)
        df = self.data[(self.data['Time']>self.collectionStartTime) &
                       (self.data['Time']<self.collectionEndTime)]
        df.to_csv(f"T{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                  index=False)
        self.collectionStartTime = None

        if self.debug:
            self.data.to_csv(
                f"DEBUG{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                index=False)

   
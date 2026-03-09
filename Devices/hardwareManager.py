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
import photosensorAmplifierC932901 as PA

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
    def __init__(self, debug, parent):
        
        #super().__init__()
        self.debug = debug
        self.parent = parent
        self.polling_rate = self.parent.config['polling_rate']

        self.temperatureController = TC.TemperatureController(debug=self.debug)
        self.ConSysInterface = CSI.ConSysInterface(debug=self.debug)
        self.photosensor = PA.Photosensor(debug=self.debug)
        
        # a place to store the refresh functions that should be called
        self.hardware_refresh_functions = [self.collect_data]
        
        # data collection
        self.collectionStartTime = None
        self.collectionEndTime = None
        maxlen = 84000    # data points
        self.today = datetime.now().strftime("%Y-%m-%d")
        self.last_dump_time = datetime.now()
        self.buffer = {'Time':deque(maxlen=maxlen),
                       'DateTime':deque(maxlen=maxlen),
                       'Timestamp':deque(maxlen=maxlen),
                       'Sample T (K)':deque(maxlen=maxlen),
                       'Setpoint T (K)':deque(maxlen=maxlen),
                       'Heater Power (%)':deque(maxlen=maxlen),
                       'MC Pressure (mbar)':deque(maxlen=maxlen),
                       'DL Pressure (mbar)':deque(maxlen=maxlen),
                       'Wavelength (nm)':deque(maxlen=maxlen),
                       'ITC502_P (%)':deque(maxlen=maxlen),
                       'ITC502_I (min)':deque(maxlen=maxlen),
                       'ITC502_D (min)':deque(maxlen=maxlen),
                       'Hamamatsu (V)':deque(maxlen=maxlen),
                       'Ch0 (V)':deque(maxlen=maxlen),
                       'Ch1 (V)':deque(maxlen=maxlen),
                       'Ch2 (V)':deque(maxlen=maxlen),
                       'Ch3 (V)':deque(maxlen=maxlen),
                       'Z_Motor':deque(maxlen=maxlen),
                       'Beam_current':deque(maxlen=maxlen),
                       'UBX_x':deque(maxlen=maxlen),
                       'MRS_h':deque(maxlen=maxlen),
                       'GC_Pres':deque(maxlen=maxlen),
                       't_block':deque(maxlen=maxlen),
                       'PMTVac':deque(maxlen=maxlen),
                       'n_avg':deque(maxlen=maxlen),
                       'EXS_rPos':deque(maxlen=maxlen),
                       'ENS_rPos':deque(maxlen=maxlen),
                       'Table_Pos':deque(maxlen=maxlen),
                       'Grating':deque(maxlen=maxlen),
                       't_avg':deque(maxlen=maxlen)}
        self.data = None

        # configuration for scanning
        self.scan_config = {
            "wl_start":110,
            "wl_end":220,
            "wl_step":1.0,
            "n_scans":1,
            "n_points":111,
            "n_avg":np.nan,
            "t_avg":np.nan,
            "t_bllock":np.nan,
            "UnduPos_start":np.nan,
            "UnduPos_end":np.nan,
            "Table_Pos":np.nan,
            "Grating":np.nan,
            "Comments":"",
            "Sample":"",
            "EXS_rPos":np.nan,
            "ENS_rPos":np.nan,
            "PMTVac":np.nan
        }

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
        this_dict = {
            'Time':time.strftime("%H:%M:%S"),
             'DateTime':time,
             'Timestamp':datetime.timestamp(time),
             'Sample T (K)':self.temperatureController.get_temp(),
             'Setpoint T (K)':self.temperatureController.get_target_temp(),
             'Heater Power (%)':self.temperatureController.get_heater_power(),
             'MC Pressure (mbar)':self.ConSysInterface.get_MC_pressure(),
             'DL Pressure (mbar)':self.ConSysInterface.get_DL_pressure(),
             'Wavelength (nm)':self.ConSysInterface.get_wavelength(),
             'ITC502_P (%)':self.temperatureController.get_P(),
             'ITC502_I (min)':self.temperatureController.get_I(),
             'ITC502_D (min)':self.temperatureController.get_D(),
             'Hamamatsu (V)':self.photosensor.get_output(),
             'Ch0 (V)':self.ConSysInterface.get_ch0(),
             'Ch1 (V)':self.ConSysInterface.get_ch1(),
             'Ch2 (V)':self.ConSysInterface.get_ch2(),
             'Ch3 (V)':self.ConSysInterface.get_ch3(),
             'Z_Motor':self.ConSysInterface.get_z_motor(),
             'Beam_current':self.ConSysInterface.get_beam_current(),
             'UBX_x':self.ConSysInterface.get_UBX_x(),
             'MRS_h':self.ConSysInterface.get_MRS_h(),
             'GC_Pres':np.nan,
             't_block':self.ConSysInterface.get_block_time(),
             'PMTVac':self.ConSysInterface.get_PMTVac_status(),
             'n_avg':self.ConSysInterface.get_n_avg(),
             'EXS_rPos':self.ConSysInterface.get_exit_slit_position(),
             'ENS_rPos':self.ConSysInterface.get_entrance_slit_position(),
             'Table_Pos':self.ConSysInterface.get_table_position(),
             'Grating':self.ConSysInterface.get_grating(),
             't_avg':np.nan,
        }
        
        # update the scanning configuration with values read from ConSys
        consys_vals = ["n_avg", "Grating", "EXS_rPos", "ENS_rPos", "Table_Pos",
                       "PMTVac", "t_avg", "t_block"]
        for value in consys_vals:
            self.scan_config[value] = this_dict[value]
                
        # replace bad values with np.nan, but skip the first 10 so we know how
        # to even identify them
        target_temp = this_dict['Setpoint T (K)']
        
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
                        if len(lnnvs > 1):
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
                        if self.debug:
                            traceback.print_exc()
                        this_dict[key] = np.nan
            if this_dict[key] == "No Signal":
                if self.debug:
                    print("Bad value!")
                this_dict[key] = np.nan
            # add the data to the buffer
            self.buffer[key].append(this_dict[key])
        #self.buffer.append(this_dict)

    def dump_buffer(self):
        """
        """
        # what data to dump? Everything, but avoid duplicates
        self.data = pd.DataFrame.from_dict(self.buffer)
        to_dump = self.data[(self.data['DateTime']>self.last_dump_time)]
        self.last_dump_time = datetime.now()
        
        fname = self.parent.config["buffer_dump_directory"] + f"{self.today}.csv"
        if os.path.isfile(fname):
            to_dump.to_csv(fname, mode="a", index=False, header=False)
        else:
            to_dump.to_csv(fname, mode="a", index=False)

        return None

    def save_data(self, do_legacy=True, dXX=1):
        """
        Saves the data from the buffer into a dat file. 

        do_legacy (bool) : whether to save a file compatible with the legacy
            excel system, in addition to the full file. Defaults to true.

        dXX (int) : this file's index within the current scan. Defaults to 1
        """
        # we save these columns in this order, using these names
        saved_cols = {
            "Wavelength (nm)":"Wavelength/nm",
            "Ch0 (V)":"Ch0/V",
            "Ch1 (V)":"Ch1/V",
            "Ch2 (V)":"Ch2/V",
            "Ch3 (V)":"Ch3/V",
            "Z_Motor":"Z_Motor",
            "Beam_current":"Beam_current",
            "Sample T (K)":"Temperature/K",
            "GC_Pres":"GC_Pres/mbar",
            "Time":"Time",
            "UBX_x":"UBX_x",
            "MRS_h":"MRS_h"
        }
        
        # slice the buffer to the data we recorded
        self.collectionEndTime = datetime.now()
        self.data = pd.DataFrame.from_dict(self.buffer)
        df = self.data[(self.data['DateTime']>self.collectionStartTime) &
                       (self.data['DateTime']<self.collectionEndTime)]
        
        dXX_str = str(dXX).zfill(2)
        fname = self.parent.config["save_directory"] + \
                f"Scan{self.parent.config["latest_scan_number"]}.d"+dXX_str

        float_decimals = 5
        col_spacing = 8
        output_path = fname
        cfg = self.scan_config

        
        hls = []   # header lines

        """# Determine longest header key (for alignment)
        max_key_len = max(len(str(k)) for k in config.keys())
    
        for key, value in config.items():
            key_str = f";{key}"
            key_str = key_str.ljust(max_key_len + 2)
    
            if value is None:
                hls.append(key_str)
            else:
                hls.append(f"{key_str}{value}")"""
        hls.append(f";Start wavelength (nm)         {cfg['wl_start']}")
        hls.append(f";End wavelength (nm)           {cfg['wl_end']}")
        hls.append(f";Wavelength step (nm)          {cfg['wl_step']}")
        hls.append(f";Num. of scans / points        {cfg['n_scans']} / {cfg['n_points']}")
        hls.append(f";File date                     {self.today}")
        hls.append(f";Num. of avg. per point        {cfg['n_avg']}/ cRio {cfg['t_block']} ms")
        hls.append(f";Avg time per point            {cfg['t_avg']}")
        hls.append(f";UnduPos Start/End             {cfg['UnduPos_start']}/{cfg['UnduPos_end']}")
        hls.append(f";Table pos                     {cfg['Table_Pos']} kStp")
        hls.append(f";n/a                           ###")
        hls.append(f";Grating                       {cfg['Grating']}")
        hls.append(f";Slits                          {cfg['ENS_rPos']}/{cfg['EXS_rPos']}")
        hls.append(f";PMT Vacuum Status              {cfg['PMTVac']}")
        hls.append(f";  Comments: {cfg['Comments']}")
        hls.append(f";  Sample: {cfg['Sample']}")

        # Format numeric columns
        
        formatted_df = df[list(saved_cols.keys())].copy()
        for col in formatted_df.columns:
            if pd.api.types.is_float_dtype(formatted_df[col]):
                formatted_df[col] = formatted_df[col].map(
                    lambda x: f"{x:.{float_decimals}f}"
                )
            else:
                formatted_df[col] = formatted_df[col].astype(str)
    
        # Determine column widths
        col_width = 15
    
        # Build header row
        header_row = ";"
        for col in formatted_df.columns:
                header_row += saved_cols[col].ljust(col_width)
    
        # ---------------------------
        # 3. BUILD DATA ROWS (FIXED)
        # ---------------------------
    
        data_lines = []
    
        for _, row in formatted_df.iterrows():
            line = ""
            for col, val in zip(formatted_df.columns, row):
                if col != "DateTime":
                    line += val.ljust(col_width)
            data_lines.append(line)

        with open(output_path, "w") as f:
            for line in hls:
                f.write(line + "\n")
    
            f.write(header_row.rstrip() + "\n")
    
            for line in data_lines:
                f.write(line.rstrip() + "\n")
        
        #np.savetxt(fname, df, fmt='%s        ', header=header, comments=";")
        self.parent.config["latest_scan_number"] += 1
        self.collectionStartTime = None

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
        self.save_data()
        self.dump_buffer()

   
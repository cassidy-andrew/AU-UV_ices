import serial
import traceback
import os
import sys
import inspect
import json
import time
import numpy as np

currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, parentdir)
with open("config.json") as f:
    config_file = json.load(f)

class Photosensor():
    """
    This class represents the Hamamatsu C9329-01 photosensor amplifier
    """
    def __init__(self, debug):
        self.debug = debug
        self.read_timeout = 0.06   # seconds
        self.write_timeout = 0.06    # seconds
        self.baudrate = 19200    # see pages 10 and 76 of the manual
        self.default_channel = config_file['photosensor_channel']

        try:
            # establish the connection
            self.ser = serial.Serial(self.default_channel,
                                     baudrate=self.baudrate,
                                     timeout=self.read_timeout,
                                     write_timeout=self.write_timeout,
                                     bytesize=serial.EIGHTBITS,
                                     stopbits=serial.STOPBITS_ONE)
            # set the sensor to continuous measurement mode
            written = self.ser.write("*MOD0\n".encode('utf-8'))
        except Exception:
            traceback.print_exc()
            self.ser = None

    def get_output(self):
        try:
            line = self.ser.readline().decode('utf-8').strip()
            values = line.split(',')
            #print(values)
            measurement_raw = int("0x"+values[0], 0)
            volts = measurement_raw *5/32767
        except:
            if self.debug:
                print("Unable to read photosensor output")
            volts = np.nan
        
        return volts


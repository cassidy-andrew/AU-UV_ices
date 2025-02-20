import sys
import os
import inspect
import json

currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, parentdir)
with open("config.json") as f:
    config_file = json.load(f)

import tempControllerITC502 as TC

from PyQt5.QtCore import QTimer

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
    def __init__(self):
        self.polling_rate = config_file['polling_rate']

        self.temperatureController = TC.TemperatureController()
        
        # a place to store the refresh functions that should be called
        self.hardware_refresh_functions = []

        self.timer = QTimer()
        self.timer.timeout.connect(self._refresh)
        self.timer.start(self.polling_rate)

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

   
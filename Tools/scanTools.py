import numpy as np
import pandas as pd
from datetime import datetime
import warnings


class SpectrumScanner():
    def __init__(self, parent, config, debug):
        """
        """
        self.parent = parent
        self.config = config
        self.debug = debug

    def scan(self):
        """
        Interface with ConSys and perform a scan
        """
        return None

    def save_data(self, dXX=1):
        """
        """
        return None


class TimeScanner():
    def __init__(self, parent, config, debug):
        """
        """
        self.parent = parent
        self.config = config
        self.debug = debug

    def scan(self):
        """
        Interface with ConSys and perform a scan
        """
        return None

    def save_data(self, dXX=1):
        """
        """
        return None

import os
import numpy as np
import numpy.ctypeslib as ctl
import traceback
import ctypes
from ctypes import *

class ConSysInterface():
    def __init__(self, debug):
        """
        """
        self.debug = debug
        # load the ConSys API
        self.libname = "CSAPI.dll"
        self.libdir = "C:/Program Files/ConSys/"
        try:
            self.CSAPI = ctl.load_library(self.libdir+self.libname, self.libdir)
            # set our data types for the functions we will use
            self.CSAPI.RegisterParameterStringEx1.restype = c_long
            self.CSAPI.RegisterParameterStringEx1.argtypes = [c_char_p, c_int,
                                                              c_short]
            self.CSAPI.GetValue.restype = c_double
    
            # Now we want to register the parameters we are interested in.
            # ConSys only lets us register a few parameters, however within
            # those parameters we can have as many values as we need.

            # ------------------------------------------------------------------
            # Overivew of Registered Valaues in LShandle1
            # ------------------------------------------------------------------
            #  0 PLCAI1uv1.adc  -> voltage for the main chamber pressure
            #  1 PLCAI2uv1.adc  -> voltage for the dosing line pressure
            #  2 MONOuv1.cwl    -> wavelength measured by the monochromator
            #  3 MONOuv1.whichGr  -> which grating is being used
            #  4
            #  5
            #  6
            #  7
            #  8
            #  9
            # 10
            # 11
            # 12
            # 13
            # 14
            # 15
            # 16
            # 17
            # 18
            # 19
            # 20
            # 21
            reg_values = [
                'PLCAI1uv1.adc',    # 0 voltage for the main chamber pressure
                'PLCAI2uv1.adc',    # 1 voltage for the dosing line pressure
                'MONOuv1.cwl',      # 2 wavelength measured by the monochromator
            ]

            #regStr = b'PLCAI1uv1.adc PLCAI2uv1.adc MONOuv1.cwl'
            valStr = ''
            for value in reg_values:
                valStr += value + " "
            # encode the string of values to bytes
            regStr = valStr[:-1].encode()
            # register the parameter string
            self.LShandle1 = self.CSAPI.RegisterParameterStringEx1(
                regStr, len(regStr), 0
            )

            # wait for all the parameters to connect
            self.CSAPI.WaitForAllParametersConnected(self.LShandle1, 1000)
    
            self.registeredParameters = [self.LShandle1]
        except Exception:
            self.CSAPI = None
            self.registeredParameters = None
            self.LShandle1 = None
            print("Unable to establish connection to ConSys")
            if self.debug:
                traceback.print_exc()

    def get_MC_pressure(self):
        """
        Returns the pressure in mbar of the main chamber.

        This uses an Infinicon PBR 260 compact full range guage. See page 29
        (appendix A) of the guage's manual for the details on converting the
        measured voltage into a pressure.
        """
        if self.CSAPI == None:
            if self.debug:
                print("ConSys connection not open")
            return "No Signal"

        # get the sensor voltage from ConSys
        V = self.CSAPI.GetValue(self.LShandle1, 0)

        # check if we are over or under range, just set the value to the limit
        if V < 0.774:
            V = 0.774
        elif V > 10:
            V = 10
        
        P = 10**((V-7.75)/0.75)

        return P

    def get_wavelength(self):
        """
        Returns the wavelength measured by the monochromator
        """
        if self.CSAPI == None:
            if self.debug:
                print("ConSys connection not open")
            return "No Signal"

        # get the wavelength value from ConSys
        wl = self.CSAPI.GetValue(self.LShandle1, 2)

        return wl
        

    def get_DL_pressure(self):
        """
        Returns the pressure in mbar of the dosing line.

        This uses a ThyrCont VSR53/54MV guage. See page 24 of the guage's manual
        for details on converting the measured voltage into a pressure.
        """
        if self.CSAPI == None:
            if self.debug:
                print("ConSys connection not open")
            return "No Signal"

        # Get the sensor voltage from ConSys
        V = self.CSAPI.GetValue(self.LShandle1, 1)

        # check if we are over or under range, just set the value to the limit
        if V < 1.2:
            V = 1.2
        elif V > 8.8:
            V = 8.8

        P = 10**(V-5.5)

        return P

    def get_DL_pressure_IMR265(self):
        """
        [Depreciated, the current guage is a ThyrCont VSR53/54MV]
        Returns the pressure in mbar of the dosing line.

        This uses a Pfeiffer IMR 265 compact process ion guage. See page 25
        (appendix B) of the guage's manual for the details on converting the
        measured voltage into a pressure.
        """
        if self.CSAPI == None:
            if self.debug:
                print("ConSys connection not open")
            return "No Signal"

        # Get the sensor voltage from ConSys
        V = self.CSAPI.GetValue(self.LShandle1, 1)

        # are we using the hot or cold cathode?
        if (V >= 1.5) and (V <= 7.5):
            # hot cathode
            P = 10**(V-7.5)
        elif (V >= 8.5) and (V <= 9.75):
            # cold cathode
            P = 10**(4*(V-9))
        elif V < 1.5:
            # under range, give the lowest value
            P = 10**(1.5-7.5)
        elif V > 9.75:
            # over range, give the highest value
            P = 10**(4*(9.75-9))
        else:
            # between the hot and cold cathode regions. Measurement is undefined
            P = np.nan

        return P

    def close(self):
        """
        It is important to run this when the program ends, to ensure stability!
        """
        if self.CSAPI == None:
            # we are already closed / never opened to begin with
            return None
        else:
            # deregister all our parameters
            for parameter in self.registeredParameters:
                self.CSAPI.DeRegister(parameter)
            # close the ConSys API
            self.CSAPI.CloseCsAPI()

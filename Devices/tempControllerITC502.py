import serial
import traceback
import os
import sys
import inspect
import json
import time

currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, parentdir)
with open("config.json") as f:
    config_file = json.load(f)

class TemperatureController():
    """
    This class represents the Oxford Instruments ITC502 temperature
    controller and associated functions. It is used to both read values
    from, and send commands to, the temperature controller hardware.

    Until I have access to the hardware to test with, I assume we are using
    the serial interface rather than the GPIB connection.
    """
    def __init__(self):
        self.read_timeout = 0.03   # seconds
        self.write_timeout = 0.03    # seconds
        self.baudrate = 9600    # see pages 10 and 76 of the manual
        self.default_channel = config_file['temperature_controller_channel']

        try:
            self.ser = serial.Serial(self.default_channel,
                                     baudrate=self.baudrate,
                                     timeout=self.read_timeout,
                                     write_timeout=self.write_timeout,
                                     bytesize=serial.EIGHTBITS,
                                     stopbits=serial.STOPBITS_ONE,
                                     parity=serial.PARITY_NONE)
        except Exception:
            traceback.print_exc()

    def _parse_output(self, line):
        """
        Interprets the output of the controller
        """
        prefix = line[0]
        sign_symbol = line[1]
        if sign_symbol == '+':
            sign = 1
        else:
            sign = -1
        number = sign*float(line[2:])/10
        return prefix, number

    def _send_command(self, command, debug=False):
        written = 0
        output = None
        try:
            # write the command
            written = self.ser.write(command.encode('utf-8'))
            time.sleep(0.005)
            # read the output
            read = self.ser.readline()
            output = read.decode('utf-8')
            #time.sleep(0.002)
            #output = self._parse_output(read.decode('utf-8'))
            prefix = output[0]
            if prefix == "?":
                value = "No Signal"
            else:
                sign_symbol = output[1]
                if sign_symbol == '+':
                    sign = 1
                else:
                    sign = -1
                value = sign*float(output[2:])/10
            print(f"wrote {written} bytes, got {read} with value {value}")
        except Exception:
            print(f"wrote {written} bytes, got {read}")
            traceback.print_exc()
            value = "No Signal"
        return value

    def get_temp(self, channel=None):
        """
        See page 44 of the manual for the Rn command, which reads the value of
        some parameter specified by a number n 0-9. For reading the temperature,
        n = 1, 2, or 3 corresponding to sensors 1, 2, or 3.
        """
        command = "R1\n\r"
        value = self._send_command(command, debug=False)
        return value

    def set_temp(self, target, channel=None):
        """
        See page 47 of the manual, which specifies the syntax for setting the
        temperature.
        """
        command = "T" + str(target) + "\n\r"

    def get_target_temp(self, channel=None):
        """
        """
        command = "R0\n\r"
        value = self._send_command(command, debug=False)
        return value

    def get_heater_power(self, channel=None):
        """
        """            
        command = "R5\n\r"
        value = self._send_command(command, debug=False)
        return value

    def get_P(self, channel=None):
        """
        PROPORTIONAL BAND
        """
        command = "R8\n\r"
        value = self._send_command(command, debug=False)
        return value

    def get_I(self, channel=None):
        """
        INTEGRAL ACTION TIME
        """
        command = "R9\n\r"
        value = self._send_command(command, debug=False)
        return value

    def get_D(self, channel=None):
        """
        DERIVATIVE ACTION TIME
        """
        command = "R10\n\r"
        value = self._send_command(command, debug=False)
        return value

    def get_heater_status_no(self, channel=None):
        command = "X\n\r"
        value = self._send_command(command, debug=False)
        return value
        
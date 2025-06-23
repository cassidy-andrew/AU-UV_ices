from serial import Serial
import traceback
import os
import sys
import inspect
import json

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
        self.read_timeout = 1    # seconds
        self.write_timeout = 2    # seconds
        self.baudrate = 9600    # see pages 10 and 76 of the manual
        self.default_channel = config_file['temperature_controller_channel']

    def _open_serial_connection(self, channel):
        try:
            ser = Serial(channel, baudrate=self.baudrate,
                            timeout=self.read_timeout)
            ser.write_timeout = self.write_timeout
            return ser
        except Exception:
            traceback.print_exc()
            return None

    def get_temp(self, channel=None):
        """
        See page 44 of the manual for the Rn command, which reads the value of
        some parameter specified by a number n 0-9. For reading the temperature,
        n = 1, 2, or 3 corresponding to sensors 1, 2, or 3.
        """
        if channel == None:
            channel = self.default_channel
            
        command = "R1" + "\n"

        ser = self._open_serial_connection(channel)

        try:
            ser.write(command.encode('utf-8'))
            line = ser.readline().decode('utf-8')

            ser.close()
            value = float(line)
        except Exception:
            traceback.print_exc()
            value = "No Signal"
        return value

    def set_temp(self, target, channel=None):
        """
        See page 47 of the manual, which specifies the syntax for setting the
        temperature.
        """
        if channel == None:
            channel = self.default_channel
            
        command = "T" + str(target) + "\n"

        ser = self._open_serial_connection(channel)

        try:
            ser.write(command.encode('utf-8'))
            ser.close()
            return f"set target temperature to {target}"
        except Exception:
            traceback.print_exc()
            return "Failed to set target temperature"

    def get_target_temp(self, channel=None):
        """
        """
        if channel == None:
            channel = self.default_channel
        
        command = ""

        ser = self._open_serial_connection(channel)

        try:
            ser.write(command.encode('utf-8'))
            line = ser.readline().decode('utf-8')

            ser.close()
            value = float(line)
        except Exception:
            traceback.print_exc()
            value = "No Signal"
        return value

    def get_ramp_rate(self, channel=None):
        """
        """
        if channel == None:
            channel = self.default_channel

        command = ""

        ser = self._open_serial_connection(channel)

        try:
            ser.write(command.encode('utf-8'))
            line = ser.readline().decode('utf-8')

            ser.close()
            value = float(line)
        except Exception:
            traceback.print_exc()
            value = "No Signal"
        return value

    def set_ramp_rate(self, target, channel=None):
        """
        """
        if channel == None:
            channel = self.default_channel

        ser = self._open_serial_connection(channel)

        try:
            ser.write(command.encode('utf-8'))
            ser.close()
            return f"set target temperature to {target}"
        except Exception:
            traceback.print_exc()
            return "Failed to set ramp rate"

    def get_heater_range(self, channel=None):
        """
        """
        if channel == None:
            channel = self.default_channel

        command = ""

        ser = self._open_serial_connection(channel)

        try:
            ser.write(command.encode('utf-8'))
            line = ser.readline().decode('utf-8')

            ser.close()
            value = float(line)
        except Exception:
            traceback.print_exc()
            value = "No Signal"
        return value

    def set_heater_range(self, target, channel=None):
        """
        """
        if channel == None:
            channel = self.default_channel

        command = ""

        ser = self._open_serial_connection(channel)

        try:
            ser.write(command.encode('utf-8'))
            ser.close()
            return f"set target temperature to {target}"
        except Exception:
            traceback.print_exc()
            return "Failed to set heater range"

    def get_heater_power(self, channel=None):
        """
        """
        if channel == None:
            channel = self.default_channel

        command = "R5" + "\n"

        ser = self._open_serial_connection(channel)

        try:
            ser.write(command.encode('utf-8'))
            line = ser.readline().decode('utf-8')

            ser.close()
            value = float(line)
        except Exception:
            traceback.print_exc()
            value = "No Signal"
        return value

    def get_heater_status(self, channel=None):
        if channel == None:
            channel = self.default_channel

        command = "X"

        ser = self._open_serial_connection(channel)

        try:
            ser.write(command.encode('utf-8'))
            line = ser.readline().decode('utf-8')
            ser.close()
            # ok time to interpret. see page 46 of the manual
            sweep_status = line[line.index('S')+1:line.index('S')+3]
            if sweep_status[0] == '0':
                value = "stopped"
            else:
                value = "heating"
        except Exception:
            traceback.print_exc()
            value = "No Signal"
        return value
        
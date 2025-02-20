import serial
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


class GuageController():
    """
    Represents the Infinicon TPG366 vacuum measurement and control unit for
    compact guages
    """
    def __init__(self):
        self.read_timeout = 1    # seconds
        self.write_timeout = 2    # seconds
        self.baudrate = 9600    # see page 41 of the manual
        self.default_channel = config_file['guage_controller_channel']

    def _open_serial_connection(self, channel):
        try:
            ser = serial.Serial(channel, baudrate=self.baudrate,
                            timeout=self.read_timeout)
            ser.write_timeout = self.write_timeout
            return ser
        except Exception:
            traceback.print_exc()
            return None
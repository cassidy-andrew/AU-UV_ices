import numpy as np
import pandas as pd
from datetime import datetime
import warnings


class Queue():
    def __init__(self, parent, debug):
        """
        """

        self.parent = parent
        self.hardwareManager = parent.hardwareManager
        self.debug = debug

        self.running = False

        self.instructions = []

    def run_queue(self):
        """
        """
        if self.running:
            return None

        self.running = True
        for instruction in instructions:
            if self.hardwareManager.abort_status == True:
                return None
            else:
                instruction.execute()

        self.running = False
        return None

    def add_to_queue(self, instruction):
        """
        """
        self.instructions.append(instruction)

    def clear_queue(self):
        """
        """
        self.instructions = []
        return None
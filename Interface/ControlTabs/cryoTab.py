import sys
import traceback
import os
import inspect
import json

from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.Qt import *

class CryoTab():
    def __init__(self, parent, debug):
        """
        A tab for viewing the most important parameters in big font
        """
        self.parent = parent
        self.debug = debug

        # define fonts
        self.valueFontA = QFont("Consolas", 30)
        self.titleFontA = QFont("Arial", 15)
        self.valueFontB = QFont("Consolas", 15)
        self.titleFontB = QFont("Arial", 10)

        # where we hold all the smaller UI elements
        self.outerLayout = QGridLayout()

        # this is good for making the tab a little easier to read
        self.verticalSpacer = QSpacerItem(20, 20)   # x, y

        self.tempLabel = QLabel("Cryo control coming soon...")
        self.tempLabel.setFont(self.titleFontA)
        self.outerLayout.addWidget(self.tempLabel)
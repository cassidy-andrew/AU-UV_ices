# -----------------------------------------------------------------------------
# DUVET Test Suite
#
# This file executes various tests on DUVET and should always be run before
# comitting any changes.
# -----------------------------------------------------------------------------

import unittest

import duvet
import spectools
import deptools
import specGUI
import depGUI


class SpectrumDisplayTabTestCase(unittest.TestCase):
    """
    A collection of tests associated with a SpectrumDisplayTab object.
    """
    def setUp(self):
        self.SDT = specGUI.spectrumDisplayTab(debug=False)

    def test_add_remove_spectrum(self):
        """
        Test the ability to add and remove a spectrum from the spectrum list
        """
        # create the item in the speclist
        self.SDT.add_spectrum()
        # check
        self.assertEqual(len(self.SDT.all_spectra), 1)
        # remove the item from the speclist
        item = self.SDT.speclist.item(0)
        self.SDT.remove_spectra([item])
        # check
        self.assertEqual(len(self.SDT.all_spectra), 0)
        self.assertEqual(self.SDT.speclist.item(0), None)


class guiSpectrumTestCase(unittest.TestCase):
    """
    A collection of tests associated with a guiSpectrum object.
    """
    def setUp(self):
        self.SDT = specGUI.spectrumDisplayTab(debug=False)
        self.guiSpec = specGUI.guiSpectrum(index=0, parentWindow=self.SDT,
                                           debug=False)
        self.guiSpec.make_list_item()

    def test_color_change(self):
        """
        Test the ability to change a spectrum's color
        """
        # check the color cycle
        self.assertEqual(self.guiSpec.cycle_color(), None)
        # check the color picker
        self.guiSpec.update_color()

    def test_update_description(self):
        """
        Test the ability of a spectrum to change description
        """
        # make sure the default description is none
        self.assertEqual(self.guiSpec.spec.description, "")
        # apply a test description and make sure it was set
        self.guiSpec.spec.update_description("test description")
        self.assertEqual(self.guiSpec.spec.description, "test description")


if __name__ == '__main__':
    unittest.main()

"""Unit test for segy IO
"""
import unittest
import segyio
import segysettings

class TestSEGYRead(unittest.TestCase):
    """Unit test for segy read.
    """
    def test_setting_file_io(self):
        """Test the settings file read and write

        Create settings file, then output to json file. Read it back and compare.
        """
        reader = segyio.SEGYReader()
        path = 'default_settings.json'
        default_settings = segysettings.default_segy_settings(path)
        reader.init_setting(path)
        self.assertEqual(default_settings, reader.settings)

    def test_prepare_read(self):
        """Test the preparation of reading
        """
        file_path = r"./test_data/cdplbls_2373_angstk0_to_15.sgy"
        reader = segyio.SEGYReader(file_path)

        # initialize using the default settings
        reader.init_setting()

        # prepare reading
        reader.prepare()

        # expect the followings
        settings = reader.settings
        self.assertEqual(settings["endian"], "big")
        self.assertEqual(settings["sample_format"], "ibm")
        self.assertEqual(settings["sample_per_trace"], 1500)

    def test_encoding_check(self):
        """Test the checking of the file encoding
        """
        file_path = r"./test_data/cdplbls_2373_angstk0_to_15.sgy"
        reader = segyio.SEGYReader(file_path)

        # initialize using the default settings
        reader.init_setting()

        # open file
        file = open(file_path, 'rb')

        # checking encoding
        segyio._check_encoding(file, reader.settings)

        self.assertEqual(reader.settings['text_header_encoding'], 'ebcdic')

if __name__ == '__main__':
    unittest.main()

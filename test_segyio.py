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

if __name__ == '__main__':
    unittest.main()

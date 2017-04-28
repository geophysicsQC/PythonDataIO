"""SEGY IO module
"""
import json
import segysettings

class SEGYReader:
    """Read SEG-Y file

    args:
    has_init - True or False. Will set to False updating file_path or setting_path
    settings - a dictionary of settings
    """
    def __init__(self, file_path='', setting_path=''):
        self._file_path = file_path
        self._setting_path = setting_path
        self.has_init = False
        self.settings = {}

    def file_path(self):
        """Get file path
        """
        return self._file_path

    def setting_path(self):
        """Get setting file path
        """
        return self._setting_path

    def set_file_path(self, path):
        """Set file path
        """
        self._file_path = path
        self.has_init = False

    def init_setting(self, path=''):
        """Initialize settings, if path is empty string, use default
        """
        self._setting_path = path
        # set init flag to False to force initialization in the reading process
        self.has_init = False
        if path == '':
            self.settings = segysettings.default_segy_settings()
            return

        with open(path, 'r') as jsn_file:
            self.settings = json.load(jsn_file)

    def prepare(self):
        """Prepare reading process. The function will read in all trace headers defined by
        the settings file.
        """
        pass




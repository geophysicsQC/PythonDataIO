"""SEGY IO module
"""
import json
import struct
import segysettings

class SEGYReader:
    """Read SEG-Y file

    args:
    has_init = True or False. Will set to False updating file_path or setting_path
    setting_path = path to the settings file
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
        """Set file path.

        Will automatically set had_init to False.

        args:
        path = path to the SEG-Y file
        """
        self._file_path = path
        self.has_init = False

    def init_setting(self, path=''):
        """Initialize settings, if path is empty string, use default

        args:
        path = file path to the settings file.
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
        """Prepare reading process.

        Detect file endianess, sample per trace, SEG-Y version number, number of text
        headers.
        """
        with open(self.file_path, 'rb') as segy_file:
            # check file endianess
            self._check_file_endianess(segy_file, self.settings)
            # read required parameter
            self._read_mandatory_parameters(segy_file, self.settings)
            # detect text header number
            self._check_text_header(segy_file, self.settings)
            # detect version number
            self._check_version_number(segy_file, self.settings)

    def _read_mandatory_parameters(self, segy_file, settings):
        """Read mandatory parameters.
        """
        if settings['endian'] == 'little':
            is_little_endian = True
        elif settings['endian'] == 'big':
            is_little_endian = False
        else:
            raise InvalidSettingValue()

        # read samples per trace
        format_type, relative_byte = settings['binary_header']['sample_per_trace']
        settings['sample_per_trace'] = _read_header(segy_file, format_type,
                                                    relative_byte +
                                                    settings['text_header_byte'],
                                                    is_little_endian)
        # read sample format
        format_type, relative_byte = settings['binary_header']['sample_format_code']
        sample_format_code = _read_header(segy_file, format_type,
                                          relative_byte +
                                          settings['text_header_byte'],
                                          is_little_endian)

        # update sample_format
        if sample_format_code == 1:
            settings['sample_format'] = 'ibm'
        elif sample_format_code == 2:
            settings['sample_format'] = 'int4'
        elif sample_format_code == 3:
            settings['sample_format'] = 'int2'
        elif sample_format_code == 5:
            settings['sample_format'] = 'ieee_float'
        elif sample_format_code == 8:
            settings['sample_format'] = 'int1'
        else:
            raise SampleFormatDetectionError()


    def _check_file_endianess(self, segy_file, settings):
        """Check file endianess.

        If user wants to test file endianess, we will use sample_format_code binary header
        to identify it.
        """
        if settings['endian_detection']:
            if settings['endian'] != "little" and settings['endian'] != "big":
                raise EndianMissingError()
            else:
                return

        format_type, relative_byte = settings['binary_header']['sample_format_code']
        sample_format_code = _read_header(segy_file, format_type,
                                          relative_byte +
                                          settings['text_header_byte'],
                                          True)
        if sample_format_code < 1 or sample_format_code > 8:
            # if using little endian, we cannot get the right sample format
            # code
            sample_format_code = _read_header(segy_file, format_type,
                                              relative_byte +
                                              settings['text_header_byte'],
                                              False)
            if (sample_format_code != 1 and
                    sample_format_code != 2 and
                    sample_format_code != 3 and
                    sample_format_code != 4 and
                    sample_format_code != 5 and
                    sample_format_code != 8):
                # if using big endian, we still cannot get the right sample
                # format code
                raise EndianDetectionError()
            else:
                # detect
                settings['endian'] = 'big'
                return
        # detect
        settings['endian'] = 'little'

    def _check_text_header(self, segy_file, settings):
        """Check text header number.
        """
        pass

    def _check_version_number(self, segy_file, settings):
        """Check SEG-Y version number.
        """
        pass


class ParameterMissingError(Exception):
    """Error shot when prepare reading
    """

    def __init__(self, name_of_parameter=''):
        Exception.__init__(self)
        self.name_of_parameter = name_of_parameter

    def __str__(self):
        return "Required SEG-Y file parameter(s) could not be found in the settings" \
               + self.name_of_parameter


class WrongFormatStringError(Exception):
    """Error format string for header instruction in the settings
    """
    pass


class EndianDetectionError(Exception):
    """Error shot when we cannot detect file endianess
    """
    pass


class EndianMissingError(Exception):
    """Error shot when there is no 'endian' field in the settings, or the 'endian' field
    is not either 'little' or 'big'
    """
    pass

class SampleFormatDetectionError(Exception):
    """Error when sample format cannot be determined by the sample format code.
    """
    pass

class InvalidSettingValue(Exception):
    """Error when the settings value is not valid.
    """
    pass


def _read_header(segy_file, format_type, byte, is_little_endian):
    """Read header.

    args:
    segy_file = SEG-Y file instance
    type = 'short' | 'int'
    byte = absolute byte position of the header in segy_file file
    is_little_endian = True | False

    return:
    header value
    """
    segy_file.seek(byte, 0)
    if format_type == 'short':
        format_code = 'h'
        size_read = 2
    elif format_type == 'int':
        format_code = 'i'
        size_read = 4
    else:
        raise WrongFormatStringError()

    if is_little_endian:
        format_code += '<'
    else:
        format_code += '>'

    char_string = segy_file.read(size_read)
    return struct.unpack(format_code, char_string)

"""SEGY IO module
"""
import json
import struct
import segysettings
import codecs

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
        with open(self._file_path, 'rb') as segy_file:
            # check file endianess
            _check_file_endianess(segy_file, self.settings)
            # read required parameter
            _read_mandatory_parameters(segy_file, self.settings)
            # check code encoding
            _check_encoding(segy_file, self.settings)
            # detect text header number
            _check_text_header_number(segy_file, self.settings)
            # detect version number
            _check_version_number(segy_file, self.settings)

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

class EncodingDetectionError(Exception):
    """Error shot when encoding detection fails
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

def _check_file_endianess(segy_file, settings):
    """Check file endianess.

    If user wants to test file endianess, we will use sample_format_code binary header
    to identify it.
    """
    # if not enabling endian detection, expect little or big for the field endian in the
    #  settings
    if not settings['endian_detection']:
        if settings['endian'] != "little" and settings['endian'] != "big":
            raise EndianMissingError()
        else:
            return

    sample_format_code = _read_binary_header(segy_file, settings, "sample_format_code",
                                             use_settings_endian=False,
                                             little_endian=True)
    if sample_format_code < 1 or sample_format_code > 8:
        # if using little endian, we cannot get the right sample format
        # code
        sample_format_code = _read_binary_header(segy_file, settings, "sample_format_code",
                                                 use_settings_endian=False,
                                                 little_endian=False)
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

def _read_binary_header(segy_file, settings, name, use_settings_endian=True, little_endian=True):
    """Read binary header

    args:
    segy_file = file-type object with rb mode opened
    settings = settings dictionary
    name = header name
    use_settings_endian = True | False, if True, little_endian is useless.
    little_endian = True | False, if use_settings_endian is False, the endianess is
                    determined by this argument

    return:
    header value
    """
    if use_settings_endian:
        if ettings["endian"] == "little":
            is_little_endian = True
        elif settings["endian"] == "big":
            is_little_endian = False
    else:
        is_little_endian = little_endian

    format_type, relative_byte = settings['binary_header'][name]
    value = _read_header(segy_file, format_type,
                                        relative_byte +
                                        settings['text_header_byte'],
                                        is_little_endian)
    return value

def _check_text_header_number(segy_file, settings):
    """Check extra text header number.

    Following this rule to check number of extra text headers
    1. read text header indicator from binary header
    2. if the indicator >= 0, then set extra_text_header_number be the indicator
    3. if the indicator < 0, then we detect the extra header number using stanza
       from the settings
    """
    # check if need to detect text header
    if not settings[text_header_number_detection]:
        # make sure text_header_number should be a positive integer number or 0
        value = settings["extra_text_header_number"]
        if not (isinstance(value, int) and value >= 0):
            raise InvalidSettingValue()

    extra_text_header_indicator = _read_binary_header(segy_file, settings, "extra_text_header_number")

    # indicator not less than 0, set value and return
    if extra_text_header_indicator >= 0:
        settings["extra_text_header_number"] = extra_text_header_indicator
        return

    # otherwise, call outside function to determine the number of extra headers

def _check_version_number(segy_file, settings):
    """Check SEG-Y version number.
    """
    pass

def _read_mandatory_parameters(segy_file, settings):
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

    if is_little_endian:
        format_code = '<'
    else:
        format_code = '>'

    if format_type == 'short':
        format_code += 'h'
        size_read = 2
    elif format_type == 'int':
        format_code += 'i'
        size_read = 4
    else:
        raise WrongFormatStringError()

    char_string = segy_file.read(size_read)
    return struct.unpack(format_code, char_string)[0]

def _check_encoding(segy_file, settings):
    """Check the file encoding by checking the first letter read.

    Expect a capitalized C letter for the first letter of the text header. If not found,
    will raise EncodingDetectionError.
    """
    if settings['text_header_encoding_detection']:
        if settings['text_header_encoding'] != "ascii" and settings['text_header_encoding'] != "ebcdic":
            raise InvalidSettingValue()

    # read first byte
    segy_file.seek(0)
    C_letter_byte = segy_file.read(1)

    # try ebcdic first
    C_letter = codecs.decode(C_letter_byte, encoding='cp037')
    if C_letter == 'C':
        settings['text_header_encoding'] = 'ebcdic'
        return
    # try ascii then
    C_letter = codecs.decode(C_letter_byte, encoding='ascii')
    if C_letter == 'C':
        settings['text_header_encoding'] = 'ebcdic'
        return
    raise EncodingDetectionError()


def _count_extra_text_headers(segy_file, stop_stanza, binary_header_bytes, text_header_size):
    """Count the number of extra text headers in the segy file

    The program will loop through the first extra text header untill it meets the stop_stanza
    to count number of the extra text headers.

    args
    segy_file = opened SEG-Y file instance in rb mode
    stop_stanza = the stop stanza
    binary_header_byte = size of the binary header, standard should be 400
    text_header_size = size of the text header, standard should be 3200
    """
    segy_file.seek(binary_header_bytes + text_header_size)
    # read untill eof
    # while segy_file.read()
    # TODO finish the function
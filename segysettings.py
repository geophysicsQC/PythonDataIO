"""SEG-Y settings module.
"""
import json


def default_segy_settings(path=''):
    """Return the default SEG-Y settings dictionary. If path is not empty, write out the
    settings file in json format. For all header instructions, the list is
    [type, byte relative to binary header start byte/trace header start byte]
    """
    data = {}
    data['binary_header'] = {}
    data['trace_header'] = {}

    # specification of binary header fields that are mandatory
    data['binary_header']['sample_per_trace'] = ['short', 20]
    data['binary_header']['sample_format_code'] = ['short', 24]
    data['binary_header']['extra_text_header_number'] = ['short', 304]

    # specification of other binary header fields
    data['binary_header']['job_id'] = ['int', 0]
    data['binary_header']['line_no'] = ['int', 4]
    data['binary_header']['reel_no'] = ['int', 8]
    data['binary_header']['trace_per_ensemble'] = ['short', 12]
    data['binary_header']['auxtrace_per_ensemble'] = ['short', 14]
    data['binary_header']['sample_interval_us'] = ['short', 16]
    data['binary_header']['ori_sample_interval_us'] = ['short', 18]
    data['binary_header']['ori_sample_per_trace'] = ['short', 22]
    data['binary_header']['ensemble_fold'] = ['short', 26]
    data['binary_header']['sorting_code'] = ['short', 28]

    # specification of trace header fields
    data['trace_header']['trace_seq_no_within_line'] = ['int', 0]
    data['trace_header']['trace_seq_no_within_file'] = ['int', 4]
    data['trace_header']['ori_fld_rcd_no'] = ['int', 8]
    data['trace_header']['trace_no_within_ori_fld_rcd'] = ['int', 12]

    # bytes for different parts
    data['text_header_byte'] = 3200
    data['binary_header_byte'] = 400
    data['trace_header_byte'] = 240

    # detection methods options ['auto'|'manual']
    data['text_header_encoding_detection'] = 'auto'
    # depends on data['binary_header']['extra_text_header_number']
    data['text_header_number_detection'] = 'auto'
    data['endian_detection'] = 'auto'
    data['sample_format_detection'] = 'auto'

    # if data['endian_detection'] == 'auto', use the following setting for endianess
    data['endian'] = 'little'

    # text header encoding options ['ascii'|'ebcdic'],
    # used when data['text_header_encoding_detection'] = 'manual'
    data['text_header_encoding'] = 'ascii'

    # if data['text_header_number_detection'] == 'manual', use the following field
    data['text_header_number'] = 1

    # sample format used if data['sample_format_detection'] == 'auto'
    # the possible sample formats are ['ibm'|'int4'|'int2'|'ieee_float'|'int1']
    data['sample_format'] = 'ibm'

    if path != '':
        with open(path, 'w') as json_file:
            json.dump(data, json_file)

    return data

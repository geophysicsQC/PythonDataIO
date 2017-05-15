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
    # Number of 3200-byte, extended textual file header records following the Binary Header
    # Value meaning
    # 0 = there are no extended textual file header records
    # -1 = there are a variable number of extended textual file header records and the end
    #      of the extended textual file header is denoted by a (SEG: EndText) stanza in the
    #      final record
    # positive number = exactly that many extended textual file header records
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

    # Parameter detection flags (booleans) +++++++++++++++++++++++++++++++++++++++++++++++
    # depends on the first character of the text header
    data['text_header_encoding_detection'] = True
    # depends on data['binary_header']['extra_text_header_number']
    data['text_header_number_detection'] = True
    # depends on data['binary_header']['sample_format_code']
    data['endian_detection'] = True
    # depends on data['binary_header']['sample_format_code']
    data['sample_format_detection'] = True
    # depends on data['binary_header']['sample_pre_trace']
    data['sample_per_trace_detection'] = True

    # Mandatory parameters +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    data['endian'] = 'little'

    # the possible sample formats are ['ibm'|'int4'|'int2'|'ieee_float'|'int1']
    data['sample_format'] = 'ibm'

    # text header encoding options ['ascii'|'ebcdic']
    data['text_header_encoding'] = 'ascii'

    # number of text headers
    data['extra_text_header_number'] = 0

    # number of samples per trace
    data['sample_per_trace'] = 0

    # if path provided, write the default settings out +++++++++++++++++++++++++++++++++++
    if path != '':
        with open(path, 'w') as json_file:
            json.dump(data, json_file, indent=2)

    return data

"""Argument formatting
"""

import struct
from .reven import reven_helper as rvnh

ltraceconf_formats = {
    "addr": ("%#x", 4),
    "char": ("%c", 1),
    "ushort": ("%u", 2),
    "short": ("%d", 2),
    "uint": ("%u", 4),
    "int": ("%d", 4),
    "long": ("%ld", 4),
    "ulong": ("%lu", 4),
    "float": ("%n", 4),
    "double": ("%n", 8),
    "octal": ("%o", 4),
    "addr": ("%#x", 4),
    "file": ("%#x", 4),
    # "void": ("void", 0),
    # For lenses
    "hex": ("%#x", None),
    "oct": ("%#o", None),
    "bin": ("%b", None),
    # "bool": "bool",
    # "hide": "hide",
}

typesconf_formats = {
    "unsigned": "%lu",
    "signed": "%ld",
    "addr": "%#x",
    "string": "string",
    "cstring": "cstring",
    "wstring": "wstring",
    "tstring": "wstring",
    "bool": "bool",
    "void": None,
}


def as_int_value(raw_value):
    if len(raw_value) == 8:
        return struct.unpack("<q", raw_value)[0]
    return struct.unpack("<i", raw_value)[0]


def as_uint_value(raw_value):
    if len(raw_value) == 8:
        return struct.unpack("<Q", raw_value)[0]
    return struct.unpack("<I", raw_value)[0]


def format_value(raw_value, fmt, point):
    if fmt is None:
        return "void"

    if fmt == "void":
        return "void"

    if raw_value is None:
        return "?"

    if fmt == "bool":
        return "true" if as_int_value(raw_value) else "false"

    if fmt == "tstring":
        fmt = typesconf_formats["tstring"]

    if fmt == "wstring":
        value = as_uint_value(raw_value)
        if value == 0:
            return "nullstr"
        string_value = rvnh.get_wstring_arg(point, value)
        if string_value is None:
            return "str %#x" % (value)
        return "%s %#x" % (ascii(string_value), value)

    if fmt == "string" or fmt == "cstring":
        value = as_uint_value(raw_value)
        if value == 0:
            return "nullstr"
        string_value = rvnh.get_string_arg(point, value)
        if string_value is None:
            return "str %#x" % (value)
        return "%s %#x" % (ascii(string_value), value)

    if fmt == "char":
        value = as_int_value(raw_value)
        return ascii("%c" % (value & 0xFF))

    if fmt == "addr":
        value = as_uint_value(raw_value)
        return "%#x" % value

    if fmt == "unsigned":
        return str(as_uint_value(raw_value))

    if fmt == "signed":
        return str(as_int_value(raw_value))

    if fmt in ltraceconf_formats:
        value = as_int_value(raw_value)
        return ltraceconf_formats[fmt][0] % value

    if fmt in typesconf_formats:
        value = as_int_value(raw_value)
        return typesconf_formats[fmt] % value

    if fmt == "guess":
        threshold = 199999
        value = as_int_value(raw_value)
        if value < -threshold or value > threshold:
            value = as_uint_value(raw_value)
            return hex(value)
        else:
            return str(value)

    value = as_int_value(raw_value)
    return fmt % value


def get_argument_values(point, proto):
    is_64bit = point.context_before().is64b()

    offset = 4
    iargs = rvnh.ms_x64_args(point.context_before(), raw=True)

    args = []

    for proto_arg in proto.args:
        arg_value = None
        if not proto_arg.is_void():
            if is_64bit:
                arg_value = next(iargs)
            else:
                type_size = proto_arg.type.size
                if type_size is None:
                    type_size = 4
                arg_value = rvnh.get_int_arg(
                    point, offset, type_size, raw=True
                )
                offset += type_size

        args.append((proto_arg, arg_value))

    return args

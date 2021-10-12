"""Retrieve prototype information from resources
"""

import functools

from .demangle import msvc_demangle

from .ltraceconf.ltraceconf import LTraceConf
from .msdnxml.msdn_xml_file import MsdnXmlFile
from .msdnxml.clangparser import ProtoStrParser


def clang_parse(proto_parser, proto_str, callconv):
    clang = proto_parser.get_proto(proto_str, callconv)
    unknown_types = clang.diag.unknown_types()
    if not unknown_types:
        return clang.proto

    clang = proto_parser.clang()
    for t in unknown_types:
        clang.add_typedef(t, "addr")
    clang.parse_proto(proto_str, callconv)

    return clang.proto


class CallInfo(object):
    def __init__(
        self, srv, msdn_xml, msdn_typedefs_conf, ltrace_conf, ltrace_extra_conf
    ):
        self.msdn_xml = MsdnXmlFile(msdn_xml)
        self.proto_parser = ProtoStrParser(srv, msdn_typedefs_conf)
        self.ltrace_info = LTraceConf(ltrace_conf)
        self.ltrace_extra_info = LTraceConf(ltrace_extra_conf)

    @functools.lru_cache(maxsize=2048)
    def resolve_proto(self, symbol):
        # demangled
        prototype = symbol.prototype
        if prototype is not None:  # assume demangled proto
            proto_str = prototype + ";"
            maybe_proto = clang_parse(self.proto_parser, proto_str, None)
            if maybe_proto is not None:
                return maybe_proto

        symbol_name = symbol.name
        # ltrace-extra.conf
        maybe_proto = self.ltrace_extra_info.get_proto(symbol_name)
        if maybe_proto is not None:
            return maybe_proto

        # ltrace.conf
        maybe_proto = self.ltrace_info.get_proto(symbol_name)
        if maybe_proto is not None:
            return maybe_proto

        callconv, func_name = msvc_demangle(symbol_name)

        # msdn.xml
        proto_str = self.msdn_xml.function_proto_str(func_name)
        if proto_str is not None:
            maybe_proto = clang_parse(self.proto_parser, proto_str, callconv)
            if maybe_proto is not None:
                return maybe_proto

        # ltrace-extra.conf - demangled
        maybe_proto = self.ltrace_extra_info.get_proto(func_name)
        if maybe_proto is not None:
            return maybe_proto

        # ltrace.conf - demangled
        maybe_proto = self.ltrace_info.get_proto(func_name)
        if maybe_proto is not None:
            return maybe_proto

        return None

from sys import stderr
from pcpp import Preprocessor
from io import StringIO

from reven2.preview.prototypes import RevenPrototypes

from .. import prototype
from . import cenv


class Diagnostic(object):
    def __init__(self, tu):
        self._unknown_types = tu.unknown_types
        self._diagnostics = tu.diagnostics

    def unknown_types(self):
        return self._unknown_types


class ClangParser(object):
    def __init__(self, srv, typesconf_file):
        self._cenv = cenv.cenv_from_typesconf_file(typesconf_file)
        self._reven = srv
        self._extra_typedefs = []

    def add_typedef(self, alias, real_type):
        self._extra_typedefs.append((alias, real_type))

    def parse_type(self, type_node):
        return prototype.PrototypeType(
            name=type_node.name,
            real_type=type_node.canonical,
            size=type_node.size,
            format=self._cenv.type_format(type_node.name, type_node.canonical),
        )

    def parse_arg(self, arg):
        return prototype.PrototypeArgument(
            name=arg.name, type=self.parse_type(arg.type)
        )

    def parse_func(self, f, proto):
        proto.name = f.name
        proto.return_type = self.parse_type(f.return_type)
        for arg in f.parameters:
            proto.add_argument(self.parse_arg(arg))

    def parse_tu(self, tu, proto):
        for f in tu.functions:
            self.parse_func(f, proto)

    def patch_sources(self, proto_src):
        return "{defines}\n{typedefs}\n{extra_typedefs}\n{proto}\n".format(
            defines=cenv.generate_defines(self._cenv.defines()),
            typedefs=self._cenv.typedefs(),
            extra_typedefs=cenv.generate_c_typedefs(self._extra_typedefs),
            proto=cenv.cpp_compat(proto_src),
        )

    def preprocess_sources(self, sources):
        cpp = Preprocessor()
        cpp.parse(StringIO(sources), source="proto.hpp")
        sstr = StringIO()
        cpp.write(sstr)
        src = sstr.getvalue()
        sstr.close()
        return src

    def preprocess(self, proto_src):
        src = self.patch_sources(proto_src)
        return self.preprocess_sources(src)

    def parse_proto(self, proto_src, callconv=None):
        proto = prototype.Prototype(proto_src, callconv)
        src = self.preprocess(proto_src)

        tu = RevenPrototypes(self._reven).parse_translation_unit(src)

        self.parse_tu(tu, proto)
        self.proto = proto
        self.diag = Diagnostic(tu)

        return proto


class ProtoStrParser:
    def __init__(self, srv, typesconf_file):
        self._reven_server = srv
        self._typesconf_file = typesconf_file

    def clang(self):
        return ClangParser(self._reven_server, self._typesconf_file)

    def parse_proto(self, proto_str, callconv=None):
        clang_parser = ClangParser(self._reven_server, self._typesconf_file)
        clang_parser.parse_proto(proto_str, callconv)
        return clang_parser

    def get_proto(self, proto_str, callconv=None):
        return self.parse_proto(proto_str, callconv)

        try:
            return self.parse_proto(proto_str, callconv)
        except Exception as e:
            print(
                "ERR: Prototype `{}` error: {}".format(proto_str, e),
                file=stderr,
            )
            return None

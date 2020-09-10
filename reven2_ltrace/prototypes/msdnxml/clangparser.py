from sys import stderr
import clang.cindex
from pcpp import Preprocessor
from io import StringIO
import re

from .. import prototype
from . import cenv


clang_version = "7"
clang_library_file = "/usr/lib/llvm-{v}/lib/libclang-{v}.so.1".format(
    v=clang_version
)

clang.cindex.Config.set_library_file(clang_library_file)


class Diagnostic(object):
    def __init__(self, tu):
        self._diagnostics = tu.diagnostics

    def unknown_types(self):
        types = []

        for diag in self._diagnostics:
            pattern = re.compile(r"unknown type name '(.*)'")
            m = pattern.fullmatch(diag.spelling)
            if m:
                types.append(m.group(1))

        return types


class ClangParser(object):
    def __init__(self, typesconf_file):
        self._cenv = cenv.cenv_from_typesconf_file(typesconf_file)
        self._index = clang.cindex.Index.create()
        self._extra_typedefs = []

    def add_typedef(self, alias, real_type):
        self._extra_typedefs.append((alias, real_type))

    def parse_type(self, type_node):
        t = prototype.PrototypeType()
        t.name = type_node.spelling
        t.real_type = type_node.get_canonical().spelling
        t.size = type_node.get_size()
        t.format = self._cenv.type_format(t.name, t.real_type)
        return t

    def parse_arg(self, arg_node):
        arg_name = arg_node.spelling
        arg_type = self.parse_type(arg_node.type)
        return prototype.PrototypeArgument(arg_name, arg_type)

    def parse_func(self, func_node, proto):
        proto.name = func_node.spelling
        proto.return_type = self.parse_type(func_node.result_type)
        for arg_node in func_node.get_arguments():
            proto.add_argument(self.parse_arg(arg_node))

    def parse_tu(self, tu, proto):
        for node in tu.cursor.get_children():
            if node.kind is clang.cindex.CursorKind.FUNCTION_DECL:
                self.parse_func(node, proto)

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

        tu = self._index.parse(
            "proto.hpp", unsaved_files=[("proto.hpp", src)], options=6
        )

        self.parse_tu(tu, proto)
        self.proto = proto
        self.diag = Diagnostic(tu)

        return proto


class ProtoStrParser:
    def __init__(self, typesconf_file):
        self._typesconf_file = typesconf_file

    def clang(self):
        return ClangParser(self._typesconf_file)

    def parse_proto(self, proto_str, callconv=None):
        clang_parser = ClangParser(self._typesconf_file)
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

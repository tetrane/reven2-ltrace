"""Extract information from ltrace.conf
"""

from .. import prototype

from .ltrace_parser import parse_ltrace_conf_file
from .ltrace_expression import (
    ArrayExpression,
    EnumExpression,
    LensExpression,
    StringExpression,
    StructExpression,
)


class LTraceConf:
    def __init__(self, ltrace_file):
        self.functions = parse_ltrace_conf_file(ltrace_file)

    def _make_arg(self, func_arg):
        arg_name = None  # no arg name in ltrace.conf
        arg_type = self._make_type(func_arg)
        return prototype.PrototypeArgument(arg_name, arg_type)

    # TODO: should properly handle string and enum,array,struct
    def _make_type(self, node):

        if isinstance(node, LensExpression):
            lens = node
            node = lens.type

            type_format = lens.lens
            type_name = "{}({})".format(lens.lens, node.name)
            real_type_name = node.name
            type_size = node.get_size()
        elif isinstance(node, StringExpression):
            type_format = "string"
            type_name = "string"
            real_type_name = "string"
            type_size = None
        elif isinstance(node, EnumExpression):
            type_format = "int"
            type_name = str(node)
            real_type_name = node.type
            type_size = node.type.get_size()
        elif isinstance(node, ArrayExpression):
            type_format = "addr"
            type_name = str(node)
            real_type_name = "array"
            type_size = None
        elif isinstance(node, StructExpression):
            type_format = "addr"
            type_name = str(node)
            real_type_name = "struct"
            type_size = None
        else:  # isinstance(node, TypeExpression):
            type_format = node.name
            type_name = node.name
            real_type_name = str(node)  # node.name
            type_size = node.get_size()

        return prototype.PrototypeType(
            name=type_name,
            real_type=real_type_name,
            format=type_format,
            size=type_size,
        )

    def _make_proto(self, function):
        proto = prototype.Prototype()
        proto.name = function.name
        proto.full_proto = str(function)

        proto.return_type = self._make_type(function.return_type)

        for func_arg in function.args:
            proto_arg = self._make_arg(func_arg)
            proto.add_argument(proto_arg)

        return proto

    def get_proto(self, symbol_name):
        if symbol_name not in self.functions:
            return None

        function = self.functions[symbol_name]
        return self._make_proto(function)

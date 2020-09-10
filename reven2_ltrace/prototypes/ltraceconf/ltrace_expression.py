"""Utility used when parsing expressions from ltrace.conf
"""

# FIXME: Only valid on 32 bit system
type_info = {
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
    "void": ("void", 0),
    # For lenses
    "hex": "%#x",
    "oct": "%o",
    "bin": "%b",
    "bool": "bool",
    "hide": "hide",
}


class DeclExpression:
    def __init__(self, return_type, name, args):
        self.return_type = return_type
        self.name = name
        self.args = args

    def __repr__(self):
        output = "%s %s(" % (self.return_type, self.name)
        for arg in self.args:
            output += "%r, " % arg
        if len(self.args) > 0:
            output = output[:-2]
        output += ")"
        return output


class TypeExpression:
    def __init__(self, name):
        self.name = name
        self.is_pointer = False
        self.is_output = False

    def get_format(self):
        # FIXME: Pointer not handled yet
        return type_info[self.name][0]

    def get_size(self):
        return type_info[self.name][1]

    def __repr__(self):
        output = ""
        if self.is_output:
            output += "+"
        output += self.name
        if self.is_pointer:
            output += "*"
        return output


class EnumExpression:
    def __init__(self):
        self.name = "enum"
        self.constants = {}
        self.type = TypeExpression("int")

    def get_format(self):
        return ""

    def get_name(self, value):
        return self.constants.get(value, value)

    def get_size(self):
        return self.type.get_size()

    def add_constant(self, name, value):
        self.constants[value] = name

    def __repr__(self):
        output = "enum("
        for value, name in self.constants.items():
            output += "%s=%d, " % (name, value)
        return output[:-2] + ")"


class LensExpression:
    def __init__(self, type, lens):
        self.type = type
        self.lens = lens

    def get_format(self):
        return type_info.get(self.lens, self.type.get_format())

    def get_size(self):
        return self.type.get_size()

    def __repr__(self):
        if self.lens:
            return "%s(%s)" % (self.lens, self.type)
        else:
            return "%s" % self.type


class ArrayExpression:
    def __init__(self, lens, expr):
        self.lens = lens
        self.expr = expr

    def get_size(self):
        return type_info["addr"][1]

    def get_array(self, point, addr, args):
        return "[%#x]" % addr

    def __repr__(self):
        return "%s[%s]" % (self.lens, self.expr)


class StructExpression:
    def __init__(self, lens_list):
        self.lens_list = lens_list

    def __repr__(self):
        output = "struct("
        for lens in self.lens_list:
            output += "%s, " % lens
        return output[:-2] + ")"


class StringExpression:
    def __init__(self, expr=None):
        self.expr = None
        if expr and (expr.expr != "zero" or expr.arg_expr):
            self.expr = expr

    def get_format(self):
        return "%s"

    def get_size(self):
        return 4

    def get_string(self, string, args):
        if self.expr:
            expr_result = self.expr.get_result(args)
            if expr_result:
                min_len = (
                    min(len(string), expr_result)
                    if expr_result != -1
                    else len(string)
                )
                return string[:min_len]
            else:
                print(
                    "Warning: Expression '%s' not handled yet" % self.expr.expr
                )
                return string
        else:
            return string

    def __repr__(self):
        if self.expr:
            return "string[%s]" % self.expr
        else:
            return "string"


class ElementaryExpression:
    def __init__(self, expr, arg_expr=None):
        self.expr = expr
        self.arg_expr = arg_expr

    def get_result(self, args):
        if "arg" in self.expr:
            arg_n = int(self.expr[3:])
            return int(args[arg_n][1])
        elif self.expr.isdigit():
            return int(self.expr)
        elif self.expr == "zero":
            return -1 if not self.arg_expr else self.arg_expr.get_result(args)

    def __repr__(self):
        if not self.arg_expr:
            return "%s" % self.expr
        else:
            return "%s(%s)" % (self.expr, self.arg_expr)

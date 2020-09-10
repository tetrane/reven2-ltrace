"""Abstract prototype info from any source (ltrace.conf or msdn)
"""


def void_arg(type_name, real_type_name):
    arg_type = PrototypeType(name=type_name, real_type=real_type_name, size=0)
    return PrototypeArgument(name=None, type=arg_type)


class PrototypeType(object):
    def __init__(self, name=None, real_type=None, format=None, size=None):
        self.name = name
        self.real_type = real_type
        self.format = format
        self.size = size

    def __str__(self):
        return "Type(name={}, real_type={}, size={}, format={})".format(
            self.name, self.real_type, self.size, self.format
        )


class PrototypeArgument(object):
    def __init__(self, name=None, type=None):
        self.name = name
        self.type = type if type is not None else PrototypeType()

    def is_void(self):
        return (
            self.type.size is not None
            and self.type.size == 0
            and self.name is None
        )

    def __str__(self):
        return "Argument(name={}, type={})".format(self.name, self.type)


class Prototype(object):
    def __init__(self, src="", callconv=None):
        self.args = []
        self.name = None
        self.return_type = PrototypeType()
        self.full_proto = src
        self.callconv = callconv

    def add_argument(self, arg):
        self.args.append(arg)

    def __str__(self):
        return "{} {} {}({}) from {}".format(
            self.return_type,
            self.callconv,
            self.name,
            ", ".join([str(a) for a in self.args]),
            self.full_proto,
        )

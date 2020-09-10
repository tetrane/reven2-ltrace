"""Sugar to display call info
"""

from .prototypes import demangle
from .reven import reven_helper as rvnh
from .prototype_formatter import format_value, get_argument_values


class PrettyProto(object):
    def __init__(self, tr, proto):
        self._proto = proto
        self._tr = tr
        self._ret = PrettyRet(proto.return_type, tr)

    @property
    def tr(self):
        return PrettyTr(self._tr)

    @property
    def func(self):
        return self._proto.name

    @property
    def ret(self):
        return self._ret

    @property
    def params(self):
        return [
            PrettyArg(a, i, value=None, tr=None)
            for i, a in enumerate(self._proto.args)
            if not a.is_void()
        ]

    @property
    def args(self):
        args = get_argument_values(self._tr, self._proto)
        return [
            PrettyArg(a, i, v, self._tr)
            for i, (a, v) in enumerate(args)
            if not a.is_void()
        ]

    def __str__(self):
        return str(self._proto.name)


class PrettyTr(object):
    def __init__(self, tr):
        self._tr = tr
        self._ossi_after = tr.context_after().ossi.location()

    @property
    def id(self):
        return self._tr.id

    @property
    def instr(self):
        return str(self._tr.instruction)

    @property
    def to_bin(self):
        if not self._ossi_after or not self._ossi_after.binary:
            return "<unknown>"
        return self._ossi_after.binary.name

    @property
    def to_sym(self):
        if not self._ossi_after or not self._ossi_after.symbol:
            return "<unknown>"
        callconv, symbol = demangle.msvc_demangle(self._ossi_after.symbol.name)
        return symbol

    def __str__(self):
        return "#{}".format(self._tr.id)


class PrettyType(object):
    def __init__(self, type):
        self._type = type

    @property
    def name(self):
        return self._type.name

    @property
    def real(self):
        return self._type.real_type

    @property
    def size(self):
        return self._type.size

    @property
    def format(self):
        return self._type.format

    def __str__(self):
        return str(self.name)


class PrettyRet(object):
    def __init__(self, type, tr):
        self._type = type
        self._tr = rvnh.get_ret_point(tr)
        self._value = (
            None if self._tr is None else rvnh.get_ret_raw_value(self._tr)
        )

    @property
    def tr(self):
        if self._tr is None:
            return "#unknown"

        return "#{}".format(self._tr.id)

    @property
    def type(self):
        return PrettyType(self._type)

    @property
    def value(self):
        return format_value(self._value, self._type.format, self._tr)

    def __str__(self):
        if self.value is None:
            return "?"
        return str(self.value)


class PrettyArg(object):
    def __init__(self, arg, index, value, tr):
        self._arg = arg
        self._value = value
        self._index = index
        self._tr = tr

    @property
    def name(self):
        if self._arg.name is None:
            return "arg{}".format(self._index + 1)
        return self._arg.name

    @property
    def value(self):
        if self._arg.is_void():
            return ""
        return format_value(self._value, self._arg.type.format, self._tr)

    @property
    def type(self):
        return PrettyType(self._arg.type)

    def __str__(self):
        if self.value is None:
            return "?"
        return str(self.value)

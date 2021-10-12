"""Output modes to display call info
"""

import inspect
import sys

from .pretty import PrettyProto, PrettyTr
from .prototypes import prototype
from .reven import reven_helper as rvnh


def get_print_func(pretty_mode):
    if pretty_mode is None:
        return print_default

    return globals().get("print_" + pretty_mode) or print_default


def list_print_modes():
    prefix = "print_"

    def select(value):
        return inspect.isfunction(value) and value.__name__.startswith(prefix)

    funcs = inspect.getmembers(sys.modules[__name__], select)
    return [
        (f.__name__[len(prefix) :], f.__doc__) for n, f in funcs  # noqa: E203
    ]


def dummy_proto(tr, symbol_name):
    proto = prototype.Prototype()
    proto.name = symbol_name
    proto.return_type = prototype.PrototypeType(
        name="?", real_type="?", format="guess", size=None
    )
    return proto


def get_pretty_proto(tr, info):
    symbol = rvnh.symbol_after(tr)
    if symbol is None:
        proto = dummy_proto(tr, "<unknown>")
    else:
        proto = info.resolve_proto(symbol) or dummy_proto(tr, symbol.name)
    return PrettyProto(tr, proto)


def print_default(tr, info):
    """Print oneline by default"""
    print_oneline(tr, info)


def print_tr(tr, info=None):
    """Print transition id"""
    print("#{}".format(tr.id))


def print_instr(tr, info=None):
    """Print transition id and instruction"""
    print("#{id} {instr}".format(id=tr.id, instr=str(tr.instruction)))


def print_ossi(tr, info=None):
    """Print transition id and called binary and symbol"""
    print("{tr} {tr.to_bin}!{tr.to_sym}".format(tr=PrettyTr(tr)))


def print_proto(tr, info):
    """Print prototype without values"""
    fmt = "{tr} {ret.type} {func}({params})"
    param_fmt = "{param.type} {param.name}"

    proto = get_pretty_proto(tr, info)
    params = ", ".join([param_fmt.format(param=p) for p in proto.params])
    print(
        fmt.format(
            tr=PrettyTr(tr), ret=proto.ret, func=proto.func, params=params
        )
    )


def print_ltrace(tr, info):
    """Print prototype and values in original ltrace-like style"""
    fmt = "{tr} {func}({values}) = {ret}"

    cs = get_pretty_proto(tr, info)
    args_value = ", ".join([arg.value for arg in cs.args])
    print(fmt.format(tr=cs.tr, func=cs.func, values=args_value, ret=cs.ret))


def print_oneline(tr, info):
    """Print extra information oneline"""
    fmt = "{tr} {ret.type} {bin}!{func}({args}) = {ret.value} at {ret.tr}"
    arg_fmt = "{arg.type} {arg.name}={arg.value}"

    cs = get_pretty_proto(tr, info)
    args = ", ".join([arg_fmt.format(arg=arg) for arg in cs.args])
    print(
        fmt.format(
            tr=cs.tr, ret=cs.ret, bin=cs.tr.to_bin, func=cs.func, args=args
        )
    )


def print_full_info(tr, info):
    """Print full information in multiple lines"""
    fmt = "{tr} {bin}!{func}({args}) = {ret.value} {ret_type_info} at {ret.tr}"
    arg_fmt = "{arg.name}={arg.value} {type_info}"
    type_info_fmt = "[{type.name}][{type.real}][{type.format}][{type.size}]"

    cs = get_pretty_proto(tr, info)

    args = []
    for arg in cs.args:
        arg_type = type_info_fmt.format(type=arg.type)
        args.append(arg_fmt.format(arg=arg, type_info=arg_type))
    args = ",\n\t".join(args)

    ret_type = type_info_fmt.format(type=cs.ret.type)

    print(
        fmt.format(
            tr=cs.tr,
            bin=cs.tr.to_bin,
            func=cs.func,
            args=args,
            ret=cs.ret,
            ret_type_info=ret_type,
        )
    )

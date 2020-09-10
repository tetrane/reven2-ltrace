"""Helpers to retrieve values for arguments and return from the reven trace.
"""

import struct
from sys import stderr

import reven2


def printerr(*args, **kwargs):
    print(*args, file=stderr, **kwargs)


def read_reg_before(point, reg, raw=True):
    return point.context_before().read(reg, raw=raw)


def read_reg_after(point, reg, raw=True):
    return point.context_after().read(reg, raw=raw)


def symbol_name_after(point):
    try:
        location = point.context_after().ossi.location()
        if location is None:
            raise RuntimeError("Cannot resolve ossi location")
        if location.symbol is None:
            raise RuntimeError("Ossi location is not linked to a symbol")
        return location.symbol.name
    except RuntimeError as e:
        printerr("WAR: No symbol at #{}: {}".format(point.id, e))
        return None


def read_addr_before(point, address, size, raw=True):
    a = reven2.address.LogicalAddress(address)
    return point.context_before().read(a, size, raw=raw)


# FIXME: Handle correct arg size for fastcall
def get_int_arg(point, offset, size, is_fastcall=False, raw=False):
    if not is_fastcall or offset > 8:
        esp = read_reg_before(
            point, _stack_pointer(point.context_before()), raw=False
        )
        arg = read_addr_before(
            point,
            esp + offset if not is_fastcall else esp + offset - 8,
            size,
            raw=raw,
        )

        return arg
    elif offset == 4:
        return read_reg_before(point, reven2.arch.x64.ecx, raw=raw)
    else:
        return read_reg_before(point, reven2.arch.x64.edx, raw=raw)


def _read_string_before(point, offset, string_type):
    if offset == 0:
        return None
    address = reven2.address.LogicalAddress(offset)
    try:
        return point.context_before().read(address, string_type)
    except RuntimeError as e:
        printerr("WAR: Cannot read string arg at {}: {}".format(point, e))
        return None
    except UnicodeDecodeError as e:
        printerr("WAR: Cannot decode string arg at {}: {}".format(point, e))
        return None


def get_string_arg(point, address_offset):
    String1000 = reven2.types.CString(
        encoding=reven2.types.Encoding.Utf8, max_character_count=1000
    )
    return _read_string_before(point, address_offset, String1000)


def get_wstring_arg(point, address_offset):
    WString1000 = reven2.types.CString(
        encoding=reven2.types.Encoding.Utf16, max_character_count=1000
    )
    return _read_string_before(point, address_offset, WString1000)


def ret_access(point, logical):
    address = reven2.address.LogicalAddress(logical)
    access_size = 4
    read_access = reven2.memhist.MemoryAccessOperation.Read

    accesses = point._trace.memory_accesses(
        address,
        access_size,
        point,
        is_forward=True,
        operation=read_access,
        fetch_count=1000,
    )

    for access in accesses:
        return access.transition

    return None


def _stack_pointer_after(point):
    return _stack_pointer(point.context_after())


def _stack_pointer(context):
    return reven2.arch.x64.rsp if context.is64b() else reven2.arch.x64.esp


def _ret_value(context, raw=False):
    reg = reven2.arch.x64.rax if context.is64b() else reven2.arch.x64.eax
    return context.read(reg, raw=raw)


def get_ret_point(point):
    logical = read_reg_after(point, _stack_pointer_after(point), raw=False)

    try:
        ret_point = ret_access(point, logical)
    except RuntimeError as e:
        printerr("WAR: Cannot get ret point for `{}`: {}".format(point, e))
        return None

    if ret_point is None:
        printerr("WAR: No ret point found for `{}`".format(point))
        return None

    return ret_point


def get_ret_raw_value(ret_point):
    return _ret_value(ret_point.context_before(), raw=True)


def get_ret_int_value(ret_point):
    raw_result = get_ret_raw_value(ret_point)

    if len(raw_result) == 8:
        return struct.unpack("<q", raw_result)[0]

    return struct.unpack("<i", raw_result)[0]


# TODO XMM0-3
# TODO arg type
def ms_x64_args(context, raw=False):
    # RCX/XMM0
    yield context.read(reven2.arch.x64.rcx, raw=raw)
    # RDX/XMM1
    yield context.read(reven2.arch.x64.rdx, raw=raw)
    # R8/XMM2
    yield context.read(reven2.arch.x64.r8, raw=raw)
    # R9/XMM3
    yield context.read(reven2.arch.x64.r9, raw=raw)

    # stack shadow + ret address
    # XXX: wrong if context is before the call
    stack_offset = 32 + 8
    while True:
        # TODO arg type, stack aligned on 16bytes
        size = 8
        rsp_value = context.read(reven2.arch.x64.rsp, raw=False)
        address = reven2.address.LogicalAddress(rsp_value + stack_offset)
        try:
            yield context.read(address, size, raw=raw)
        except RuntimeError as e:
            printerr(
                "WAR: Cannot read memory arg at {}: {}".format(
                    context.transition_before(), e
                )
            )
            yield None
        stack_offset += size


# TODO [XYZ]MM0-7
# TODO arg type
def sysv_amd64_args(context, raw=False):
    # RDI
    yield context.read(reven2.arch.x64.rdi, raw=raw)
    # RSI
    yield context.read(reven2.arch.x64.rsi, raw=raw)
    # RDX
    yield context.read(reven2.arch.x64.rdx, raw=raw)
    # RCX
    yield context.read(reven2.arch.x64.rcx, raw=raw)
    # R8
    yield context.read(reven2.arch.x64.r8, raw=raw)
    # R9
    yield context.read(reven2.arch.x64.r9, raw=raw)

    # XXX: wrong if context is before the call
    stack_offset = 8
    while True:
        # TODO arg type, stack aligned on 16bytes
        size = 8
        rsp_value = context.read(reven2.arch.x64.rsp, raw=False)
        address = reven2.address.LogicalAddress(rsp_value + stack_offset)
        yield context.read(address, size, raw=raw)
        stack_offset += size

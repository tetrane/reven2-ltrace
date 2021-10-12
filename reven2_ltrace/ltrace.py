"""Main script

Entrypoints:
- `main` is to be used when called from the command line
- `print_ltrace` will print ltrace information
   for a binary on a given context range
- `ltrace_pretty_proto` can be used to yield ltrace information
   for a binary on a given context range
"""

import argparse
import reven2

from .pretty_print import (
    get_print_func,
    get_pretty_proto,
    list_print_modes,
)
from .prototypes.call_info import CallInfo
from .reven.binary_ranges import binary_ranges

from .resources import (
    msdn_xml,
    msdn_typedefs_conf,
    ltrace_conf,
    ltrace_extra_conf,
)


def ltrace_pretty_proto(srv, binary_path, from_context=None, to_context=None):
    ltracer = CallInfo(
        srv, msdn_xml, msdn_typedefs_conf, ltrace_conf, ltrace_extra_conf
    )

    for tr in ltrace(srv.trace, binary_path, from_context, to_context):
        # ignore pagefaults
        if tr.type == reven2.trace.TransitionType.Instruction:
            yield get_pretty_proto(tr, ltracer)


def is_last_context(trace, context):
    return context._id == trace.transition_count


def ltrace(trace, binary_path, from_context=None, to_context=None):
    """Generate transitions leaving the given binary"""
    for _, last in binary_ranges(trace, binary_path, from_context, to_context):
        if last is not None and not is_last_context(trace, last):
            yield last.transition_after()


def print_ltrace(
    srv, binary_path, from_context=None, to_context=None, pretty_mode=None
):
    """
    Print ltrace information for binary on a context range.

    Each time the binary is exited, print information about the call.

    Examples
    ========

    >>> srv = reven2.RevenServer("localhost", 42777)
    >>> print_ltrace(srv, "c:/windows/explorer.exe")
    #26671651 LRESULT user32!DispatchMessage(const MSG * lpmsg=0x2a3f880) \
        = 0 at #26687018

    Information
    ===========

    @param srv: a connected instance of reven2.RevenServer
    @param binary_path: Full path str of the binary to analyse
    @param from_context: reven2.trace.Context to start the analysis at
        if None, analysis starts at the first context of the trace
    @param to_context: reven2.trace.Context to stop the analysis at
        if None, analysis stops at the last context of the trace
    @param pretty_mode: str of the pretty mode to be used for display
        @see pretty_print.py
        if None, use default pretty mode
    """
    print_info = get_print_func(pretty_mode)
    ltracer = CallInfo(
        srv, msdn_xml, msdn_typedefs_conf, ltrace_conf, ltrace_extra_conf
    )

    for tr in ltrace(srv.trace, binary_path, from_context, to_context):
        # ignore pagefaults
        if tr.type == reven2.trace.TransitionType.Instruction:
            print_info(tr, ltracer)


def parse_cli_args():
    pretty_modes_doc = (
        "Available PRETTY values for the --pretty option:\n"
        + "\n".join(
            [
                "  {}\n    {}".format(mode, desc)
                for mode, desc in list_print_modes()
            ]
        )
    )
    parser = argparse.ArgumentParser(
        epilog=pretty_modes_doc,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "--host",
        type=str,
        default="localhost",
        help='reven host, as a string (default: "localhost")',
    )
    parser.add_argument(
        "-p",
        "--port",
        type=int,
        default="13370",
        help="reven port, as an int (default: 13370)",
    )
    parser.add_argument("--from", type=int, help="start at context")
    parser.add_argument("--to", type=int, help="stop at context")
    parser.add_argument("--pretty", type=str, help="output format")
    parser.add_argument(
        "BINARY", nargs="?", help="full path of the binary to ltrace"
    )

    return parser.parse_args()


def print_binaries(srv):
    for b in srv.ossi.executed_binaries():
        print(b.path)


def main():
    args = parse_cli_args()
    host = args.host
    port = args.port
    binary_path = args.BINARY

    srv = reven2.RevenServer(host, port)

    if binary_path is None:
        print_binaries(srv)
        return

    from_context = None
    to_context = None

    if vars(args)["from"] is not None:
        from_context = srv.trace._context(vars(args)["from"])
    if args.to is not None:
        to_context = srv.trace._context(args.to)

    print_ltrace(srv, binary_path, from_context, to_context, args.pretty)


if __name__ == "__main__":
    main()

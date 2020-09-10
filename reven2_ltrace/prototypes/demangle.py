import re


def msvc_demangle(symbol):
    types = {
        "__cdecl": re.match(r"_(\w+)$", symbol),
        "__stdcall": re.match(r"_(\w+)@\d+$", symbol),
        "__fastcall": re.match(r"@(\w+)@\d+$", symbol),
        "__vectorcall": re.match(r"(\w+)@@\d+$", symbol),
        # FIXME: '__clrcall':
        # FIXME: '__thiscall':
    }
    for name, match in types.items():
        if match:
            return (name, match.group(1))
    return ("__cdecl", symbol)

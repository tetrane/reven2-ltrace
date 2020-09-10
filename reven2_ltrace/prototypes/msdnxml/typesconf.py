"""Parse msdn-types.conf typedefs
"""


def _handle_typesconf_line(typesconf, line):
    if line.startswith("typedef"):
        eqsplit = line[:-2].split("=")
        real_type = eqsplit[1]
        alias = eqsplit[0].split()[1]
        typesconf.typedefs.append((alias, real_type))

    elif line.startswith("#define"):
        define = line.strip().split()[1]
        typesconf.defines.append((define, ""))


def _parse_typesconf_file(typesconf, typesconf_file):
    with open(typesconf_file, "r") as file:
        for line in file.readlines():
            _handle_typesconf_line(typesconf, line)


class TypesConf(object):
    def __init__(self, typesconf_file=None):
        self.typedefs = []
        self.defines = []
        if typesconf_file is not None:
            _parse_typesconf_file(self, typesconf_file)

    def type_format(self, type_name, real_type_name):
        bool_types = ["BOOL", "BOOLEAN", "_Bool", "bool"]
        cstring_types = ["PSTR", "LPSTR", "PCSTR", "LPCSTR"]
        wstring_types = ["PWSTR", "LPWSTR", "PCWSTR", "LPCWSTR"]
        tstring_types = ["PTSTR", "LPTSTR", "PCTSTR", "LPCTSTR"]

        if type_name in bool_types:
            return "bool"

        if type_name in wstring_types or type_name in tstring_types:
            return "wstring"

        if type_name in cstring_types:
            return "cstring"

        if "unsigned" in type_name or "unsigned" in real_type_name:
            return "unsigned"

        if "char*" in type_name or "char *" in real_type_name:
            return "cstring"

        if "*" in type_name or "*" in real_type_name:
            return "addr"

        if "void" in real_type_name:
            return "void"

        return "signed"

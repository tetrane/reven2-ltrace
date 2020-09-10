from . import typesconf


def generate_defines(defineslist):
    return "\n".join(
        [
            "#define {} {}".format(define, value)
            for (define, value) in defineslist
        ]
    )


def generate_c_typedefs(typeslist):
    return "\n".join(
        [
            "typedef {} {};".format(real_type, alias)
            for alias, real_type in typeslist
        ]
    )


def cpp_compat(src):
    cpp_tokens = [
        "virtual:",
        "virtual",
        "public:",
        "public",
        "protected:",
        "protected",
        "private:",
        "private",
    ]
    for t in cpp_tokens:
        src = src.replace(t, "")
    src = src.replace("::", "_")
    return src


class CEnv(object):
    def __init__(self, types=None):
        self._typesconf = types if type is not None else typesconf.TypesConf()
        self._ctypedefs = generate_c_typedefs(self._typesconf.typedefs)

    def defines(self):
        return self._typesconf.defines

    def typedefs(self):
        return self._ctypedefs

    def type_format(self, type_name, real_type_name):
        return self._typesconf.type_format(type_name, real_type_name)


def cenv_from_typesconf_file(typesconf_path):
    tconf = typesconf.TypesConf(typesconf_path)
    return CEnv(tconf)

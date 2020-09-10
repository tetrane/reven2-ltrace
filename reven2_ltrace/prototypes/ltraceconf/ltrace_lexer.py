"""Lexer for ltrace.conf
"""

import ply.lex as lex  # noqa: F401

reserved = {
    "void": "VOID",
    "char": "CHAR",
    "ushort": "USHORT",
    "short": "SHORT",
    "uint": "UINT",
    "int": "INT",
    "ulong": "ULONG",
    "long": "LONG",
    "float": "FLOAT",
    "double": "DOUBLE",
    "octal": "OCTAL",
    "addr": "ADDR",
    "file": "FILE",
    "format": "FORMAT",
    "array": "ARRAY",
    "struct": "STRUCT",
    "string": "STRING",
    "oct": "OCT",
    "hex": "HEX",
    "hide": "HIDE",
    "bool": "BOOL",
    "bitvec": "BITVEC",
    "enum": "ENUM",
    "typedef": "TYPEDEF",
    "retval": "RETVAL",
    "zero": "ZERO",
}

literals = ["(", ")", ",", "=", "+", "*", "[", "]"]

precedence = (("left", "+"), ("right", "*"))

tokens = ["NAME", "NUMBER", "ARGUMENT", "ELEMENT", "STRING_N"] + list(
    reserved.values()
)

t_ignore_COMMENT = r";.*"
t_ignore = " \t"


def t_STRING_N(t):
    r"string\d+"
    return t


def t_ARGUMENT(t):
    r"arg\d+"
    return t


def t_ELEMENT(t):
    r"elt\d+"
    return t


def t_NAME(t):
    r"[a-zA-Z_][a-zA-Z_0-9]*"
    t.type = reserved.get(t.value, "NAME")
    return t


def t_NUMBER(t):
    r"\d+"
    t.value = int(t.value)
    return t


def t_newline(t):
    r"\n+"
    t.lexer.lineno += len(t.value)


def t_error(t):
    print("Illegal character '%s'" % t.value[0])
    t.lexer.skip(1)

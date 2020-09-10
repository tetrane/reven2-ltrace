"""Parser for ltrace.conf
"""

import ply.yacc as yacc

from .ltrace_lexer import *  # noqa: F403
from . import ltrace_expression as Expression

parsetab_tabmodule = "rvnltrace_parsetab"
parsetab_outputdir = "/tmp"

typedefs = {}


def p_file(p):
    "file : statement"
    p[0] = p[1]


def p_statement(p):
    """
    statement :
              | statement expression
    """
    if len(p) > 1:
        p[0] = p[1]
        if p[2]:
            p[0][p[2].name] = p[2]
    else:
        p[0] = {}


def p_expression(p):
    """
    expression : declaration
               | typedef
    """
    p[0] = p[1]


def p_declaration(p):
    "declaration : lens NAME '(' lens_list ')'"
    p[0] = Expression.DeclExpression(p[1], p[2], p[4])


def p_lens_list(p):
    """
    lens_list :
              | lens
              | lens_list ',' lens
    """
    if len(p) == 2:
        p[0] = [p[1]]
    elif len(p) == 4:
        p[0] = p[1] + [p[3]]
    else:
        p[0] = []


# FIXME: Value can't be omitted yet
def p_const_list(p):
    """
    const      : NAME '=' NUMBER
    const_list : const
               | const_list ',' const
    """
    if len(p) == 2:
        p[0] = Expression.EnumExpression()
        p[0].add_constant(*p[1])
    elif p[2] == "=":
        p[0] = (p[1], p[3])
    else:
        p[0] = p[1]
        p[0].add_constant(*p[3])


def p_elem_expr_number(p):
    "elem_expr : NUMBER"
    p[0] = Expression.ElementaryExpression(str(p[1]))


def p_elem_expr_arg(p):
    "elem_expr : ARGUMENT"
    p[0] = Expression.ElementaryExpression(p[1])


def p_elem_expr_retval(p):
    "elem_expr : RETVAL"
    p[0] = Expression.ElementaryExpression("arg0")


def p_elem_expr_element(p):
    "elem_expr : ELEMENT"
    p[0] = Expression.ElementaryExpression(p[1])


def p_elem_expr_zero(p):
    """
    elem_expr : ZERO
              | ZERO '(' elem_expr ')'
    """
    if len(p) == 2:
        p[0] = Expression.ElementaryExpression(p[1])
    else:
        p[0] = Expression.ElementaryExpression(p[1], p[3])


def p_lens(p):
    """
    lens : type
         | '+' lens
         | STRING
         | STRING '(' type ')'
         | STRING '[' elem_expr ']'
         | HEX '(' type ')'
         | OCT '(' type ')'
         | HIDE '(' type ')'
         | BOOL '(' type ')'
         | BITVEC '(' type ')'
         | ENUM '(' const_list ')'
         | ENUM '[' type ']' '(' const_list ')'
    """
    if len(p) == 2 and p[1] != "string":
        p[0] = p[1]
    elif p[1] == "+":
        p[0] = p[2]
        p[0].is_output = True  # FIXME: Not implemented yet
    elif p[1] == "string":
        if len(p) == 2:
            p[0] = Expression.StringExpression()
        elif p[2] == "(":
            if isinstance(p[3], Expression.ArrayExpression):
                # FIXME: Check array type is 'char'
                p[0] = Expression.StringExpression(p[3].expr)
            else:
                # FIXME: Check type is 'char*'
                p[0] = Expression.StringExpression()
        else:
            p[0] = Expression.StringExpression(p[3])
    elif p[1] == "enum":
        if p[2] == "(":
            p[0] = p[3]
        else:
            p[0] = p[6]
            p[0].type = p[3]
    else:
        p[0] = Expression.LensExpression(p[3], p[1])


def p_lens_string_n(p):
    "lens : STRING_N"
    p[0] = Expression.StringExpression(
        Expression.ElementaryExpression("arg" + p[1][6:])
    )


def p_type(p):
    """
    type : VOID
         | CHAR
         | USHORT
         | SHORT
         | UINT
         | INT
         | ULONG
         | LONG
         | FLOAT
         | DOUBLE
         | OCTAL
         | ADDR
         | FILE
         | lens '*'
         | ARRAY '(' lens ',' elem_expr ')'
         | STRUCT '(' lens_list ')'
    """
    if len(p) == 2:
        p[0] = Expression.TypeExpression(p[1])
    elif p[2] == "*":
        p[0] = p[1]
        p[0].is_pointer = True
    elif p[1] == "array":
        p[0] = Expression.ArrayExpression(p[3], p[5])
    elif p[1] == "struct":
        p[0] = Expression.StructExpression(p[3])


# FIXME: Not implemented yet
def p_type_format(p):
    "type : FORMAT"
    p[0] = Expression.StringExpression()


def p_type_custom(p):
    "type : NAME"
    if not p[1] in typedefs:
        raise RuntimeError("Error: Unknown type '%s'" % p[1])
    p[0] = typedefs[p[1]]


def p_typedef(p):
    "typedef : TYPEDEF NAME '=' lens"
    typedefs[p[2]] = p[4]


def p_error(p):
    if p:
        raise RuntimeError(
            "Syntax error at line %d before '%s'" % (p.lineno, p.value)
        )
    raise RuntimeError("Syntax error at EOF")


def parse_ltrace_conf_file(filepath):
    lexer = lex.lex()  # noqa: F405, F841
    parser = yacc.yacc(
        tabmodule=parsetab_tabmodule, outputdir=parsetab_outputdir
    )

    with open(filepath, "r") as f:
        result = parser.parse(f.read())
        return result


if __name__ == "__main__":
    result = parse_ltrace_conf_file("/etc/ltrace.conf")
    for k, v in result.items():
        print("%s\t\t%s" % (k, v))

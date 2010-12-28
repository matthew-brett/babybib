""" Parser for bibtex files """

from ply.yacc import yacc

from .btlex import tokens, lexer
from .parsers import Macro


macros = {}
preamble = []

def p_start(p):
    " definitions : definitions entry"
    key, value = p[2]
    p[0] = p[1]
    p[0][key] = value


def p_definitions_from_entry(p):
    """definitions : entry
    """
    # entries are citekey, fieldlist tuples
    p[0] = dict((p[1],))


def p_definitions_from_definitions_null(p):
    """definitions : definitions macro
                   | definitions preamble
                   | definitions IMPLICIT_COMMENT
                   | definitions EXPLICIT_COMMENT
    """
    p[0] = p[1]


def p_definitions_from_nulls(p):
    """definitions : macro
                   | preamble
                   | IMPLICIT_COMMENT
                   | EXPLICIT_COMMENT
                   | empty
    """
    p[0] = {}


def p_entry(p):
    "entry : AT ENTRY LBRACKET CITEKEY COMMA fieldlist optcomma RBRACKET"
    # entries are (citekey, dict) tuples
    # citekeys are case sensitive
    p[0] = (p[4], p[6])


def p_macro(p):
    "macro : AT MACRO LBRACKET NAME EQUALS expression RBRACKET"
    name = p[4].lower()
    macros[name] = p[6]


def p_preamble(p):
    "preamble : AT PREAMBLE LBRACKET expression RBRACKET"
    preamble.append(p[4])


def p_optcomma(p):
    """ optcomma : COMMA
                 | empty
    """


def p_empty(p):
    "empty :"
    pass


def p_fieldlist_from_def(p):
    """ fieldlist : fielddef """
    # fieldef is a tuple
    p[0] = dict((p[1],))


def p_fieldlist_from_list_def(p):
    """ fieldlist : fieldlist COMMA fielddef
    """
    # fielddef is a tuple, fieldlist is a dictionary
    key, value = p[3]
    p[0] = p[1]
    p[0][key] = value


def p_fielddef(p):
    """ fielddef : NAME EQUALS expression"""
    p[0] = (p[1].lower(), p[3])


def p_expr_name(p):
    " expression : NAME "
    name = p[1].lower()
    if name in macros:
        p[0] = macros[name]
    else:
        p[0] = Macro(name)


def p_expr_number(p):
    """ expression : NUMBER """
    p[0] = p[1]


def p_expr_hash(p):
    """ expression : expression HASH expression """
    p[0] = p[1] + p[3]


parser = yacc()

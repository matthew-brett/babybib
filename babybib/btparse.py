""" Parser for bibtex files """

from ply.yacc import yacc

from .btlex import tokens, lexer


macros = {}
preamble = []

def p_start(p):
    """definition : macro
                  | preamble
                  | entry
                  | empty
    """


def p_empty(p):
    "empty :"
    pass


def p_discard_comments(p):
    """empty : IMPLICIT_COMMENT
             | EXPLICIT_COMMENT
    """

def p_expr_name(p):
    " expression : NAME "
    p[0] = macros.get(p[1])


def p_expr_number(p):
    """ expression : NUMBER """
    p[0] = p[1]


def p_expr_hash(p):
    """ expression : expression HASH expression """
    p[0] = p[1] + p[3]


def p_fielddef(p):
    """ fielddef : NAME EQUALS expression"""
    p[0] = (p[1], p[3])


def p_fieldlist1(p):
    """ fieldlist : fielddef """
    # fieldef is a tuple
    p[0] = dict((p[1],))


def p_fieldlist2(p):
    """ fieldlist : fieldlist COMMA fielddef
    """
    # fielddef is a tuple, fieldlist is a dictionary
    key, value = p[3]
    p[0] = p[1]
    p[0][key] = value


def p_optcomma(p):
    """ optcomma : COMMA
                 | empty
    """


def p_macro(p):
    "macro : AT MACRO LBRACKET NAME EQUALS expression RBRACKET"
    macros[p[4]] = p[6]


def p_preamble(p):
    "preamble : AT PREAMBLE LBRACKET expression RBRACKET"
    preamble.append(p[4])


def p_entry(p):
    "entry : AT ENTRY LBRACKET CITEKEY COMMA fieldlist optcomma RBRACKET"
    p[0] = (p[4], p[6])


parser = yacc()

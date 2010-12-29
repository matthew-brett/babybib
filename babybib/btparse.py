""" Parser for bibtex files """

from ply.yacc import yacc

from .btlex import tokens, lexer
from .parsers import Macro


macros = {}
preamble = []

def p_start(p):
    """ definitions : throwout
                    | empty
    """
    p[0] = {}


def p_empty(p):
    "empty :"
    pass


def p_start_entry(p):
    """ definitions : entry
    """
    p[0] = dict((p[1],))


def p_definitions_throwout(p):
    " definitions : definitions throwout "
    p[0] = p[1]


def p_definitionss_entry(p):
    " definitions : definitions entry "
    p[0] = p[1]
    key, value = p[2]
    p[0][key] = value


def p_firstdef_discard(p):
    """ throwout : macro
                 | preamble
                 | IMPLICIT_COMMENT
                 | EXPLICIT_COMMENT
    """

def p_entry(p):
    """ entry : AT ENTRY LBRACKET CITEKEY COMMA fieldlist RBRACKET
              | AT ENTRY LBRACKET CITEKEY COMMA fieldlist COMMA RBRACKET
    """
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
        p[0] = [Macro(name)]


def p_expr_number(p):
    """ expression : NUMBER """
    p[0] = [p[1]]


def p_expr_string(p):
    """ expression : quotedstring
                   | curlystring
    """
    p[0] = p[1]


def p_string_quoted(p):
    " quotedstring : QUOTE stringcontents QUOTE "
    p[0] = p[2]


def p_string_curlied(p):
    " curlystring : LCURLY stringcontents RCURLY "
    p[0] = p[2]


def p_scont_basic(p):
    """ stringcontents : STRING
                       | curlystring
    """
    p[0] = [p[1]]


def p_scont_empty(p):
    " stringcontents : empty "
    p[0] = []


def p_scont_appending(p):
    """ stringcontents : stringcontents STRING
                       | stringcontents curlystring
    """
    p[0] = p[1] + [p[2]]


def p_expr_hash(p):
    """ expression : expression HASH expression """
    p[0] = p[1] + p[3]


def p_error(p):
    print "Syntax error at token", p.type, p.lineno


parser = yacc()

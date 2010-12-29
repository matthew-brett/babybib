""" Parser for bibtex files """

from ply.yacc import yacc

from .btlex import tokens, lexer
from .parsers import Macro


def p_start(p):
    """ definitions : initialize entry
                    | initialize throwout
                    | initialize empty
    """
    # This rule executes once only at the beginning of parsing. The
    # initialization has to be done with a action rule "initialize" because the
    # initialization has to be done before processing of any entries or macros
    p[0] = {}
    if not p[2] is None: # entry is tuple, others return None
        key, value = p[2]
        p[0][key] = value


def p_initialize(p):
    " initialize : "
    # action rule to initialize parser
    p.parser.defined_macros = {}
    p.parser.undefined_macros = {}
    p.parser.preamble = []


def p_empty(p):
    "empty :"
    pass


def p_definitions_throwout(p):
    " definitions : definitions throwout "
    p[0] = p[1]


def p_definitionss_entry(p):
    " definitions : definitions entry "
    p[0] = p[1]
    key, value = p[2]
    p[0][key] = value


def p_throwouts(p):
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
    # entry types are in ENTRY, and are not case senstive. They go in the
    # fieldlist dictionary as key 'entry type'.  The space in the key makes it
    # an illegal bibtex field name, so it can't clash with bibtex fields.
    # Citekeys are case sensitive
    p[6]['entry type'] = p[2].lower()
    p[0] = (p[4], p[6])


def p_macro(p):
    "macro : AT MACRO LBRACKET NAME EQUALS expression RBRACKET"
    name = p[4].lower()
    p.parser.defined_macros[name] = p[6]


def p_preamble(p):
    "preamble : AT PREAMBLE LBRACKET expression RBRACKET"
    p.parser.preamble += p[4]


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
    d_macros = p.parser.defined_macros
    if name in d_macros:
        p[0] = d_macros[name]
        return
    # Placeholder and reference to undefined macros
    p[0] = [Macro(name)]
    ud_macros = p.parser.undefined_macros
    if name not in ud_macros:
        ud_macros[name] = [p[0]]
    else:
        ud_macros[name].append(p[0])


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

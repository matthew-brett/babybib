""" Draft of a ply bibtex parser
"""
import re

from ply import lex, yacc

from .parsers import Macro

tokens = (
    'AT',
    'NEWLINE',
    'EXPLICIT_COMMENT',
    'IMPLICIT_COMMENT',
    'CITEKEY',
    'ENTRYTYPE',
    'COMMA',
    'BRACKET',
    'EQUALS',
    'FIELDNAME',
    'LCURLY',
    'RCURLY',
    'QUOTE',
    'STRING',
    'HASH',
    'NUMBER',
    )

states = (
    ('entrydef', 'exclusive'),
    ('fielddef', 'exclusive'),
    ('quotestring', 'exclusive'),
    ('curlystring', 'exclusive'),
)


t_NEWLINE = r"\n+"
t_IMPLICIT_COMMENT = r'.*\S+.*'

t_EXPLICIT_COMMENT = r'\s*@comment([\s{(].*)?'


def t_error(t):
    pass


_name_elements = '^\s"#%\'(),={}'
_any_name = '[%s]+' % _name_elements
_not_digname = '[%s\d][%s]*' % (_name_elements, _name_elements)
_entry_type = "\s*@\s*(?P<entry_type>" + _not_digname + ")\s*[{(]"

@lex.TOKEN(_entry_type)
def t_ENTRYTYPE(t):
    entry_type = t.lexer.lexmatch.group('entry_type').lower()
    if entry_type in ('string', 'preamble'):
        next_state = 'fielddef'
    else:
        next_state = 'entrydef'
    t.lexer.push_state(next_state)
    if t.value.endswith('{'):
        t.lexer.endtoken = '}'
    else:
        t.lexer.endtoken = ')'
    t.value = entry_type
    return t


t_entrydef_CITEKEY = _any_name

def t_entrydef_COMMA(t):
    r','
    t.lexer.pop_state()
    t.lexer.push_state('fielddef')


t_entrydef_fielddef_ignore = ' \t\n'


@lex.TOKEN(_not_digname)
def t_fielddef_FIELDNAME(t):
    t.value = t.value.lower()
    return t


t_fielddef_COMMA = ','
t_fielddef_EQUALS = '='
t_fielddef_HASH = r"\#"
t_fielddef_NUMBER = r'[0-9]+'


def t_fielddef_BRACKET(t):
    r"[})]\s*"
    # Leaving fielddef state
    if t.value.strip() == t.lexer.endtoken:
        t.lexer.pop_state()
    return t


def t_fielddef_QUOTE(t):
    r'"'
    t.lexer.push_state('quotestring')
    return t


def t_fielddef_quotestring_curlystring_LCURLY(t):
    r'{'
    t.lexer.push_state('curlystring')
    return t


def t_fielddef_error(t):
    # bomb out to INITAL state
    t.lexer.lexerstatestack = []


def t_quotestring_STRING(t):
    r'[^"{}]+'
    return t


def t_quotestring_QUOTE(t):
    r'"'
    # escape from quoting state
    t.lexer.pop_state()
    return t


def t_curlystring_RCURLY(t):
    r'}'
    t.lexer.pop_state()
    return t


def t_curlystring_STRING(t):
    r"[^{}]+"
    return t


lexer = lex.lex(reflags=re.IGNORECASE)

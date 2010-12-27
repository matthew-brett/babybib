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
    'ENDSTUFF',
    'ENTRY',
    'PREAMBLE',
    'MACRO',
    'CITEKEY',
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


t_IMPLICIT_COMMENT = r'(.|\n)*?\n\s*(?=@)'
t_EXPLICIT_COMMENT = r'\s*@comment([\s{(].*)?'

_at_to_go = re.compile('\n\s*@')
def t_INITIAL_error(t):
    # Soak up any trailing lines
    match = _at_to_go.search(t.value)
    if match is None:
        t.lexer.lexpos = len(t.lexer.lexdata)
        t.type = 'IMPLICIT_COMMENT'
        return t


def t_entrydef_fielddef_quotestring_curlystring_error(t):
    # bomb out to INITAL state
    t.lexer.lexerstatestack = []


_name_elements = '^\s"#%\'(),={}'
_any_name = '[%s]+' % _name_elements
_not_digname = '[%s\d][%s]*' % (_name_elements, _name_elements)
_entry_type = "[\s\n]*@\s*(?P<entry_type>" + _not_digname + ")\s*[{(]"

_END_BRACKETS = {'{': '}', '(': ')'}

@lex.TOKEN(_entry_type)
def t_ENTRY(t):
    # Push expected end token so we can recognize it later
    t.lexer.endtoken = _END_BRACKETS[t.value[-1]]
    # Get entry type from match
    entry_type = t.lexer.lexmatch.group('entry_type').lower()
    t.value = entry_type
    # Set the type of entry
    if entry_type == 'string':
        t.type = 'MACRO'
        next_state = 'fielddef'
    elif entry_type == 'preamble':
        t.type = 'PREAMBLE'
        next_state = 'fielddef'
    else: # entry
        next_state = 'entrydef'
    t.lexer.push_state(next_state)
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
    r"[})]"
    # Leaving fielddef state; discard matching bracket
    if t.value == t.lexer.endtoken:
        t.lexer.endtoken = None
        t.lexer.pop_state()
        return
    # Otherwise return it so we can raise a parse error
    return t


def t_fielddef_QUOTE(t):
    r'"'
    t.lexer.push_state('quotestring')
    return t


def t_fielddef_quotestring_curlystring_LCURLY(t):
    r'{'
    t.lexer.push_state('curlystring')
    return t


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

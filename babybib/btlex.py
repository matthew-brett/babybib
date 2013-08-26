""" Draft of a ply bibtex parser
"""

DEBUG = True

import re

from .ply import lex

tokens = (
    'EXPLICIT_COMMENT',
    'IMPLICIT_COMMENT',
    'AT',
    'ENTRY',
    'PREAMBLE',
    'MACRO',
    'CITEKEY',
    'COMMA',
    'LBRACKET',
    'RBRACKET',
    'EQUALS',
    'NAME',
    'LCURLY',
    'RCURLY',
    'QUOTE',
    'STRING',
    'HASH',
    'NUMBER',
    )

states = (
    ('defdef', 'exclusive'),
    ('entrydef', 'exclusive'),
    ('fielddef', 'exclusive'),
    ('quotestring', 'exclusive'),
    ('curlystring', 'exclusive'),
)


_NAME_ELEMENTS = '^\s"#%\'(),={}'
_ANY_NAME = '[%s]+' % _NAME_ELEMENTS
_NOT_DIGNAME = '[%s\d][%s]*' % (_NAME_ELEMENTS, _NAME_ELEMENTS)
_END_BRACKETS = {'{': '}', '(': ')'}


# Initial state.  Soak up stuff between <newline>@ as implicit comments.  Also
# soak up any trailing not @ definition stuff at end of string, using the error
# handling.  Soak up explicit comments - they have odd bracket handling

t_IMPLICIT_COMMENT = r'(.|\n)*?\n\s*(?=@)'


_at_to_go = re.compile('\n\s*@')
def t_INITIAL_error(t):
    # Soak up any trailing lines
    match = _at_to_go.search(t.value)
    if match is None:
        # Move lexpos to signal handling of error
        t.lexer.lexpos = len(t.lexer.lexdata)
        t.type = 'IMPLICIT_COMMENT'
        return t


def t_EXPLICIT_COMMENT(t):
    r'\s*@comment([\s{(].*)?'
    # Function so we handle these before reaching AT below
    return t


def t_AT(t):
    r'\s*@'
    t.lexer.begin('defdef')
    return t


def to_initial_state(lexer):
    """ utility routine to return lexer to INITIAL state

    Clear any nested states or stateful cruft
    """
    lexer.entry_end = None
    lexer.entry_type = None
    lexer.lexerstatestack = []
    lexer.begin('INITIAL')


# defdef state is after @ and before we get to the content.  First we have to
# get what type of definition this is.  We stay in this state until we get past
# the LBRACKET

@lex.TOKEN(_NOT_DIGNAME)
def t_defdef_entrytype(t):
    entry_type = t.value.upper()
    if entry_type == 'STRING':
        t.type = 'MACRO'
    elif entry_type == 'PREAMBLE':
        t.type = 'PREAMBLE'
    else:
        t.type = 'ENTRY'
    t.lexer.entry_type = t.type
    return t


def t_defdef_entrydef_fielddef_quotestring_curlystring_error(t):
    # bomb out to INITAL state on error from this point
    to_initial_state(t.lexer)
    print("Illegal character '%s' at pos %d" %
          (t.value[0], t.lexer.lexpos))
    # Move lexpos to signal we have handled the error
    t.lexer.skip(1)


t_defdef_entrydef_fielddef_ignore = ' \t\n'


def t_defdef_LBRACKET(t):
    r'[{(]'
    # Now we are starting the body of the definition.  If this is an entry, then
    # we still need to collect the citekey and a comma.  Because the citekey can
    # start with digits, unlike field or macro names, we need a separate state
    # to collect those before we go field defining.

    # We check for the closing bracket to get out of the fielddef state
    t.lexer.entry_end = _END_BRACKETS[t.value]
    if t.lexer.entry_type in ('MACRO', 'PREAMBLE'):
        t.lexer.begin('fielddef')
    else:
        t.lexer.begin('entrydef')
    return t


t_entrydef_CITEKEY = _ANY_NAME


def t_entrydef_COMMA(t):
    r','
    # Now we are ready to define the fields in an entry
    t.lexer.begin('fielddef')
    return t


# fielddef state; common to the body of entries, preambles and macro
# definitions. We have to deal with quoted or curly brace strings, where the
# curly brace strings can be nested inside other curly brace strings or in a
# quoted string

t_fielddef_NAME = _NOT_DIGNAME # field name or macro name
t_fielddef_COMMA = ','
t_fielddef_EQUALS = '='
t_fielddef_HASH = r"\#"
t_fielddef_NUMBER = r'[0-9]+'


def t_fielddef_RBRACKET(t):
    r"[})]"
    # maybe we are leaving fielddef state
    if t.value == t.lexer.entry_end:
        to_initial_state(t.lexer)
    return t


def t_fielddef_QUOTE(t):
    r'"'
    t.lexer.push_state('quotestring')
    return t


def t_fielddef_quotestring_curlystring_LCURLY(t):
    r'{'
    # Deal with nested curly brace strings
    t.lexer.push_state('curlystring')
    return t


# Quotestring state; may need to deal with nested curly string. Quotes cannot be
# escaped within quoted strings, except by being within a nested curly string.

t_quotestring_STRING = r'[^"{}]+'


def t_quotestring_QUOTE(t):
    r'"'
    # escape from quoting state
    t.lexer.pop_state()
    return t


# Curly string state; can have nested curly strings.  Dealt with by the LCURLY
# shared definition function

t_curlystring_STRING = r"[^{}]+"


def t_curlystring_RCURLY(t):
    r'}'
    t.lexer.pop_state()
    return t


def make_lexer(*args, **kwargs):
    if not 'reflags' in kwargs:
        kwargs['reflags'] = re.IGNORECASE
    return lex.lex(*args, **kwargs)


def reset_lexer(lexer):
    lexer.begin("INITIAL")
    lexer.lexstatestack = []       # Stack of lexer states


lexer = make_lexer()

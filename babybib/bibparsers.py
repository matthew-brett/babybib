""" Parser for BibTeX files

A standalone parser using pyparsing.

To my knowledge there is no formal description of the syntax that BibTeX itself
uses when interpreting a ``.bib`` file.

This parser is the result of reading and experimentation with BibTeX.  The
experiments used test BibTeX files.  The ones I used are in the
``babybib/tests/bibs`` directory.  Reading included some extremely
well-documented prior art, such as `Nelson Beeb's bibliography tools`_ and Greg
Ward's btparse_.

Nelson Beebe proposed a formal syntax for BibTeX files for his BibTex programs
including bibparse.  His grammar is deliberately not quite the same as the rules
that BibTeX uses.

Greg Ward also wrote a parser for BibTeX files, and wrote it up in detail, in
the documentation for btparse and Text::BibTeX.  His grammar is like that of
bibparse in that it enforces slightly tighter rules than BibTeX it

.. _Nelson Beebe's bibliography tools: http://www.math.utah.edu/~beebe/software/bibtex-bibliography-tools.html
.. _btparse: http://search.cpan.org/dist/btparse

Matthew Brett 2010
Simplified BSD license
"""

import re

from pyparsing import (Regex, Suppress, ZeroOrMore, Group, Optional, Forward,
                       SkipTo, lineStart, Word, nums, CaselessLiteral,
                       restOfLine)


# Our character definitions
CHARS_NO_CURLY = Regex(r"[^{}]+")
CHARS_NO_CURLY.leaveWhitespace()
CHARS_NO_QUOTECURLY = Regex(r'[^"{}]+')
CHARS_NO_QUOTECURLY.leaveWhitespace()
LCURLY = Suppress('{')
RCURLY = Suppress('}')
LPAREN = Suppress('(')
RPAREN = Suppress(')')
QUOTE = Suppress('"')
COMMA = Suppress(',')
AT = Suppress('@')
EQUALS = Suppress('=')
HASH = Suppress('#')


def bracketed(expr):
    """ Return matcher for `expr` between curly brackets or parentheses """
    return (LPAREN + expr + RPAREN) | (LCURLY + expr + RCURLY)


# Define parser components for strings (the hard bit)
# Curly string is some stuff without curlies, or nested curly sequences
curly_string = Forward()
curly_item = Group(curly_string) | CHARS_NO_CURLY
curly_string << LCURLY + ZeroOrMore(curly_item) + RCURLY
# quoted string is either just stuff within quotes, or stuff within quotes, within
# which there is nested curliness
quoted_item = Group(curly_string) | CHARS_NO_QUOTECURLY
quoted_string = QUOTE + ZeroOrMore(quoted_item) + QUOTE

# Numbers can just be numbers. Only integers though.
number = Word(nums)

# Basis characters (by exclusion) for variable / field names.  The following
# list of characters is from the btparse documentation
any_name = Regex('[^\s"#%\'(),={}]+')

# btparse says, and the test bibs show by experiment, that macro and field names
# cannot start with a digit.  In fact entry type names cannot start with a digit
# either (see tests/bibs). Cite keys can start with a digit
not_digname = Regex('[^\d\s"#%\'(),={}][^\s"#%\'(),={}]*')

# where to go if there's an error during processing
error_start = Suppress(SkipTo(lineStart + '@'))

# Where to go when we've finished with the last entry
normal_start = Suppress(SkipTo('@'))

# Comment comments out to end of line
comment = (AT + Suppress(CaselessLiteral('comment')) +
           Regex("[\s{(].*").leaveWhitespace()).setResultsName('comment')

# Preamble start
preamble_id = Regex('preamble', re.IGNORECASE)

# Macro (string) start
macro_id = Regex('string', re.IGNORECASE)

# Id for macro def
class Macro(object):
    def __init__(self, name):
        self.name = name
    def __repr__(self):
        return 'Macro("%s")' % self.name
    def __eq__(self, other):
        return self.name == other.name
    def __ne__(self, other):
        return self.name != other.name

# The name types with their digiteyness
macro_def = not_digname.copy()
macro_ref = not_digname.copy().setParseAction(lambda s,l,t : Macro(t[0]))
field_name = not_digname.copy()
entry_type = not_digname.setResultsName('entry_type')
cite_key = any_name.setResultsName('cite_key')
# Number has to be before macro name
string = (number | macro_ref | quoted_string |
          curly_string)

# There can be hash concatenation
field_value = string + ZeroOrMore(HASH + string)
field_def = field_name + EQUALS + field_value
entry_contents = Group(
    ZeroOrMore(field_def + COMMA) + Optional(field_def))

# Entry is surrounded either by parentheses or curlies
entry = (AT + entry_type +
         bracketed(cite_key + COMMA + entry_contents) |
         error_start)

# Preamble is a macro-like thing with no name
preamble = (AT + Suppress(CaselessLiteral('preamble')) +
            bracketed(field_value)).setResultsName('preamble')

# Macros (aka strings)
macro = (AT + Suppress(CaselessLiteral('string')) +
         bracketed(macro_def + EQUALS + field_value)).setResultsName(
             'string')

# entries are last in the list (other than the fallback) because they have
# arbitrary start patterns that would match comments, preamble or macro
definitions = (comment |
               preamble |
               macro |
               entry |
               normal_start)

# Start symbol
bibfile = ZeroOrMore(definitions)


def parse_str(str):
    return bibfile.parseString(str)

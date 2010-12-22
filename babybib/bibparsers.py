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
bibparse in that it enforces slightly tighter rules than BibTeX itself.

.. _Nelson Beebe's bibliography tools: http://www.math.utah.edu/~beebe/software/bibtex-bibliography-tools.html
.. _btparse: http://search.cpan.org/dist/btparse

Matthew Brett 2010
Simplified BSD license
"""

DEBUG = True

import re

from pyparsing import (Regex, Suppress, ZeroOrMore, Group, Optional, Forward,
                       Literal, SkipTo, lineStart, Word, nums)

# Our character definitions
chars_no_curly = Regex(r"[^{}]+")
chars_no_curly.leaveWhitespace()
chars_no_quotecurly = Regex(r'[^"{}]+')
chars_no_quotecurly.leaveWhitespace()
lcurly = Suppress('{')
rcurly = Suppress('}')
lparen = Suppress('(')
rparen = Suppress(')')
quote = Suppress('"')
comma = Suppress(',')
at = Suppress('@')
equals = Suppress('=')
hash = Literal('#')

# Define parser for strings (the hard bit)
# Curly string is some stuff without curlies, or nested curly sequences
curly_string = Forward()
curly_item = Group(curly_string) | chars_no_curly
curly_string << lcurly + ZeroOrMore(curly_item) + rcurly
# quoted string is either just stuff within quotes, or stuff within quotes, within
# which there is nested curliness
quoted_item = Group(curly_string) | chars_no_quotecurly
quoted_string = quote + ZeroOrMore(quoted_item) + quote

# Now we define the entry contents.  The following list of characters is from
# the btparse documentation
any_name = Regex(r'[^\s"#%\'(),={}]+')
# btparse says, and the test bibs show by experiment, that macro and field names
# cannot start with a digit.  In fact entry type names cannot start with a digit
# either (see tests/bibs). Cite keys can start with a digit
not_digname = Regex(r'[^\d\s"#%\'(),={}][^\s"#%\'(),={}]*')
# macro names appearing on RHS and LHS of expressions have different parse
# actions.  Both are converted to strings. RHS occurences are a) checked for
# being in the parse dictionary, warning if not (null contents).  LHS occurences
# go into the the parse dictionary.
macro_lhs = not_digname.copy()
macro_rhs = not_digname.copy()
field_name = not_digname.copy()
entry_type = not_digname.copy()
cite_key = any_name.copy()
# Numbers can just be numbers. Only integers though.
number = Word(nums)
# Number has to be before macro name
string = number | macro_rhs | quoted_string | curly_string

# There can be hash concatenation
field_value = string + ZeroOrMore(hash + string)
field_def = field_name + equals + field_value
entry_contents = Group(ZeroOrMore(field_def + comma) + Optional(field_def))

# Convenience for our two types of brackets
def bracketed(expr):
    return (lparen + expr + rparen) | (lcurly + expr + rcurly)

# where to go if there's an error during processing
error_start = Suppress(SkipTo(lineStart + '@'))

# Where to go when we've finished with the last entry
normal_start = Suppress(SkipTo('@'))

# Entry is surrounded either by parentheses or curlies
entry = (at + entry_type + bracketed(cite_key + comma + entry_contents) |
         error_start)

# Comment comments out to end of line
comment = at + Regex('comment.*', re.IGNORECASE)

# Preamble is a macro-like thing with no name
preamble_id = Regex('preamble', re.IGNORECASE)
preamble = at + preamble_id + bracketed(field_value) | error_start

# Macros (aka strings)
macro_id = Regex('string', re.IGNORECASE)
macro = at + macro_id + bracketed(macro_lhs + equals + field_value) | error_start

# entries are last in the list (other than the fallback) because they have
# arbitrary start patterns that would match commments, preamble or macro
definitions = comment | preamble | macro | entry | normal_start

# Start symbol
bibfile = ZeroOrMore(definitions)


def parse_str(bib_str):
    return bibfile.parseString(bib_str)

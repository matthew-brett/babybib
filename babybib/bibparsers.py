""" Parser for bib files

A standalone parser using pyparsing based somewhat around the rules of bTOOL (C,
perl bindings - Greg Ward) and bibparse (lex / yacc / C - Nelson Beebe)

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
# cannot start with a digit
not_digname = Regex(r'[^\d\s"#%\'(),={}][^\s"#%\'(),={}]*')
macro_name = not_digname.copy()
number = Word(nums)
# Number has to be before macro name
string = number | macro_name | quoted_string | curly_string
# There can be hash concatenation
field_value = string + ZeroOrMore(hash + string)
field_name = not_digname.copy()
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
entry_type = not_digname.copy()
cite_key = any_name.copy()
entry = (at + entry_type + bracketed(cite_key + comma + entry_contents) |
         error_start)

# Comment just comments out to end of line
comment = at + Regex('comment.*', re.IGNORECASE)

# Preamble is just a macro-like thing with no name
preamble_id = Regex('preamble', re.IGNORECASE)
preamble = at + preamble_id + bracketed(field_value) | error_start

# Macros (aka strings)
macro_id = Regex('string', re.IGNORECASE)
macro = at + macro_id + bracketed(macro_name + equals + field_value) | error_start

# entries are last in the list (other than the fallback) because they have
# arbitrary start patterns that would match commments, preamble or macro
definitions = comment | preamble | macro | entry | normal_start

# Start symbol
bibfile = ZeroOrMore(definitions)


def parse_str(bib_str):
    return bibfile.parseString(bib_str)

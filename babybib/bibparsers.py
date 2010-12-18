""" Parsers for bib files """

DEBUG = True

import re

from pyparsing import (Regex, Suppress, ZeroOrMore, Group, Optional, Forward,
                       Literal, SkipTo, lineStart)

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
name = Regex(r'[^\s"#%\'(),={}]+')
string = quoted_string | curly_string | name
# There can be hash concatenation
field_value = string + ZeroOrMore(hash + string)
field_def = name + equals + field_value
entry_contents = Group(ZeroOrMore(field_def + comma) + Optional(field_def))

# Convenience for our two types of brackets
def bracketed(expr):
    return (lparen + expr + rparen) | (lcurly + expr + rcurly)

# Entry is surrounded either by parentheses or curlies
entry = at + name + bracketed(comma + entry_contents)

# Comment just comments out to end of line
comment = at + Regex('comment.*', re.IGNORECASE)

# where to go if there's an error during processing
error_start = Suppress(SkipTo(lineStart + '@'))

# Macros
macro_id = Regex('string', re.IGNORECASE)
macro = at + macro_id + bracketed(name + equals + field_value) | error_start

# Preamble
preamble_id = Regex('preamble', re.IGNORECASE)
preamble = at + preamble_id + bracketed(name + equals + field_value) | error_start

# Where to go next
normal_start = Suppress(SkipTo('@'))

# Start terminal symbol
definitions = comment | preamble | macro | entry | normal_start
bibfile = ZeroOrMore(definitions)


def parse_str(bib_str):
    return bibfile.parseString(bib_str)

""" Parsers for bib files """

DEBUG = True

import re

from pyparsing import (Regex, Suppress, ZeroOrMore, Group, Optional, Forward)

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
field_value = quoted_string | curly_string | name
field_def = name + equals + field_value
entry_contents = Group(ZeroOrMore(field_def + comma) + Optional(field_def))

# Entry is surrounded either by parentheses or curlies
entry = ((at + name + lcurly + name + comma + entry_contents + rcurly) |
         (at + name + lparen + name + comma + entry_contents + rparen))

# Comment just comments out to end of line
comment = at + Regex('comment.*', re.IGNORECASE)

# Macros
string_id = Regex('string', re.IGNORECASE)
macro = ((at + string_id + lcurly + name + equals + field_value + rcurly) |
         (at + string_id + lparen + name + equals + field_value + rparen))

# Preamble
preamble_id = Regex('preamble', re.IGNORECASE)
preamble = ((at + preamble_id + lcurly + name + equals + field_value + rcurly) |
         (at + preamble_id + lparen + name + equals + field_value + rparen))

# Start non-terminal
definitions = comment | preamble | macro | entry
bibfile = ZeroOrMore(definitions)


def parse_str(bib_str):
    return bibfile.parseString(bib_str)

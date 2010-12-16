""" Parsers for bib files """

DEBUG = True

from pyparsing import *

AT = Suppress("@")
comment = Regex(r"%.*").setName("bibtex style comment")
word = Word(alphas)
token = Word(alphanums) # for now
entry_type_id = AT + word
entry = Forward()
macro = Forward()
preamble = Forward()
members = entry | macro | preamble | comment
entry_type = AT + Word(alphas)
citekey = AT + token
block = Optional('{') + Optional('}') + Optional(',')
field = token + '=' + block
fields = Group( Optional(field) )
contents = citekey + ',' + Optional(fields)

lcurly = Suppress('{')
lparen = Suppress('(')
rcurly = Suppress('}')
rparen = Suppress(')')

chars_no_curly = Regex(r"[^{]*")
chars_no_paren = Regex(r"[^(]*")

curly_block = lcurly + chars_no_curly + rcurly
paren_block = lparen + chars_no_paren + rparen
block_item = chars_no_curly | curly_block | paren_block
block_items = Group(block_item)
block << ZeroOrMore(block_items)


bib_obj = Dict(Optional(members))

bib_obj.ignore(comment)

def parse_str(bib_str):
    return bib_obj.parseString(bib_str)

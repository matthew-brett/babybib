""" Testing ply parser for bibtex files
"""

from ..plyer import lexer

from nose.tools import assert_true, assert_equal, assert_raises

def test_plyer():
    lexer.input('hello @world\n more world \n\n @comment')
    print list(lexer)
    lexer.input('   @entry\n  hello world')
    print list(lexer)
    preamble = '@preamble({hello world {nested}})'
    lexer.input(preamble + ' \n ' + preamble + ' ')
    print list(lexer)
    lexer.input('@preamble("hello world")')
    print list(lexer)
    lexer.input('@preamble("hello {nested } world")')
    print list(lexer)
    lexer.input('@preamble("hello" # 19 # {world})')
    print list(lexer)

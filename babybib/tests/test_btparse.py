""" Testing btparse module
"""

from ..btparse import parser, macros, preamble
from ..btlex import lexer

from nose.tools import assert_true, assert_equal, assert_raises


def test_comment():
    print parser.parse('test/n   @comment some text', lexer=lexer)
    print parser.parse('@string{test = 1989}')
    print macros, preamble
    print parser.parse('@preamble{2012 # test}')
    print macros, preamble
    print parser.parse('@preamble{2013}')
    print macros, preamble
    print parser.parse('@entry{Me2014, author=1908,}')
    print parser.parse('@entry{Me2014, author=1908,title=1984}')

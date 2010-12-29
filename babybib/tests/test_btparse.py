""" Testing btparse module
"""

from ..btparse import parser
from ..btlex import lexer

from nose.tools import assert_true, assert_equal, assert_raises


def test_comment():
    assert_equal(parser.parse('test/n   @comment some text', lexer=lexer),
                 {})


def test_preamble_macro():
    assert_equal(parser.parse('@string{TEst = 1989}'), {})
    assert_equal(parser.defined_macros, {'test': ['1989']})
    assert_equal(parser.preamble, [])
    assert_equal(parser.parse('@preamble{"some text"}'), {})
    assert_equal(parser.defined_macros, {})
    assert_equal(parser.preamble, ['some text'])
    assert_equal(parser.parse('@string{TEst="a macro"}'
                              '@preamble("some text" # test)'
                              '@preamble{"more text"}'), {})
    assert_equal(parser.preamble, ['some text', 'a macro', 'more text'])


def test_entries():
    assert_equal(parser.parse('@an_entry{Me2014, author="Myself"}'),
                 {'Me2014': {'author': ['Myself'],
                             'entry type': 'an_entry'}})
    # Optional comma
    assert_equal(parser.parse('@an_entry{Me2014, author="Myself",}'),
                 {'Me2014': {'author': ['Myself'], 'entry type': 'an_entry'}})
    # Can be enclosed by comments, and contain numeric fields.  Field names
    # converted to lower case
    res = parser.parse("""
                       Some text
                       @another_entry{Me2014,
                       AUTHOR={Myself},
                       YEAR=1989
                       }
                       @comment text
                       """)
    assert_equal(res, {'Me2014': {'author': ['Myself'],
                                  'entry type': 'another_entry',
                                  'year': ['1989']}})
    # Can be empty
    assert_equal(parser.parse(''), {})
    # Have parentheses (and entry types are converted to lower case)
    assert_equal(parser.parse('@EnTrY(2012, author="me")'),
                              {'2012': {'author': ['me'],
                                        'entry type': 'entry'}})
    # Strings can be nested
    assert_equal(parser.parse('@entry(2012, author="me {too}")'),
                 {'2012': {'author': ['me ', ['too']],
                           'entry type': 'entry'}})
    # Be in single curlies
    assert_equal(parser.parse('@entry(2012, author={me})'),
                 {'2012': {'author': ['me'],
                           'entry type': 'entry'}})
    # Nested curlies
    assert_equal(parser.parse('@entry(2012, author={me {too {nested}}})'),
                 {'2012': {'author': ['me ',['too ', ['nested']]],
                           'entry type': 'entry'}})
    # Macro substitution
    assert_equal(parser.parse('@entry(2012, author={me {too {nested}}})'),
                 {'2012': {'author': ['me ',['too ', ['nested']]],
                           'entry type': 'entry'}})

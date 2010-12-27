""" Testing ply parser for bibtex files
"""

from ..plyer import lexer

from nose.tools import assert_true, assert_equal, assert_raises


def str2ttv(str):
    lexer.input(str)
    return [(t.type, t.value) for t in lexer]


def test_plyer_comment():
    str = 'hello @world\n more world \n\n @comment'
    assert_equal(str2ttv(str),
                 [('IMPLICIT_COMMENT', "hello @world\n more world \n\n "),
                  ('EXPLICIT_COMMENT', "@comment")])
    assert_equal(str2ttv(''),
                 [])
    assert_equal(str2ttv(' One line no entry'),
                 [('IMPLICIT_COMMENT', ' One line no entry')])



def test_plyer_preamble():
    str = '@preamble({hello world {nested}})'
    expected = [('PREAMBLE', 'preamble'),
                ('LCURLY', '{'),
                ('STRING', 'hello world '),
                ('LCURLY', '{'),
                ('STRING', 'nested'),
                ('RCURLY', '}'),
                ('RCURLY', '}')]
    assert_equal(str2ttv(str), expected)
    # case insenstive match to preamble
    assert_equal(str2ttv('@PREAmble({hello world {nested}})'),
                 expected)
    assert_equal(str2ttv(str + ' \n ' + str + ' '),
                 expected + expected + [('IMPLICIT_COMMENT', ' ')])
    assert_equal(str2ttv('@preamble("hello world")'),
                 [('PREAMBLE', 'preamble'),
                  ('QUOTE', '"'),
                  ('STRING', 'hello world'),
                  ('QUOTE', '"')])
    assert_equal(str2ttv('@preamble("hello {nested } world")'),
                 [('PREAMBLE', 'preamble'),
                  ('QUOTE', '"'),
                  ('STRING', 'hello '),
                  ('LCURLY', '{'),
                  ('STRING', 'nested '),
                  ('RCURLY', '}'),
                  ('STRING', ' world'),
                  ('QUOTE', '"')])
    assert_equal(str2ttv('@preamble("hello" # 19 # {world})'),
                 [('PREAMBLE', 'preamble'),
                  ('QUOTE', '"'),
                  ('STRING', 'hello'),
                  ('QUOTE', '"'),
                  ('HASH', '#'),
                  ('NUMBER', '19'),
                  ('HASH', '#'),
                  ('LCURLY', '{'),
                  ('STRING', 'world'),
                  ('RCURLY', '}')])


def test_macro():
    res = str2ttv('@string(aname = "some\nstring")\nA comment')
    assert_equal(res,
                 [('MACRO', 'string'),
                  ('FIELDNAME', 'aname'),
                  ('EQUALS', '='),
                  ('QUOTE', '"'),
                  ('STRING', 'some\nstring'),
                  ('QUOTE', '"'),
                  ('IMPLICIT_COMMENT', '\nA comment')])
    res = str2ttv('@string(aname = "some\nstring")\nA comment'
                  '@string(another = "a string")')
    # This below used to raise an error because the closing brackets were not
    # correctly matched
    str = \
"""@string{dcs87 = "Proceedings of the Seventh International Conference on
Distributed Computing Systems"}
% ACM DL Proceedings: - note the name changes since DL 96. --kevin
"""
    res = str2ttv(str)

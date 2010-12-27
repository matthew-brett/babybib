""" Testing ply parser for bibtex files
"""

from ..btlex import lexer

from nose.tools import assert_true, assert_equal, assert_raises


def str2ttv(str):
    lexer.input(str)
    return [(t.type, t.value) for t in lexer]


def test_comment():
    str = 'hello @world\n more world \n\n @comment'
    assert_equal(str2ttv(str),
                 [('IMPLICIT_COMMENT', "hello @world\n more world \n\n "),
                  ('EXPLICIT_COMMENT', "@comment")])
    assert_equal(str2ttv(''),
                 [])
    assert_equal(str2ttv('@comment some comments\n\n'),
                 [('EXPLICIT_COMMENT', '@comment some comments'),
                  ('IMPLICIT_COMMENT', '\n\n')])
    assert_equal(str2ttv('@comment{some comments\n\n'),
                 [('EXPLICIT_COMMENT', '@comment{some comments'),
                  ('IMPLICIT_COMMENT', '\n\n')])
    assert_equal(str2ttv('@comment(some comments\n\n'),
                 [('EXPLICIT_COMMENT', '@comment(some comments'),
                  ('IMPLICIT_COMMENT', '\n\n')])
    # End of file cruft
    assert_equal(str2ttv(' One line no entry'),
                 [('IMPLICIT_COMMENT', ' One line no entry')])


def test_preamble():
    str = '@preamble({hello world {nested}})'
    expected = [
        ('AT', '@'),
        ('PREAMBLE', 'preamble'),
        ('LBRACKET', '('),
        ('LCURLY', '{'),
        ('STRING', 'hello world '),
        ('LCURLY', '{'),
        ('STRING', 'nested'),
        ('RCURLY', '}'),
        ('RCURLY', '}'),
        ('RBRACKET', ')')]
    assert_equal(str2ttv(str), expected)
    # case insenstive match to preamble
    res = str2ttv('@PREAmble({hello world {nested}})')
    assert_equal([tn for tn, tv in res],
                 [tn for tn, tv in expected])
    assert_equal(str2ttv(str + ' \n ' + str + ' '),
                 (expected +
                  [('AT', ' \n @')] + expected[1:] +
                  [('IMPLICIT_COMMENT', ' ')]))
    assert_equal(str2ttv('@preamble("hello world")'),
                 [('AT', '@'),
                  ('PREAMBLE', 'preamble'),
                  ('LBRACKET', '('),
                  ('QUOTE', '"'),
                  ('STRING', 'hello world'),
                  ('QUOTE', '"'),
                  ('RBRACKET', ')')])
    assert_equal(str2ttv('@preamble("hello {nested } world")'),
                 [('AT', '@'),
                  ('PREAMBLE', 'preamble'),
                  ('LBRACKET', '('),
                  ('QUOTE', '"'),
                  ('STRING', 'hello '),
                  ('LCURLY', '{'),
                  ('STRING', 'nested '),
                  ('RCURLY', '}'),
                  ('STRING', ' world'),
                  ('QUOTE', '"'),
                  ('RBRACKET', ')')])
    assert_equal(str2ttv('@preamble("hello" # 19 # {world})'),
                 [('AT', '@'),
                  ('PREAMBLE', 'preamble'),
                  ('LBRACKET', '('),
                  ('QUOTE', '"'),
                  ('STRING', 'hello'),
                  ('QUOTE', '"'),
                  ('HASH', '#'),
                  ('NUMBER', '19'),
                  ('HASH', '#'),
                  ('LCURLY', '{'),
                  ('STRING', 'world'),
                  ('RCURLY', '}'),
                  ('RBRACKET', ')')])


def test_macro():
    res = str2ttv('@string(aname = "some\nstring")\nA comment')
    assert_equal(res,
                 [('AT', '@'),
                  ('MACRO', 'string'),
                  ('LBRACKET', '('),
                  ('NAME', 'aname'),
                  ('EQUALS', '='),
                  ('QUOTE', '"'),
                  ('STRING', 'some\nstring'),
                  ('QUOTE', '"'),
                  ('RBRACKET', ')'),
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


def test_entry():
    res = str2ttv(
"""@some_entry{Me2010,
        author="My Name",
        title="A title"
}""")
    assert_equal(res,
                 [('AT', '@'),
                  ('ENTRY', 'some_entry'),
                  ('LBRACKET', '{'),
                  ('CITEKEY', 'Me2010'),
                  ('COMMA', ','),
                  ('NAME', 'author'),
                  ('EQUALS', '='),
                  ('QUOTE', '"'),
                  ('STRING', 'My Name'),
                  ('QUOTE', '"'),
                  ('COMMA', ','),
                  ('NAME', 'title'),
                  ('EQUALS', '='),
                  ('QUOTE', '"'),
                  ('STRING', 'A title'),
                  ('QUOTE', '"'),
                  ('RBRACKET', '}')])

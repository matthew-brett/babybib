""" Test for bibparse grammar """

from pyparsing import ParseException, OneOrMore
from .. import bibparsers as bp

from nose.tools import assert_true, assert_false, assert_equal, assert_raises


def test_parse_string():
    # test string building blocks
    assert_equal(bp.chars_no_quotecurly.parseString('x')[0], 'x')
    assert_equal(bp.chars_no_quotecurly.parseString("a string")[0], 'a string')
    assert_equal(bp.chars_no_quotecurly.parseString('a "string')[0], 'a ')
    assert_equal(bp.chars_no_curly.parseString('x')[0], 'x')
    assert_equal(bp.chars_no_curly.parseString("a string")[0], 'a string')
    assert_equal(bp.chars_no_curly.parseString('a {string')[0], 'a ')
    assert_equal(bp.chars_no_curly.parseString('a }string')[0], 'a ')
    # test more general strings together
    for obj in (bp.curly_string, bp.string, bp.field_value):
        assert_equal(obj.parseString('{}').asList(), [])
        assert_equal(obj.parseString('{a "string}')[0], 'a "string')
        assert_equal(obj.parseString('{a {nested} string}').asList(),
                    ['a ', ['nested'], ' string'])
        assert_equal(obj.parseString('{a {double {nested}} string}').asList(),
                    ['a ', ['double ', ['nested']], ' string'])
    for obj in (bp.quoted_string, bp.string, bp.field_value):
        assert_equal(obj.parseString('""').asList(), [])
        assert_equal(obj.parseString('"a string"')[0], 'a string')
        assert_equal(obj.parseString('"a {nested} string"').asList(),
                    ['a ', ['nested'], ' string'])
        assert_equal(obj.parseString('"a {double {nested}} string"').asList(),
                    ['a ', ['double ', ['nested']], ' string'])
    # check names
    assert_raises(ParseException, bp.name.parseString, '## ')
    name_checker = OneOrMore(bp.name)
    assert_equal(name_checker.parseString('a name or two').asList(),
                 ['a','name','or','two'])
    # check that names also work for strings
    assert_equal(bp.string.parseString('someascii')[0], 'someascii')
    assert_raises(ParseException, bp.string.parseString, '%#=')


def test_parse_field():
    # test field value - hashes included
    fv = bp.field_value
    assert_equal(fv.parseString('aname')[0], 'aname')



""" Test for bibparse grammar """

from .. import bibparsers as bp

from nose.tools import assert_true, assert_false, assert_equal, assert_raises


def test_parse_string():
    assert_equal(bp.chars_no_quotecurly.parseString('x')[0], 'x')
    assert_equal(bp.chars_no_quotecurly.parseString("a string")[0], 'a string')
    assert_equal(bp.chars_no_quotecurly.parseString('a "string')[0], 'a ')
    assert_equal(bp.chars_no_curly.parseString('x')[0], 'x')
    assert_equal(bp.chars_no_curly.parseString("a string")[0], 'a string')
    assert_equal(bp.chars_no_curly.parseString('a {string')[0], 'a ')
    assert_equal(bp.chars_no_curly.parseString('a }string')[0], 'a ')
    cs = bp.curly_string
    assert_equal(cs.parseString('{}').asList(), [])
    assert_equal(cs.parseString('{a "string}')[0], 'a "string')
    assert_equal(cs.parseString('{a {nested} string}').asList(),
                 ['a ', ['nested'], ' string'])
    assert_equal(cs.parseString('{a {double {nested}} string}').asList(),
                 ['a ', ['double ', ['nested']], ' string'])
    qs = bp.quoted_string
    assert_equal(qs.parseString('""').asList(), [])
    assert_equal(qs.parseString('"a string"')[0], 'a string')
    assert_equal(qs.parseString('"a {nested} string"').asList(),
                 ['a ', ['nested'], ' string'])
    assert_equal(qs.parseString('"a {double {nested}} string"').asList(),
                 ['a ', ['double ', ['nested']], ' string'])


def test_parse_field():
    fv = bp.field_value
    res = fv.parseString('aname')
    print res



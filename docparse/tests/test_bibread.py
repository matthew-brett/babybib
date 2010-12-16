""" Testing bib reading
"""

from os.path import abspath, dirname, join as pjoin, split as psplit

from .. import bibparsers as bp

from nose.tools import assert_true, assert_equal, assert_raises

_mypath = dirname(__file__)
BIB_PATH = pjoin(_mypath, 'bibs')


def test_bib1():
    bib1_fname = pjoin(BIB_PATH, 'bib1.bib')
    bib1 = open(bib1_fname, 'rt').read()
    bibd = bp.parse_str(bib1)
    assert_equal(sorted(bibd.keys()), ['__key__',
                                       'author',
                                       'journal',
                                       'number',
                                       'pages',
                                       'title',
                                       'volume',
                                       'year'])
    assert_equal(bibd['__key__'], 'brett2002marsbar')
    assert_equal(bibd['journal'], 'Neuroimage')


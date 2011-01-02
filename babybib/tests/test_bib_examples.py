""" Testing example bibliographies
"""

DEBUG = True

from glob import glob
from os.path import dirname, join as pjoin, abspath, split as psplit, splitext

from ..btparse import BibTeXParser, BibTeXEntries as BTE

from nose.tools import assert_true, assert_equal, assert_raises


BIB_PATH = abspath(pjoin(dirname(__file__), 'bibs'))

BIBS = glob(pjoin(BIB_PATH, '*.bib'))

parser = BibTeXParser()

_exp_res = {
    'atfirst': BTE({'Me2010': {'title': ['An article\n@article',
                                         ['something, author=',
                                          ['Name, Another'],
                                          ', title=',
                                          ['not really an article']
                                         ], '\n'
                                        ],
                               'entry type': 'article',
                               'author': ['Brett, Matthew']},
                    'Me2009': {'title': ['A short story'],
                               'entry type': 'article',
                               'author': ['Nom de Plume, My']}}),
    'bib1': BTE({'Brett2002marsbar': {'title': [['Region of interest analysis '
                                                 'using an SPM toolbox']],
                                      'journal': ['Neuroimage'],
                                      'author': ['Matthew Brett and Jean-Luc '
                                                 'Anton and Romain Valabregue '
                                                 'and Jean-Baptise\n\tPoline'],
                                      'number': ['2'],
                                      'pages': ['1140--1141'],
                                      'volume': ['16'],
                                      'entry type': 'article',
                                      'year': ['2002'],
                                      'institution': []}}),
    'comments': BTE({'Me2011': {'entry type': 'article',
                                'author': ['Me really']},
                     'Me2010': {'title': ['An article'],
                                'entry type': 'article',
                                'author': ['Brett, Matthew']},
                     'Me2009': {'title': ['A short story'],
                                'entry type': 'article',
                                'author': ['Nom de Plume, My']}}),
    # the comments bib above should also generate comment parsing errors, but it
    # does not
    'curly_at': BTE({'Me2010': {'title': ['An @tey article'],
                                'entry type': 'article',
                                'author': ['Matthew Brett']},
                     'Me2009': {'title': ['A @tey short story'],
                                'entry type': 'article',
                                'author': ['Nom de Plume, My']}}),
    'entry_types': BTE({'an_id': {'entry type': 'somename'},
                        'another_id': {'entry type': 't2'},
                        'again_id': {'entry type': 't@'},
                        'aa1_id': {'entry type': 't+'},
                        'aa2_id': {'entry type': '_t'}}),
    'field_names': BTE({'2010': {'entry type': 'article'},
                        '2011': {'entry type': 'article', '_author': ['Me']},
                        '2012': {'entry type': 'article'},
                        '2013': {'entry type': 'article'},
                       }),
    'indented_at': BTE({'Me2010': {'title': ['An article'],
                                   'entry type': 'article',
                                   'author': ['Brett, Matthew']},
                        'Me2009': {'title': ['A short story'],
                                   'entry type': 'article',
                                   'author': ['Nom de Plume, My']},
                       }),
    'inline_comment': BTE({'Me2010': {'entry type': 'article',
                                      'author': ['Brett, Matthew']},
                           'Me2011': {'entry type': 'article',
                                      'author': ['Brett-like, Matthew']},
                           'Me2012': {'entry type': 'article'},
                           'Me2013': {'entry type': 'article',
                                      'author': ['Nom de Plume, My'],
                                      'title': ['A short story']},
                          }),
    }


def test_bibs():
    for bibfile in BIBS:
        _, name = psplit(bibfile)
        name, _ = splitext(name)
        txt = open(bibfile, 'rt').read()
        res = parser.parse(txt)
        if name in _exp_res:
            assert_equal(res, _exp_res[name])
        elif DEBUG:
            print name
            print res.entries

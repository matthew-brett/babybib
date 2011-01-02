""" Testing example bibliographies
"""

DEBUG = True

from glob import glob
from os.path import dirname, join as pjoin, abspath, split as psplit, splitext

from ..btparse import BibTeXParser, BibTeXEntries as BTE, Macro

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
                        '2014': {'.name': ["Myself"],
                                 'entry type': 'article'},
                        '2015': {'+name': ["Myself"],
                                 'entry type': 'article'},
                        '2016': {'-name': ["Myself"],
                                 'entry type': 'article'},
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
    'inline_string': BTE({'Me2010': {'entry type': 'article',
                                      'author': ['Brett, Matthew']},
                           'Me2009': {'entry type': 'article',
                                      'author': ['Nom de Plume, My'],
                                      'title': ['A short story']},
                          }),
    'nospace': BTE({'Me2010': {'entry type': 'article',
                               'title': ['An article'],
                               'author': ['Brett, Matthew']},
                    'Me2009': {'entry type': 'article',
                               'author': ['Nom de Plume, My'],
                               'title': ['A short story']},
                   }),
    'nospace_strings': BTE({'Me2010': {'author': ['some string'],
                                       'title': ['another string'],
                                       'entry type': 'article'}},
                           defined_macros = dict(
                               string1=['some string'],
                               string2 = ['another string'])),
    'numbers': BTE({'Me2010': {'year': ['3'],
                              'entry type': 'article'},
                    'Me2011': {'year': [Macro('.3')],
                               'author': ['Me'],
                               'entry type': 'article'},
                    'Me2012': {'year': ['0'],
                               'entry type': 'article'},
                    'Me2013': {'author': ['Me2'],
                               'year': [Macro('-42')],
                               'entry type': 'article'},
                    'Me2014': {'author': ['Me3'],
                               'year': [Macro('+42')],
                               'entry type': 'article'},
                  }),
    'parentheses': BTE({'Me2010': {'author': ['me'],
                                   'entry type': 'article'},
                        'Me2009': {'author': ['one string'],
                                   'title': [Macro('anstring')],
                                   'entry type': 'article'},
                        'Me2008': {'author': ['Me ) Again'],
                                   'title': ['Stuff from me'],
                                   'entry type': 'article'}},
                       defined_macros = dict(astring = ['one string']),
                       undefined_macros = dict(
                           anstring = [[Macro('anstring')]])),
    'quotes_curlies': BTE({'Me2010': {'author': ['Matthew \\'],
                                      'entry type': 'article'},
                           'Me2011': {'author': ['Matthew ', ['"'], 'Brett'],
                                      'entry type': 'article'},
                           'Me2012': {'author': [r'Matthew "Brett'],
                                      'entry type': 'article'},
                           'Me2013': {'author': ['Matthew \\',
                                                 [' Brett \\']],
                                      'entry type': 'article'},
                          }),
    'preamble': BTE(defined_macros = dict(maintainer=["Xavier D\\'ecoret"]),
                    preamble = [
                        "This bibliography was generated on \\today",
                        "This bibliography was generated on \\today",
                        "Maintained by ", "Xavier D\\'ecoret",
                                "can also be ", ["nested ", ['deeply ']],
                                '1999']),
    'strings': BTE({'Me2009': {'author': [Macro('aname')],
                               'entry type': 'article'},
                    'Me2011': {'author': ['A Name', 'a string'],
                               'entry type': 'article'},
                    'Me2012': {'author': [Macro('jan')],
                               'title': [Macro('feb')],
                               'entry type': 'article'},
                    'Me2013': {'author': ['A name later'],
                               'entry type': 'article'},
                    'Me2014': {'author': ['A cold month'],
                               'entry type': 'article'},
                    'Me2010': {'author': ['A Name'],
                               'title': ['two thousand'],
                               'year': ['A Name'],
                               'number': ['one thousand'],
                               'entry type': 'article'}},
                   defined_macros=dict(
                       aname=['A Name'],
                       another_name=['A Name'],
                       yet_another=['A Name']),
                   undefined_macros=dict(
                       aname=[[Macro('aname')]])),
    'wikip1': BTE({'abramowitz+stegun':
                   {'publisher': ['Dover'],
                    'author': ['Milton ', ['Abramowitz'],
                               ' and Irene A. ', ['Stegun']],
                    'title': ['Handbook of Mathematical Functions with\n'
                              '              Formulas, Graphs, and '
                              'Mathematical Tables'],
                    'address': ['New York'],
                    'edition': ['ninth Dover printing, tenth GPO printing'],
                    'entry type': 'book',
                    'year': ['1964']}}),
    'wikip2': BTE({'hicks2001':
                   {'author': ['von Hicks, III, Michael'],
                    'title': ["Design of a Carbon Fiber Composite Grid "
                              "Structure for the GLAST\n"
                              "              Spacecraft Using a Novel "
                              "Manufacturing Technique"],
                    'publisher': ['Stanford Press'],
                    'year': ['2001'],
                    'address': ['Palo Alto'],
                    'edition': ['1st,'],
                    'isbn': ['0-69-697269-4'],
                    'entry type': 'book'}}),
    'wikip3': BTE({'Torre2008':
                   {'author': ['Joe Torre and Tom Verducci'],
                    'publisher': ['Doubleday'],
                    'title': ['The Yankee Years'],
                    'year': ['2008'],
                    'isbn': ['0385527403'],
                    'entry type': 'book'},
                   }),
    'wikip4': BTE({'author:06':
                   {'title': ['Some publication title'],
                    'author': ['First Author and Second Author'],
                    'crossref': ["conference:06"],
                    'pages': ['330-331'],
                    'entry type': 'inproceedings'},
                   'conference:06':
                   {'editor': ['First Editor and Second Editor'],
                    'title': ['Proceedings of the Xth Conference on XYZ'],
                    'booktitle': ['Proceedings of the Xth Conference on XYZ'],
                    'year': ['2006'],
                    'month': [Macro('oct')],
                    'entry type': 'proceedings'}}),
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

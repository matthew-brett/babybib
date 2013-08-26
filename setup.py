#!/usr/bin/env python
# emacs: -*- mode: python-mode; py-indent-offset: 4; indent-tabs-mode: nil -*-
# vi: set ft=python sts=4 ts=4 sw=4 et:
### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ##
#
#   See COPYING file distributed along with the NiBabel package for the
#   copyright and license terms.
#
### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ##
"""Build helper."""

import os
from os.path import join as pjoin
import sys

# BEFORE importing distutils, remove MANIFEST. distutils doesn't properly
# update it when the contents of directories change.
if os.path.exists('MANIFEST'): os.remove('MANIFEST')

# For some commands, use setuptools.
if len(set(('develop', 'bdist_egg', 'bdist_rpm', 'bdist', 'bdist_dumb',
            'install_egg_info', 'egg_info', 'easy_install',
            )).intersection(sys.argv)) > 0:
    # setup_egg imports setuptools setup, thus monkeypatching distutils.
    import setup_egg

from distutils.core import setup

extra_setuptools_args = {}
if 'setuptools' in sys.modules:
    extra_setuptools_args = dict(
        tests_require=['nose'],
        test_suite='nose.collector',
        zip_safe=False,
        extras_require = dict(
            doc='Sphinx>=0.3',
            test='nose>=0.10.1')
    )

CLASSIFIERS = ["Development Status :: 3 - Alpha",
               "Environment :: Console",
               "Intended Audience :: Science/Research",
               "License :: OSI Approved :: BSD License",
               "Operating System :: OS Independent",
               "Programming Language :: Python",
               "Topic :: Scientific/Engineering"]

def main(**extra_args):
    setup(name='babybib',
          maintainer='Matthew Brett',
          maintainer_email='matthew.brett@gmail.com',
          description="A small bibtex parser in Python",
          long_description=open('README.rst', 'rt').read(),
          url="https://github.com/matthew-brett/babybib",
          # download_url=DOWNLOAD_URL,
          license='BSD License',
          classifiers=CLASSIFIERS,
          author="Matthew Brett",
          author_email="matthew.brett@gmail.com",
          platforms="OS Independent",
          version="0.1",
          requires='',
          provides=['babybib'],
          packages = ['babybib',
                      'babybib.tests',
                      'babybib.ply'],
          # The package_data spec has no effect for me (on python 2.6) -- even
          # changing to data_files doesn't get this stuff included in the source
          # distribution -- not sure if it has something to do with the magic
          # above, but distutils is surely the worst piece of code in all of
          # python -- duplicating things into MANIFEST.in but this is admittedly
          # only a workaround to get things started -- not a solution
          package_data = {'babybib':
                          [pjoin('tests', 'bibs', '*'),
                           pjoin('tests', 'bibtexing', '*'),
                          ]},
          scripts      = [pjoin('bin', 'bib2rst'),
                          ],
          **extra_args
         )


if __name__ == "__main__":
    main(**extra_setuptools_args)

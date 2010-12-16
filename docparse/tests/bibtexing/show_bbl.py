#!/usr/bin/env python
"""
Read bib file and write bbl file to stdout

Based on test_names.py by Xavier Decoret
"""

usage = "usage: %prog [options] bibfile [bibfile [bibfile]]"

import os
from os.path import dirname, join as pjoin, abspath
import sys
import shutil
import tempfile
from subprocess import check_call
from optparse import OptionParser

_my_path = dirname(__file__)

def mycall(cmd):
    return check_call(cmd, shell=True)


def main():
    parser = OptionParser(usage=usage)
    parser.add_option("-s", "--style",
                      help="format entries using STYLE (default is custom "
                      "'names.bst' style",
                      metavar="STYLE")
    parser.add_option("-c", "--in-cwd",
                      action='store_true',
                      default=False,
                      help="run in current directory")
    (options, bibfiles) = parser.parse_args()
    if len(bibfiles) == 0:
        parser.print_help()
        sys.exit(0)
    if options.style is None:
        options.style = abspath(pjoin(_my_path, 'names.bst'))
    if not options.in_cwd:
        if options.style.endswith('.bst'):
            options.style = abspath(options.style)
        bibfiles = [abspath(bibfile) for bibfile in bibfiles]
        pwd = os.getcwd()
        tmpdir = tempfile.mkdtemp()
        try:
            os.chdir(tmpdir)
            show_bbl(options.style, bibfiles)
        finally:
            os.chdir(pwd)
            shutil.rmtree(tmpdir)
    else:
        show_bbl(options.style, bibfiles)


def show_bbl(style, bibfiles):
    test_file = open("test.tex","wt")
    test_file.write(r"""
\documentclass{article}
\begin{document}
\nocite{*}
\bibliographystyle{%s}
\bibliography{%s}
\end{document}
""" % (style, ','.join(bibfiles)))
    test_file.close()
    mycall(r"latex \\nonstopmode \\input{test.tex}")
    mycall("bibtex test")
    print open('test.bbl', 'rt').read()


if __name__ == '__main__':
    main()



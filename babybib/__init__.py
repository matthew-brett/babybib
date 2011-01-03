""" BibTeX parser

The standard parser uses ply_ - :mod:`btparse`.

To my knowledge there is no formal description of the syntax that BibTeX itself
uses when interpreting a ``.bib`` file.  The parser here tries to do the same
thing as BibTeX, roughly, rather than extend or formalize BibTeX grammar.  The
behavior of the parser is the result of reading what other people have written
or done, and experiments with BibTeX.  The small BibTeX test files should be in
the ``babybib/tests/bibs`` directory.  Reading included some extremely
well-documented prior art, such as `Nelson Beeb's bibliography tools`_ and Greg
Ward's btparse_.

Nelson Beebe proposed a formal syntax for BibTeX files for his BibTex programs
including bibparse.  His grammar is deliberately not quite the same as the rules
that BibTeX uses.

Greg Ward also wrote a parser for BibTeX files, and wrote it up in detail, in
the documentation for btparse and Text::BibTeX.  His grammar is like that of
bibparse in that it enforces slightly tighter rules than BibTeX does.

.. _ply: http://www.dabeaz.com/ply
.. _bibstuff: http://pricklysoft.org/software/bibstuff.html
.. _Nelson Beebe's bibliography tools: http://www.math.utah.edu/~beebe/software/bibtex-bibliography-tools.html
.. _btparse: http://search.cpan.org/dist/btparse

Matthew Brett 2010
Simplified BSD license
"""
# init for babybib

from .btparse import parse, BibTeXParser, BibTeXEntries

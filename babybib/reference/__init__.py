""" For-show parser using pyparsing

Actually I wrote this parser first, but it was a little slow, and I didn't know
how to do error recovery, so I moved to ply for the standard parser.

pyparsing is very elegant and expressive, so the syntax that results is easy to
read.  It's more or less the same as the syntax in the ply-based parser, without
the error handling.
"""

import btpyparse
from .btpyparse import parse_str

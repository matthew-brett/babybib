#!/usr/bin/python
# In Emacs, use -*- mode: python -*-

import string,sys,os,re;

import getopt
opts, pargs = getopt.getopt(sys.argv[1:],'',['help', 'style='])
describe = None

usage = 0
style = 'names'
for k,v in opts:
    if  k=='--help':
        usage = 1
    elif k == '--style':
        style = v

if usage:
        print "usage: %s --help [--style <stylename>]" % sys.argv[0]
        sys.exit(0)

r = re.compile("\\.bib");

bibfiles = []
for f in pargs:    
    m = r.search(f)
    if m:
        bibfiles.append(f[:m.start()])

testFile = open("test.tex","w")

print >>testFile,"\\documentclass{article}"
print >>testFile,"\\begin{document}"
print >>testFile,"\\nocite{*}"
print >>testFile,"\\bibliographystyle{%s}" % style
print >>testFile,"\\bibliography{%s}\n" % string.join(bibfiles,",")
print >>testFile,"\\end{document}"
testFile.close()

os.system("latex \\\\nonstopmode \\\\input{test.tex}")
os.system("bibtex test")
os.system("more test.bbl")





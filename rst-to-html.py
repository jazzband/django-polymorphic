#!/usr/bin/python

import sys,os

css='--stylesheet-path=rst.css'

def conv(name):
    if len(sys.argv)>1:
        os.system('rst2html.py '+css+' %s.rst >%s.html' % (name, name) )
    else:
        os.system('rst2html.py '+css+' %s.rst >%s.html ; firefox %s.html' % (name, name, name) )

conv('DOCS')
conv('README')
conv('CHANGES')

sys.exit()



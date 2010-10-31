#!/usr/bin/python

import sys,os

dopart = None
if len(sys.argv)>1: dopart = sys.argv[1]
noshow = 'noshow' in sys.argv

css='--stylesheet-path=rst.css'

def conv(name):
    print 'convert',name
    if noshow:
        os.system('rst2html.py '+css+' %s.rst >%s.html' % (name, name) )
    else:
        os.system('rst2html.py '+css+' %s.rst >%s.html ; firefox %s.html' % (name, name, name) )

if not dopart or dopart=='1': conv('DOCS')
if not dopart or dopart=='2': conv('README')
if not dopart or dopart=='3': conv('CHANGES')

sys.exit()



# -*- coding: utf-8 -*-
"""
This module is a scratchpad for general development, testing & debugging
"""

from django.core.management.base import NoArgsCommand
from django.db.models import connection
from poly.models import *
from pprint import pprint

def reset_queries():
    connection.queries=[]

def show_queries():
    print; print 'QUERIES:',len(connection.queries); pprint(connection.queries); print; connection.queries=[]
    
class Command(NoArgsCommand):
    help = ""

    def handle_noargs(self, **options):
        print "polycmd"

        ModelA.objects.all().delete()
        
        o=ModelA.objects.create(field1='A1')
        o=ModelB.objects.create(field1='B1', field2='B2')
        o=ModelC.objects.create(field1='C1', field2='C2', field3='C3')
        
        print ModelA.objects.all()

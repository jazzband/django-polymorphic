# -*- coding: utf-8 -*-
"""
This module is a scratchpad for general development, testing & debugging
"""
import uuid

from django.core.management.base import NoArgsCommand
from django.db.models import connection
from pprint import pprint
import settings

from pexp.models import *

def reset_queries():
    connection.queries=[]

def show_queries():
    print; print 'QUERIES:',len(connection.queries); pprint(connection.queries); print; connection.queries=[]

class Command(NoArgsCommand):
    help = ""

    def handle_noargs(self, **options):
        print 'polycmd - sqlite test db is stored in:',settings.SQLITE_DB_PATH
        print

        Project.objects.all().delete()
        a=Project.objects.create(topic="John's gathering")
        b=ArtProject.objects.create(topic="Sculpting with Tim", artist="T. Turner")
        c=ResearchProject.objects.create(topic="Swallow Aerodynamics", supervisor="Dr. Winter")
        print Project.objects.all()
        print

        ModelA.objects.all().delete()
        a=ModelA.objects.create(field1='A1')
        b=ModelB.objects.create(field1='B1', field2='B2')
        c=ModelC.objects.create(field1='C1', field2='C2', field3='C3')
<<<<<<< HEAD:pexp/management/commands/p2cmd.py
        print ModelA.objects.extra( select={"select1": "field1 = 'A1'", "select2": "field1 = 'A0'"} )
=======
        print ModelA.objects.extra( select={"select1": "field1 = 'A1'", "select2": "field1 != 'A1'"} )
>>>>>>> 7c2be35... pexp:pexp/management/commands/p2cmd.py
        print

        if not 'UUIDField' in globals(): return
        UUIDModelA.objects.all().delete()
        a=UUIDModelA.objects.create(field1='012345678900123456789001234567890012345678900123456789001234567890')
        b=UUIDModelB.objects.create(field1='B1', field2='B2')
        c=UUIDModelC.objects.create(field1='C1', field2='C2', field3='C3')
        print UUIDModelA.objects.all()

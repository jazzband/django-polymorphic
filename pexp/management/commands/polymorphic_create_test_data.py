# -*- coding: utf-8 -*-
"""
This module is a scratchpad for general development, testing & debugging
"""

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
        o=Project.objects.create(topic="John's gathering")
        o=ArtProject.objects.create(topic="Sculpting with Tim", artist="T. Turner")
        o=ResearchProject.objects.create(topic="Swallow Aerodynamics", supervisor="Dr. Winter")
        print Project.objects.all()
        print
        



# -*- coding: utf-8 -*-
# flake8: noqa
"""
This module is a scratchpad for general development, testing & debugging.
"""

from django.core.management.base import NoArgsCommand
from django.db.models import connection
from pprint import pprint

from pexp.models import *

def reset_queries():
    connection.queries=[]

def show_queries():
    print; print 'QUERIES:',len(connection.queries); pprint(connection.queries); print; connection.queries=[]

class Command(NoArgsCommand):
    help = ""

    def handle_noargs(self, **options):
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
        print ModelA.objects.all()
        print


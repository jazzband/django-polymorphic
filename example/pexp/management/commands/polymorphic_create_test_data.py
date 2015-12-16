# -*- coding: utf-8 -*-
"""
This module is a scratchpad for general development, testing & debugging
"""

from django.core.management.base import NoArgsCommand
from django.db.models import connection
from pprint import pprint

from pexp import models


def reset_queries():
    connection.queries = []


def show_queries():
    print()
    print('QUERIES:', len(connection.queries))
    pprint(connection.queries)
    print
    connection.queries = []


class Command(NoArgsCommand):
    help = ""

    def handle_noargs(self, **options):
        models.Project.objects.all().delete()
        models.Project.objects.create(topic="John's gathering")
        models.ArtProject.objects.create(
            topic="Sculpting with Tim",
            artist="T. Turner",
        )
        models.ResearchProject.objects.create(
            topic="Swallow Aerodynamics",
            supervisor="Dr. Winter",
        )
        print(models.Project.objects.all())
        print()

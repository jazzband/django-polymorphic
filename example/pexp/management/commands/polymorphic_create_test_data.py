# -*- coding: utf-8 -*-
"""
This module is a scratchpad for general development, testing & debugging
"""

from django.core.management.base import NoArgsCommand

from pexp.models import *


class Command(NoArgsCommand):
    help = ""

    def handle_noargs(self, **options):
        Project.objects.all().delete()
        o = Project.objects.create(topic="John's gathering")
        o = ArtProject.objects.create(topic="Sculpting with Tim", artist="T. Turner")
        o = ResearchProject.objects.create(topic="Swallow Aerodynamics", supervisor="Dr. Winter")
        print Project.objects.all()
        print

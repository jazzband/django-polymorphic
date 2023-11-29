"""
This module is a scratchpad for general development, testing & debugging
"""

from django.core.management import BaseCommand
from pexp.models import Project, ArtProject, ResearchProject


class Command(BaseCommand):
    help = ""

    def handle_noargs(self, **options):
        Project.objects.all().delete()
        _ = Project.objects.create(topic="John's gathering")
        _ = ArtProject.objects.create(topic="Sculpting with Tim", artist="T. Turner")
        _ = ResearchProject.objects.create(topic="Swallow Aerodynamics", supervisor="Dr. Winter")
        print(Project.objects.all())

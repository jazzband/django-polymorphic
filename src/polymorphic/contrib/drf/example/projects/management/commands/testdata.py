from django.core.management.base import BaseCommand

from projects.models import ArtProject, Project, ResearchProject


class Command(BaseCommand):
    help = "Generates test data"

    def handle(self, *args, **options):
        Project.objects.all().delete()
        Project.objects.create(topic="Project title #1")
        ArtProject.objects.create(topic="Art project title #1", artist="T. Artist")
        ResearchProject.objects.create(
            topic="Research project title #1", supervisor="Dr. Research"
        )

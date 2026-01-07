from django.db import models
from polymorphic.models import PolymorphicModel


class Project(PolymorphicModel):
    topic = models.CharField(max_length=30)


class ArtProject(Project):
    artist = models.CharField(max_length=30)


class ResearchProject(Project):
    supervisor = models.CharField(max_length=30)

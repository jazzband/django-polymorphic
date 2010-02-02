from django.db import models

from polymorphic.models import PolymorphicModel, PolymorphicManager, PolymorphicQuerySet, ShowFields, ShowFieldsAndTypes


class Project(ShowFields, PolymorphicModel):
    topic = models.CharField(max_length=30)
class ArtProject(Project):
    artist = models.CharField(max_length=30)
class ResearchProject(Project):
    supervisor = models.CharField(max_length=30)

class ModelA(PolymorphicModel):
    field1 = models.CharField(max_length=10)
class ModelB(ModelA):
    field2 = models.CharField(max_length=10)
class ModelC(ModelB):
    field3 = models.CharField(max_length=10)

class SModelA(ShowFieldsAndTypes, PolymorphicModel):
    field1 = models.CharField(max_length=10)
class SModelB(SModelA):
    field2 = models.CharField(max_length=10)
class SModelC(SModelB):
    field3 = models.CharField(max_length=10)

# for Django 1.2+, test models with same names in different apps
# (the other models with identical names are in polymorphic/tests.py)
from django import VERSION as django_VERSION
if not (django_VERSION[0]<=1 and django_VERSION[1]<=1):
    class Model2A(PolymorphicModel):
        field1 = models.CharField(max_length=10)
    class Model2B(Model2A):
        field2 = models.CharField(max_length=10)
    class Model2C(Model2B):
        field3 = models.CharField(max_length=10)

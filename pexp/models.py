# -*- coding: utf-8 -*-

from django.db import models

from polymorphic import PolymorphicModel, PolymorphicManager, PolymorphicQuerySet
from polymorphic.showfields import ShowFieldContent, ShowFieldType, ShowFieldTypeAndContent

class Project(ShowFieldContent, PolymorphicModel):
    topic = models.CharField(max_length=30)
class ArtProject(Project):
    artist = models.CharField(max_length=30)
class ResearchProject(Project):
    supervisor = models.CharField(max_length=30)

class ModelA(ShowFieldTypeAndContent, PolymorphicModel):
    field1 = models.CharField(max_length=10)
class ModelB(ModelA):
    field2 = models.CharField(max_length=10)
class ModelC(ModelB):
    field3 = models.CharField(max_length=10)

class nModelA(models.Model):
    field1 = models.CharField(max_length=10)
class nModelB(nModelA):
    field2 = models.CharField(max_length=10)
class nModelC(nModelB):
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

try: from polymorphic.test_tools  import UUIDField
except: pass
if 'UUIDField' in globals():
    class UUIDModelA(ShowFieldTypeAndContent, PolymorphicModel):
        uuid_primary_key = UUIDField(primary_key = True)
        field1 = models.CharField(max_length=10)
    class UUIDModelB(UUIDModelA):
        field2 = models.CharField(max_length=10)
    class UUIDModelC(UUIDModelB):
        field3 = models.CharField(max_length=10)

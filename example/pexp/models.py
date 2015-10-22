# -*- coding: utf-8 -*-

import django
from django.db import models

from polymorphic.models import PolymorphicModel
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

class Model2A(PolymorphicModel):
    field1 = models.CharField(max_length=10)
class Model2B(Model2A):
    field2 = models.CharField(max_length=10)
class Model2C(Model2B):
    field3 = models.CharField(max_length=10)

if django.VERSION < (1,8):
    from polymorphic.tools_for_tests import UUIDField
else:
    from django.db.models import UUIDField

class UUIDModelA(ShowFieldTypeAndContent, PolymorphicModel):
    uuid_primary_key = UUIDField(primary_key = True)
    field1 = models.CharField(max_length=10)
class UUIDModelB(UUIDModelA):
    field2 = models.CharField(max_length=10)
class UUIDModelC(UUIDModelB):
    field3 = models.CharField(max_length=10)

class ProxyBase(PolymorphicModel):
    title = models.CharField(max_length=200)

    def __unicode__(self):
        return u"<ProxyBase[type={0}]: {1}>".format(self.polymorphic_ctype, self.title)

    class Meta:
        ordering = ('title',)

class ProxyA(ProxyBase):
    class Meta:
        proxy = True

    def __unicode__(self):
        return u"<ProxyA: {0}>".format(self.title)

class ProxyB(ProxyBase):
    class Meta:
        proxy = True

    def __unicode__(self):
        return u"<ProxyB: {0}>".format(self.title)

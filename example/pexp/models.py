# -*- coding: utf-8 -*-

from django.db import models

from polymorphic.models import PolymorphicModel
from polymorphic.showfields import ShowFieldContent, ShowFieldTypeAndContent


class Project(ShowFieldContent, PolymorphicModel):
    """Polymorphic model"""
    topic = models.CharField(max_length=30)


class ArtProject(Project):
    artist = models.CharField(max_length=30)


class ResearchProject(Project):
    supervisor = models.CharField(max_length=30)


class UUIDModelA(ShowFieldTypeAndContent, PolymorphicModel):
    """UUID as primary key example"""
    uuid_primary_key = models.UUIDField(primary_key=True)
    field1 = models.CharField(max_length=10)


class UUIDModelB(UUIDModelA):
    field2 = models.CharField(max_length=10)


class UUIDModelC(UUIDModelB):
    field3 = models.CharField(max_length=10)


class ProxyBase(PolymorphicModel):
    """Proxy model example - a single table with multiple types."""
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


# Internals for management command tests

class TestModelA(ShowFieldTypeAndContent, PolymorphicModel):
    field1 = models.CharField(max_length=10)


class TestModelB(TestModelA):
    field2 = models.CharField(max_length=10)


class TestModelC(TestModelB):
    field3 = models.CharField(max_length=10)
    field4 = models.ManyToManyField(TestModelB, related_name='related_c')


class NormalModelA(models.Model):
    """Normal Django inheritance, no polymorphic behavior"""
    field1 = models.CharField(max_length=10)


class NormalModelB(NormalModelA):
    field2 = models.CharField(max_length=10)


class NormalModelC(NormalModelB):
    field3 = models.CharField(max_length=10)

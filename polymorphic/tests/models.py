# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from django.db import models
from django.db.models.query import QuerySet
from django.contrib.contenttypes.models import ContentType

from polymorphic import PolymorphicModel, PolymorphicManager, PolymorphicQuerySet

from .fields import UUIDField
from .showfields import ShowFieldContent, ShowFieldType, ShowFieldTypeAndContent


##


class PlainA(models.Model):
    field1 = models.CharField(max_length=10)


class PlainB(PlainA):
    field2 = models.CharField(max_length=10)


class PlainC(PlainB):
    field3 = models.CharField(max_length=10)


##


class Model2A(ShowFieldType, PolymorphicModel):
    field1 = models.CharField(max_length=10)


class Model2B(Model2A):
    field2 = models.CharField(max_length=10)


class Model2C(Model2B):
    field3 = models.CharField(max_length=10)


class Model2D(Model2C):
    field4 = models.CharField(max_length=10)


##


class ModelExtraA(ShowFieldTypeAndContent, PolymorphicModel):
    field1 = models.CharField(max_length=10)


class ModelExtraB(ModelExtraA):
    field2 = models.CharField(max_length=10)


class ModelExtraC(ModelExtraB):
    field3 = models.CharField(max_length=10)


class ModelExtraExternal(models.Model):
    topic = models.CharField(max_length=10)


##


class ModelShow1(ShowFieldType, PolymorphicModel):
    field1 = models.CharField(max_length=10)
    m2m = models.ManyToManyField('self')


class ModelShow2(ShowFieldContent, PolymorphicModel):
    field1 = models.CharField(max_length=10)
    m2m = models.ManyToManyField('self')


class ModelShow3(ShowFieldTypeAndContent, PolymorphicModel):
    field1 = models.CharField(max_length=10)
    m2m = models.ManyToManyField('self')


##


class ModelShow1_plain(PolymorphicModel):
    field1 = models.CharField(max_length=10)


class ModelShow2_plain(ModelShow1_plain):
    field2 = models.CharField(max_length=10)


##


class Base(ShowFieldType, PolymorphicModel):
    field_b = models.CharField(max_length=10)


class ModelX(Base):
    field_x = models.CharField(max_length=10)


class ModelY(Base):
    field_y = models.CharField(max_length=10)


##


class Enhance_Plain(models.Model):
    field_p = models.CharField(max_length=10)


class Enhance_Base(ShowFieldTypeAndContent, PolymorphicModel):
    field_b = models.CharField(max_length=10)


class Enhance_Inherit(Enhance_Base, Enhance_Plain):
    field_i = models.CharField(max_length=10)


##


class DiamondBase(models.Model):
    field_b = models.CharField(max_length=10)


class DiamondX(DiamondBase):
    field_x = models.CharField(max_length=10)


class DiamondY(DiamondBase):
    field_y = models.CharField(max_length=10)


class DiamondXY(DiamondX, DiamondY):
    pass


##


class RelationBase(ShowFieldTypeAndContent, PolymorphicModel):
    field_base = models.CharField(max_length=10)
    fk = models.ForeignKey('self', null=True, related_name='relationbase_set')
    m2m = models.ManyToManyField('self')


class RelationA(RelationBase):
    field_a = models.CharField(max_length=10)


class RelationB(RelationBase):
    field_b = models.CharField(max_length=10)


class RelationBC(RelationB):
    field_c = models.CharField(max_length=10)


##


class RelatingModel(models.Model):
    many2many = models.ManyToManyField(Model2A)


##


class One2OneRelatingModel(PolymorphicModel):
    one2one = models.OneToOneField(Model2A)
    field1 = models.CharField(max_length=10)


##


class One2OneRelatingModelDerived(One2OneRelatingModel):
    field2 = models.CharField(max_length=10)


##


class MyManagerQuerySet(PolymorphicQuerySet):
    def my_queryset_foo(self):
        clone = self._clone()
        return clone.all()  # Just a method to prove the existance of the custom queryset.


class MyManager(PolymorphicManager):
    queryset_class = MyManagerQuerySet

    def get_query_set(self):
        return super(MyManager, self).get_query_set().order_by('-field1')

    def my_queryset_foo(self):
        return self.get_query_set().my_queryset_foo()


class ModelWithMyManager(ShowFieldTypeAndContent, Model2A):
    objects = MyManager()
    field4 = models.CharField(max_length=10)


##


class ParentModelWithManager(PolymorphicModel):
    pass


class ChildModelWithManager(PolymorphicModel):
    # Also test whether foreign keys receive the manager:
    fk = models.ForeignKey(ParentModelWithManager, related_name='childmodel_set')
    objects = MyManager()


class PlainMyManagerQuerySet(QuerySet):
    def my_queryset_foo(self):
        return self.all()  # Just a method to prove the existance of the custom queryset.


class PlainMyManager(models.Manager):
    def my_queryset_foo(self):
        return self.get_query_set().my_queryset_foo()

    def get_query_set(self):
        return PlainMyManagerQuerySet(self.model, using=self._db)


class PlainParentModelWithManager(models.Model):
    pass


class PlainChildModelWithManager(models.Model):
    fk = models.ForeignKey(PlainParentModelWithManager, related_name='childmodel_set')
    objects = PlainMyManager()


##


class MROBase1(ShowFieldType, PolymorphicModel):
    objects = MyManager()
    field1 = models.CharField(max_length=10)  # needed as MyManager uses it


class MROBase2(MROBase1):
    pass  # Django vanilla inheritance does not inherit MyManager as _default_manager here


class MROBase3(models.Model):
    objects = PolymorphicManager()


class MRODerived(MROBase2, MROBase3):
    pass  # Should inherit _default_manager from MROBase2


##


class MROPlainBase1(ShowFieldType, models.Model):
    objects = PlainMyManager()
    field1 = models.CharField(max_length=10)  # needed as PlainMyManager uses it


class MROPlainBase2(MROPlainBase1):
    pass  # Django vanilla inheritance does not inherit PlainMyManager as _default_manager here


class MROPlainBase3(models.Model):
    objects = models.Manager()


class MROPlainDerived(MROPlainBase2, MROPlainBase3):
    pass  # ...and neither here


##


class BlogBase(ShowFieldTypeAndContent, PolymorphicModel):
    name = models.CharField(max_length=10)


class BlogA(BlogBase):
    info = models.CharField(max_length=10)


class BlogB(BlogBase):
    pass


class BlogEntry(ShowFieldTypeAndContent, PolymorphicModel):
    blog = models.ForeignKey(BlogA)
    text = models.CharField(max_length=10)


##


class BlogEntry_limit_choices_to(ShowFieldTypeAndContent, PolymorphicModel):
    blog = models.ForeignKey(BlogBase)
    text = models.CharField(max_length=10)


##


class ModelFieldNameTest(ShowFieldType, PolymorphicModel):
    modelfieldnametest = models.CharField(max_length=10)


##


class InitTestModel(ShowFieldType, PolymorphicModel):
    bar = models.CharField(max_length=100)

    def __init__(self, *args, **kwargs):
        kwargs['bar'] = self.x()
        super(InitTestModel, self).__init__(*args, **kwargs)


class InitTestModelSubclass(InitTestModel):
    def x(self):
        return 'XYZ'


##
# models from github issue

class Top(ShowFieldType, PolymorphicModel):
    name = models.CharField(max_length=50)

    class Meta:
        ordering = ('pk',)


class Middle(Top):
    description = models.TextField()


class Bottom(Middle):
    author = models.CharField(max_length=50)


##


class UUIDProject(ShowFieldTypeAndContent, PolymorphicModel):
        uuid_primary_key = UUIDField(primary_key=True)
        topic = models.CharField(max_length=30)


class UUIDArtProject(UUIDProject):
        artist = models.CharField(max_length=30)


class UUIDResearchProject(UUIDProject):
        supervisor = models.CharField(max_length=30)


##


class UUIDPlainA(models.Model):
    uuid_primary_key = UUIDField(primary_key=True)
    field1 = models.CharField(max_length=10)


class UUIDPlainB(UUIDPlainA):
    field2 = models.CharField(max_length=10)


class UUIDPlainC(UUIDPlainB):
    field3 = models.CharField(max_length=10)


##
# base -> proxy

class ProxyBase(PolymorphicModel):
    some_data = models.CharField(max_length=128)


class ProxyChild(ProxyBase):
    class Meta:
        proxy = True


##
# base -> proxy -> real models

class ProxiedBase(ShowFieldTypeAndContent, PolymorphicModel):
    name = models.CharField(max_length=10)


class ProxyModelBase(ProxiedBase):
    class Meta:
        proxy = True


class ProxyModelA(ProxyModelBase):
    field1 = models.CharField(max_length=10)


class ProxyModelB(ProxyModelBase):
    field2 = models.CharField(max_length=10)


##
# validation error: "polymorphic.relatednameclash: Accessor for field 'polymorphic_ctype' clashes
# with related field 'ContentType.relatednameclash_set'." (reported by Andrew Ingram)
# fixed with related_name

class RelatedNameClash(ShowFieldType, PolymorphicModel):
    ctype = models.ForeignKey(ContentType, null=True, editable=False)


##
# Test primary key override

class PrimaryKeyOverrideBase(PolymorphicModel):
    field1 = models.CharField(max_length=10)


class PrimaryKeyOverride(PrimaryKeyOverrideBase):
    char_primary_key = models.CharField(max_length=10, primary_key=True)
    field2 = models.CharField(max_length=10)

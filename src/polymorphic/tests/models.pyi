from _typeshed import Incomplete
from typing import Any, ClassVar
from django.contrib.auth.models import Group
from django.db import models
from django_stubs.db.models import Manager
from django_stubs.db.models.query import QuerySet
from polymorphic.managers import PolymorphicManager as PolymorphicManager
from polymorphic.models import PolymorphicModel as PolymorphicModel
from polymorphic.query import PolymorphicQuerySet as PolymorphicQuerySet
from polymorphic.showfields import (
    ShowFieldContent as ShowFieldContent,
    ShowFieldType as ShowFieldType,
    ShowFieldTypeAndContent as ShowFieldTypeAndContent,
)

class PlainA(models.Model):
    field1: Incomplete

class PlainB(PlainA):
    field2: Incomplete

class PlainC(PlainB):
    field3: Incomplete

class Model2A(ShowFieldType, PolymorphicModel):
    field1: Incomplete
    polymorphic_showfield_deferred: bool

class Model2B(Model2A):
    field2: Incomplete

class Model2C(Model2B):
    field3: Incomplete

class Model2D(Model2C):
    field4: Incomplete

class ModelExtraA(ShowFieldTypeAndContent, PolymorphicModel):
    field1: Incomplete

class ModelExtraB(ModelExtraA):
    field2: Incomplete

class ModelExtraC(ModelExtraB):
    field3: Incomplete

class ModelExtraExternal(models.Model):
    topic: Incomplete

class ModelShow1(ShowFieldType, PolymorphicModel):
    field1: Incomplete
    m2m: Incomplete

class ModelShow2(ShowFieldContent, PolymorphicModel):
    field1: Incomplete
    m2m: Incomplete

class ModelShow3(ShowFieldTypeAndContent, PolymorphicModel):
    field1: Incomplete
    m2m: Incomplete

class ModelShow1_plain(PolymorphicModel):
    field1: Incomplete

class ModelShow2_plain(ModelShow1_plain):
    field2: Incomplete

class Base(ShowFieldType, PolymorphicModel):
    polymorphic_showfield_deferred: bool
    field_b: Incomplete

class ModelX(Base):
    field_x: Incomplete

class ModelY(Base):
    field_y: Incomplete

class Enhance_Plain(models.Model):
    field_p: Incomplete
    objects: ClassVar[Any]

class Enhance_Base(ShowFieldTypeAndContent, PolymorphicModel):
    base_id: Incomplete
    field_b: Incomplete

class Enhance_Inherit(Enhance_Base, Enhance_Plain):
    field_i: Incomplete

class RelationAbstractModel(models.Model):
    class Meta:
        abstract = True

class RelationBase(RelationAbstractModel, ShowFieldTypeAndContent, PolymorphicModel):
    field_base: Incomplete
    fk: Incomplete
    m2m: Incomplete

class RelationA(RelationBase):
    field_a: Incomplete

class RelationB(RelationBase):
    field_b: Incomplete

class RelationBC(RelationB):
    field_c: Incomplete

class RelatingModel(models.Model):
    many2many: Incomplete

class One2OneRelatingModel(PolymorphicModel):
    one2one: Incomplete
    field1: Incomplete

class One2OneRelatingModelDerived(One2OneRelatingModel):
    field2: Incomplete

class ModelUnderRelParent(PolymorphicModel):
    field1: Incomplete

class ModelUnderRelChild(PolymorphicModel):
    parent: Incomplete

class MyManagerQuerySet(PolymorphicQuerySet[Any]):
    def my_queryset_foo(self): ...

class MyManager(PolymorphicManager[Any]):
    queryset_class = MyManagerQuerySet
    def get_queryset(self): ...
    def my_queryset_foo(self): ...

class ModelWithMyManager(ShowFieldTypeAndContent, Model2A):
    objects: Incomplete
    field4: Incomplete

class ModelWithMyManagerNoDefault(ShowFieldTypeAndContent, Model2A):
    objects: Incomplete
    my_objects: Incomplete
    field4: Incomplete

class ModelWithMyManagerDefault(ShowFieldTypeAndContent, Model2A):
    my_objects: Incomplete
    objects: Incomplete
    field4: Incomplete

class ModelWithMyManager2(ShowFieldTypeAndContent, Model2A):
    objects: Incomplete
    field4: Incomplete

class ModelArticle(PolymorphicModel):
    sales_points: Incomplete

class ModelPackage(ModelArticle):
    name: Incomplete

class ModelComponent(ModelArticle):
    name: Incomplete

class ModelOrderLine(models.Model):
    articles: Incomplete

class MROBase1(ShowFieldType, PolymorphicModel):
    objects: Incomplete
    field1: Incomplete

class MROBase2(MROBase1): ...

class MROBase3(models.Model):
    base_3_id: Incomplete
    objects: Incomplete

class MRODerived(MROBase2, MROBase3): ...
class ParentModelWithManager(PolymorphicModel): ...

class ChildModelWithManager(PolymorphicModel):
    field1: Incomplete
    fk: Incomplete
    objects: Incomplete

class PlainMyManagerQuerySet(QuerySet[Any]):
    def my_queryset_foo(self): ...

class PlainMyManager(models.Manager[Any]):
    def my_queryset_foo(self): ...
    def get_queryset(self): ...

class PlainParentModelWithManager(models.Model): ...

class PlainChildModelWithManager(models.Model):
    fk: Incomplete
    objects: Incomplete

class BlogBase(ShowFieldTypeAndContent, PolymorphicModel):
    name: Incomplete

class BlogA(BlogBase):
    info: Incomplete

class BlogB(BlogBase): ...

class BlogEntry(ShowFieldTypeAndContent, PolymorphicModel):
    blog: Incomplete
    text: Incomplete

class BlogEntry_limit_choices_to(ShowFieldTypeAndContent, PolymorphicModel):
    blog: Incomplete
    text: Incomplete

class ModelFieldNameTest(ShowFieldType, PolymorphicModel):
    modelfieldnametest: Incomplete

class InitTestModel(ShowFieldType, PolymorphicModel):
    bar: Incomplete
    def __init__(self, *args, **kwargs) -> None: ...

class InitTestModelSubclass(InitTestModel):
    def x(self): ...

class Top(PolymorphicModel):
    name: Incomplete

class Middle(Top):
    description: Incomplete

class Bottom(Middle):
    author: Incomplete

class UUIDProject(ShowFieldTypeAndContent, PolymorphicModel):
    uuid_primary_key: Incomplete
    topic: Incomplete

class UUIDArtProject(UUIDProject):
    artist: Incomplete

class UUIDResearchProject(UUIDProject):
    supervisor: Incomplete

class UUIDArtProjectA(UUIDArtProject): ...
class UUIDArtProjectB(UUIDArtProjectA): ...
class UUIDArtProjectC(UUIDArtProjectB): ...
class UUIDArtProjectD(UUIDArtProjectC): ...

class UUIDPlainA(models.Model):
    uuid_primary_key: Incomplete
    field1: Incomplete

class UUIDPlainB(UUIDPlainA):
    field2: Incomplete

class UUIDPlainC(UUIDPlainB):
    field3: Incomplete

class ProxyBase(PolymorphicModel):
    some_data: Incomplete

class ProxyChild(ProxyBase):
    class Meta:
        proxy = True

class NonProxyChild(ProxyBase):
    name: Incomplete

class ProxiedBase(ShowFieldTypeAndContent, PolymorphicModel):
    name: Incomplete

class ProxyModelBase(ProxiedBase):
    class Meta:
        proxy = True

class ProxyModelA(ProxyModelBase):
    field1: Incomplete

class ProxyModelB(ProxyModelBase):
    field2: Incomplete

class RelatedNameClash(ShowFieldType, PolymorphicModel):
    ctype: Incomplete

class ParentLinkAndRelatedName(ModelShow1_plain):
    superclass: Incomplete

class CustomPkBase(ShowFieldTypeAndContent, PolymorphicModel):
    b: Incomplete

class CustomPkInherit(CustomPkBase):
    custom_id: Incomplete
    i: Incomplete

class DateModel(PolymorphicModel):
    date: Incomplete

class AbstractModel(PolymorphicModel):
    class Meta:
        abstract = True

class SwappableModel(AbstractModel):
    class Meta:
        swappable: str

class SwappedModel(AbstractModel): ...

class InlineParent(models.Model):
    title: Incomplete

class InlineModelA(PolymorphicModel):
    parent: Incomplete
    field1: Incomplete

class InlineModelB(InlineModelA):
    field2: Incomplete
    plain_a: Incomplete

class AbstractProject(PolymorphicModel):
    topic: Incomplete
    class Meta:
        abstract = True

class ArtProject(AbstractProject):
    artist: Incomplete

class Duck(PolymorphicModel):
    name: Incomplete

class RedheadDuck(Duck):
    class Meta:
        proxy = True

class RubberDuck(Duck):
    class Meta:
        proxy = True

class MultiTableBase(PolymorphicModel):
    field1: Incomplete

class MultiTableDerived(MultiTableBase):
    field2: Incomplete

class SubclassSelectorAbstractBaseModel(PolymorphicModel):
    base_field: Incomplete

class SubclassSelectorAbstractModel(SubclassSelectorAbstractBaseModel):
    abstract_field: Incomplete
    class Meta:
        abstract = True

class SubclassSelectorAbstractConcreteModel(SubclassSelectorAbstractModel):
    concrete_field: Incomplete

class SubclassSelectorProxyBaseModel(PolymorphicModel):
    base_field: Incomplete

class SubclassSelectorProxyModel(SubclassSelectorProxyBaseModel):
    class Meta:
        proxy = True

class SubclassSelectorProxyConcreteModel(SubclassSelectorProxyModel):
    concrete_field: Incomplete

class NonPolymorphicParent(PolymorphicModel, Group):
    test: Incomplete
    objects: Manager[Any]

class Participant(PolymorphicModel): ...

class UserProfile(Participant):
    name: Incomplete

class Team(models.Model):
    team_name: Incomplete
    user_profiles: Incomplete

class BlueHeadDuck(Duck):
    color: str
    def __init__(self, *args, **kwargs) -> None: ...

class HomeDuck(models.Model):
    home: str
    def __init__(self, *args, **kwargs) -> None: ...
    class Meta:
        abstract = True

class PurpleHeadDuck(HomeDuck, BlueHeadDuck):
    class Meta:
        proxy = True

class Account(PolymorphicModel):
    user: Incomplete

class SpecialAccount1(Account):
    extra1: Incomplete

class SpecialAccount1_1(SpecialAccount1):
    extra2: Incomplete

class SpecialAccount2(Account):
    extra1: Incomplete

class ModelMixin(models.Model):
    class Meta:
        abstract = True

    created_at: Incomplete
    modified_at: Incomplete

class PolymorphicMixin(PolymorphicModel):
    class Meta:
        abstract = True

    created_at: Incomplete
    modified_at: Incomplete

class Foo(PolymorphicModel): ...
class Bar(PolymorphicMixin, PolymorphicModel): ...
class Baz(ModelMixin, PolymorphicModel): ...

class MyBaseQuerySet(PolymorphicQuerySet[Any]):
    def filter_by_user(self, _): ...

class MyBaseModel(PolymorphicModel):
    objects: Incomplete

class MyChild1QuerySet(MyBaseQuerySet):
    def filter_by_user(self, num): ...

class MyChild1Model(MyBaseModel):
    fieldA: Incomplete
    objects: Incomplete

class MyChild2QuerySet(MyBaseQuerySet):
    def filter_by_user(self, num): ...

class MyChild2Model(MyBaseModel):
    fieldB: Incomplete
    objects: Incomplete
    base_manager: Incomplete

class SpecialQuerySet(PolymorphicQuerySet[Any]):
    def has_text(self, text): ...

class SpecialPolymorphicManager(Incomplete):
    def custom_queryset(self): ...

class AbstractManagerTest(PolymorphicModel):
    objects: Incomplete
    basic_manager: Incomplete
    default_manager: Incomplete
    abstract_field: Incomplete
    class Meta:
        abstract = True

class RelatedManagerTest(models.Model): ...

class DerivedManagerTest(AbstractManagerTest):
    related_test: Incomplete

class DerivedManagerTest2(DerivedManagerTest):
    objects: Incomplete

class FKTestBase(PolymorphicModel): ...
class FKTestChild(Base): ...

class FKTest(models.Model):
    fk: Incomplete

class NoChildren(PolymorphicModel):
    field1: Incomplete

class NormalBase(models.Model):
    nb_field: Incomplete
    objects: ClassVar[Any]

class NormalExtension(NormalBase):
    ne_field: Incomplete

class PolyExtension(PolymorphicModel, NormalExtension):
    poly_ext_field: Incomplete

class PolyExtChild(PolyExtension):
    poly_child_field: Incomplete

class DeepCopyTester(PolymorphicModel):
    binary_field: Incomplete

class DeepCopyTester2(DeepCopyTester):
    binary_field2: Incomplete

class DucksLake(models.Model):
    lake: Incomplete
    duck: Incomplete
    time: Incomplete

class Lake(models.Model):
    ducks: Incomplete

class LakeWithThrough(models.Model):
    ducks: Incomplete

class ChoiceBlank(PolymorphicModel): ...

class ChoiceAthlete(ChoiceBlank):
    choice: Incomplete

class BetMultiple(models.Model):
    answer: Incomplete

class RankedAthlete(models.Model):
    choiceAthlete: Incomplete
    bet: Incomplete
    rank: Incomplete

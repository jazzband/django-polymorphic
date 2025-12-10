import uuid

import django
from django.contrib.auth.models import Group
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.db.models.query import QuerySet

from polymorphic.managers import PolymorphicManager
from polymorphic.models import PolymorphicModel
from polymorphic.query import PolymorphicQuerySet
from polymorphic.showfields import ShowFieldContent, ShowFieldType, ShowFieldTypeAndContent


class PlainA(models.Model):
    field1 = models.CharField(max_length=30)

    def __str__(self):
        return self.field1


class PlainB(PlainA):
    field2 = models.CharField(max_length=30)


class PlainC(PlainB):
    field3 = models.CharField(max_length=30)


class Model2A(ShowFieldType, PolymorphicModel):
    field1 = models.CharField(max_length=30)
    polymorphic_showfield_deferred = True


class Model2B(Model2A):
    field2 = models.CharField(max_length=30)


class Model2C(Model2B):
    field3 = models.CharField(max_length=30)


class Model2D(Model2C):
    field4 = models.CharField(max_length=30)


class ModelExtraA(ShowFieldTypeAndContent, PolymorphicModel):
    field1 = models.CharField(max_length=30)


class ModelExtraB(ModelExtraA):
    field2 = models.CharField(max_length=30)


class ModelExtraC(ModelExtraB):
    field3 = models.CharField(max_length=30)


class ModelExtraExternal(models.Model):
    topic = models.CharField(max_length=30)


class ModelShow1(ShowFieldType, PolymorphicModel):
    field1 = models.CharField(max_length=30)
    m2m = models.ManyToManyField("self")


class ModelShow2(ShowFieldContent, PolymorphicModel):
    field1 = models.CharField(max_length=30)
    m2m = models.ManyToManyField("self")


class ModelShow3(ShowFieldTypeAndContent, PolymorphicModel):
    field1 = models.CharField(max_length=30)
    m2m = models.ManyToManyField("self")


class ModelShow1_plain(PolymorphicModel):
    field1 = models.CharField(max_length=30)


class ModelShow2_plain(ModelShow1_plain):
    field2 = models.CharField(max_length=30)


class Base(ShowFieldType, PolymorphicModel):
    polymorphic_showfield_deferred = True
    field_b = models.CharField(max_length=30)


class ModelX(Base):
    field_x = models.CharField(max_length=30)


class ModelY(Base):
    field_y = models.CharField(max_length=30)


class Enhance_Plain(models.Model):
    field_p = models.CharField(max_length=30)


class Enhance_Base(ShowFieldTypeAndContent, PolymorphicModel):
    base_id = models.AutoField(primary_key=True)
    field_b = models.CharField(max_length=30)


class Enhance_Inherit(Enhance_Base, Enhance_Plain):
    field_i = models.CharField(max_length=30)


class RelationAbstractModel(models.Model):
    class Meta:
        abstract = True


class RelationBase(RelationAbstractModel, ShowFieldTypeAndContent, PolymorphicModel):
    field_base = models.CharField(max_length=30)
    fk = models.ForeignKey(
        "self", on_delete=models.CASCADE, null=True, related_name="relationbase_set"
    )
    m2m = models.ManyToManyField("self")


class RelationA(RelationBase):
    field_a = models.CharField(max_length=30)


class RelationB(RelationBase):
    field_b = models.CharField(max_length=30)


class RelationBC(RelationB):
    field_c = models.CharField(max_length=30)


class RelatingModel(models.Model):
    many2many = models.ManyToManyField(Model2A)


class One2OneRelatingModel(PolymorphicModel):
    one2one = models.OneToOneField(Model2A, on_delete=models.CASCADE)
    field1 = models.CharField(max_length=30)


class One2OneRelatingModelDerived(One2OneRelatingModel):
    field2 = models.CharField(max_length=30)


class ModelUnderRelParent(PolymorphicModel):
    field1 = models.CharField(max_length=30)
    _private = models.CharField(max_length=30)


class ModelUnderRelChild(PolymorphicModel):
    parent = models.ForeignKey(
        ModelUnderRelParent, on_delete=models.CASCADE, related_name="children"
    )
    _private2 = models.CharField(max_length=30)


class MyManagerQuerySet(PolymorphicQuerySet):
    def my_queryset_foo(self):
        # Just a method to prove the existence of the custom queryset.
        return self.all()


class MyManager(PolymorphicManager):
    queryset_class = MyManagerQuerySet

    def get_queryset(self):
        return super().get_queryset().order_by("-field1")

    def my_queryset_foo(self):
        return self.all().my_queryset_foo()


class ModelWithMyManager(ShowFieldTypeAndContent, Model2A):
    objects = MyManager()
    field4 = models.CharField(max_length=30)


class ModelWithMyManagerNoDefault(ShowFieldTypeAndContent, Model2A):
    objects = PolymorphicManager()
    my_objects = MyManager()
    field4 = models.CharField(max_length=30)


class ModelWithMyManagerDefault(ShowFieldTypeAndContent, Model2A):
    my_objects = MyManager()
    objects = PolymorphicManager()
    field4 = models.CharField(max_length=30)


class ModelWithMyManager2(ShowFieldTypeAndContent, Model2A):
    objects = MyManagerQuerySet.as_manager()
    field4 = models.CharField(max_length=30)


class ModelArticle(PolymorphicModel):
    sales_points = models.IntegerField()


class ModelPackage(ModelArticle):
    name = models.CharField(max_length=300)


class ModelComponent(ModelArticle):
    name = models.CharField(max_length=300)


class ModelOrderLine(models.Model):
    articles = models.ManyToManyField(ModelArticle, related_name="orderline")


class MROBase1(ShowFieldType, PolymorphicModel):
    objects = MyManager()
    field1 = models.CharField(max_length=30)  # needed as MyManager uses it


class MROBase2(MROBase1):
    pass
    # No manager_inheritance_from_future or Meta set. test that polymorphic restores that.


class MROBase3(models.Model):
    # make sure 'id' field doesn't clash, detected by Django 1.11
    base_3_id = models.AutoField(primary_key=True)
    objects = models.Manager()


class MRODerived(MROBase2, MROBase3):
    pass


class ParentModelWithManager(PolymorphicModel):
    pass


class ChildModelWithManager(PolymorphicModel):
    # Also test whether foreign keys receive the manager:
    field1 = models.CharField(max_length=30)  # needed as MyManager uses it
    fk = models.ForeignKey(
        ParentModelWithManager, on_delete=models.CASCADE, related_name="childmodel_set"
    )
    objects = MyManager()


class PlainMyManagerQuerySet(QuerySet):
    def my_queryset_foo(self):
        # Just a method to prove the existence of the custom queryset.
        return self.all()


class PlainMyManager(models.Manager):
    def my_queryset_foo(self):
        return self.get_queryset().my_queryset_foo()

    def get_queryset(self):
        return PlainMyManagerQuerySet(self.model, using=self._db)


class PlainParentModelWithManager(models.Model):
    pass


class PlainChildModelWithManager(models.Model):
    fk = models.ForeignKey(
        PlainParentModelWithManager,
        on_delete=models.CASCADE,
        related_name="childmodel_set",
    )
    objects = PlainMyManager()


class BlogBase(ShowFieldTypeAndContent, PolymorphicModel):
    name = models.CharField(max_length=30)


class BlogA(BlogBase):
    info = models.CharField(max_length=30)


class BlogB(BlogBase):
    pass


class BlogEntry(ShowFieldTypeAndContent, PolymorphicModel):
    blog = models.ForeignKey(BlogA, on_delete=models.CASCADE)
    text = models.CharField(max_length=30)


class BlogEntry_limit_choices_to(ShowFieldTypeAndContent, PolymorphicModel):
    blog = models.ForeignKey(BlogBase, on_delete=models.CASCADE)
    text = models.CharField(max_length=30)


class ModelFieldNameTest(ShowFieldType, PolymorphicModel):
    modelfieldnametest = models.CharField(max_length=30)


class InitTestModel(ShowFieldType, PolymorphicModel):
    bar = models.CharField(max_length=300)

    def __init__(self, *args, **kwargs):
        kwargs["bar"] = self.x()
        super().__init__(*args, **kwargs)


class InitTestModelSubclass(InitTestModel):
    def x(self):
        return "XYZ"


# models from github issue


class Top(PolymorphicModel):
    name = models.CharField(max_length=50)


class Middle(Top):
    description = models.TextField()


class Bottom(Middle):
    author = models.CharField(max_length=50)


class UUIDProject(ShowFieldTypeAndContent, PolymorphicModel):
    uuid_primary_key = models.UUIDField(primary_key=True, default=uuid.uuid1)
    topic = models.CharField(max_length=30)


class UUIDArtProject(UUIDProject):
    artist = models.CharField(max_length=30)


class UUIDResearchProject(UUIDProject):
    supervisor = models.CharField(max_length=30)


class UUIDPlainA(models.Model):
    uuid_primary_key = models.UUIDField(primary_key=True, default=uuid.uuid1)
    field1 = models.CharField(max_length=30)


class UUIDPlainB(UUIDPlainA):
    field2 = models.CharField(max_length=30)


class UUIDPlainC(UUIDPlainB):
    field3 = models.CharField(max_length=30)


# base -> proxy


class ProxyBase(PolymorphicModel):
    some_data = models.CharField(max_length=128)


class ProxyChild(ProxyBase):
    class Meta:
        proxy = True


class NonProxyChild(ProxyBase):
    name = models.CharField(max_length=30)


# base -> proxy -> real models


class ProxiedBase(ShowFieldTypeAndContent, PolymorphicModel):
    name = models.CharField(max_length=30)


class ProxyModelBase(ProxiedBase):
    class Meta:
        proxy = True


class ProxyModelA(ProxyModelBase):
    field1 = models.CharField(max_length=30)


class ProxyModelB(ProxyModelBase):
    field2 = models.CharField(max_length=30)


# test bad field name
# class TestBadFieldModel(ShowFieldType, PolymorphicModel):
#    instance_of = models.CharField(max_length=30)


# validation error: "polymorphic.relatednameclash: Accessor for field 'polymorphic_ctype' clashes
# with related field 'ContentType.relatednameclash_set'." (reported by Andrew Ingram)
# fixed with related_name
class RelatedNameClash(ShowFieldType, PolymorphicModel):
    ctype = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True, editable=False)


# class with a parent_link to superclass, and a related_name back to subclass


class ParentLinkAndRelatedName(ModelShow1_plain):
    superclass = models.OneToOneField(
        ModelShow1_plain,
        on_delete=models.CASCADE,
        parent_link=True,
        related_name="related_name_subclass",
    )


class CustomPkBase(ShowFieldTypeAndContent, PolymorphicModel):
    b = models.CharField(max_length=1)


class CustomPkInherit(CustomPkBase):
    custom_id = models.AutoField(primary_key=True)
    i = models.CharField(max_length=1)


class DateModel(PolymorphicModel):
    date = models.DateTimeField()


# Define abstract and swappable (being swapped for SwappedModel) models
# To test manager validation (should be skipped for such models)
class AbstractModel(PolymorphicModel):
    class Meta:
        abstract = True


class SwappableModel(AbstractModel):
    class Meta:
        swappable = "POLYMORPHIC_TEST_SWAPPABLE"


class SwappedModel(AbstractModel):
    pass


class InlineParent(models.Model):
    title = models.CharField(max_length=30)


class InlineModelA(PolymorphicModel):
    parent = models.ForeignKey(
        InlineParent, related_name="inline_children", on_delete=models.CASCADE
    )
    field1 = models.CharField(max_length=30)


class InlineModelB(InlineModelA):
    field2 = models.CharField(max_length=30)

    plain_a = models.ForeignKey(
        PlainA,
        null=True,
        blank=True,
        default=None,
        on_delete=models.SET_NULL,
        related_name="inline_bs",
    )


class AbstractProject(PolymorphicModel):
    topic = models.CharField(max_length=30)

    class Meta:
        abstract = True


class ArtProject(AbstractProject):
    artist = models.CharField(max_length=30)


class Duck(PolymorphicModel):
    name = models.CharField(max_length=30)


class RedheadDuck(Duck):
    class Meta:
        proxy = True


class RubberDuck(Duck):
    class Meta:
        proxy = True


class MultiTableBase(PolymorphicModel):
    field1 = models.CharField(max_length=30)


class MultiTableDerived(MultiTableBase):
    field2 = models.CharField(max_length=30)


class SubclassSelectorAbstractBaseModel(PolymorphicModel):
    base_field = models.CharField(max_length=30, default="test_bf")


class SubclassSelectorAbstractModel(SubclassSelectorAbstractBaseModel):
    abstract_field = models.CharField(max_length=30, default="test_af")

    class Meta:
        abstract = True


class SubclassSelectorAbstractConcreteModel(SubclassSelectorAbstractModel):
    concrete_field = models.CharField(max_length=30, default="test_cf")


class SubclassSelectorProxyBaseModel(PolymorphicModel):
    base_field = models.CharField(max_length=30, default="test_bf")


class SubclassSelectorProxyModel(SubclassSelectorProxyBaseModel):
    class Meta:
        proxy = True


class SubclassSelectorProxyConcreteModel(SubclassSelectorProxyModel):
    concrete_field = models.CharField(max_length=30, default="test_cf")


class NonPolymorphicParent(PolymorphicModel, Group):
    test = models.CharField(max_length=30, default="test_non_polymorphic_parent")


class Participant(PolymorphicModel):
    pass


class UserProfile(Participant):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Team(models.Model):
    team_name = models.CharField(max_length=100)
    user_profiles = models.ManyToManyField(UserProfile, related_name="user_teams")


class BlueHeadDuck(Duck):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.color = "blue"


class HomeDuck(models.Model):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.home = "Duckburg"

    class Meta:
        abstract = True


class PurpleHeadDuck(HomeDuck, BlueHeadDuck):
    class Meta:
        proxy = True


class Account(PolymorphicModel):
    user = models.OneToOneField(
        get_user_model(), primary_key=True, on_delete=models.CASCADE, related_name="account"
    )


class SpecialAccount1(Account):
    extra1 = models.IntegerField(null=True, default=None, blank=True)


class SpecialAccount1_1(SpecialAccount1):
    extra2 = models.IntegerField(null=True, default=None, blank=True)


class SpecialAccount2(Account):
    extra1 = models.CharField(default="", blank=True, max_length=30)


class ModelMixin(models.Model):
    class Meta:
        abstract = True

    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)


class PolymorphicMixin(PolymorphicModel):
    class Meta:
        abstract = True

    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)


class Foo(PolymorphicModel):
    pass


class Bar(PolymorphicMixin, PolymorphicModel):
    pass


class Baz(ModelMixin, PolymorphicModel):
    pass


class MyBaseQuerySet(PolymorphicQuerySet):
    def filter_by_user(self, _):
        return self.all()


class MyBaseModel(PolymorphicModel):
    ...
    objects = MyBaseQuerySet.as_manager()


class MyChild1QuerySet(MyBaseQuerySet):
    def filter_by_user(self, num):
        return self.filter(fieldA__lt=num)


class MyChild1Model(MyBaseModel):
    fieldA = models.IntegerField()
    ...
    objects = MyChild1QuerySet.as_manager()


class MyChild2QuerySet(MyBaseQuerySet):
    def filter_by_user(self, num):
        return self.filter(fieldB__gt=num)


class MyChild2Model(MyBaseModel):
    fieldB = models.IntegerField()
    ...
    objects = PolymorphicManager.from_queryset(MyChild2QuerySet)()
    base_manager = MyBaseQuerySet.as_manager()

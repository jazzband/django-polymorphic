import uuid

from django.contrib.auth.models import Group
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.db.models import Manager
from django.db import models
from django.db.models.query import QuerySet
from django.db.models import F
from django.db.models.functions import Upper
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation

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


class PlainD(PlainA):
    field2 = models.CharField(max_length=30)


class Model2A(ShowFieldType, PolymorphicModel):
    field1 = models.CharField(max_length=30)
    polymorphic_showfield_deferred = True


class RandomMixinB:
    def random_method(self):
        return "random b"


class Model2B(RandomMixinB, Model2A):
    field2 = models.CharField(max_length=30)


class RandomMixinC:
    def random_method(self):
        return "random c"


class Model2C(RandomMixinC, Model2B):
    field3 = models.CharField(max_length=30, blank=True, default="")


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


class UUIDArtProjectA(UUIDArtProject): ...


class UUIDArtProjectB(UUIDArtProjectA): ...


class UUIDArtProjectC(UUIDArtProjectB): ...


class UUIDArtProjectD(UUIDArtProjectC): ...


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

    # File field for testing multipart encoding in polymorphic inlines (issue #380)
    file_upload = models.FileField(upload_to="test_uploads/", null=True, blank=True, default=None)


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


class SpecialQuerySet(PolymorphicQuerySet):
    def has_text(self, text):
        return self.filter(abstract_field__icontains=text)


class SpecialPolymorphicManager(PolymorphicManager.from_queryset(SpecialQuerySet)):
    def custom_queryset(self):
        return self.get_queryset()


class AbstractManagerTest(PolymorphicModel):
    """
    Tests that custom manager patterns work on abstract base models
    """

    objects = SpecialPolymorphicManager()
    basic_manager = Manager()
    default_manager = PolymorphicManager()

    abstract_field = models.CharField(max_length=32)

    class Meta:
        abstract = True


class RelatedManagerTest(models.Model): ...


class DerivedManagerTest(AbstractManagerTest):
    related_test = models.ForeignKey(
        RelatedManagerTest,
        on_delete=models.CASCADE,
        default=None,
        null=True,
        related_name="derived",
    )


class DerivedManagerTest2(DerivedManagerTest):
    objects = PolymorphicManager()


class FKTestBase(PolymorphicModel): ...


class FKTestChild(Base): ...


class FKTest(models.Model):
    fk = models.ForeignKey(Base, null=True, on_delete=models.SET_NULL)


class NoChildren(PolymorphicModel):
    field1 = models.CharField(max_length=12)


class ModelWithPolyFK(models.Model):
    """Model with FK to polymorphic model for popup testing."""

    name = models.CharField(max_length=100)
    poly_fk = models.ForeignKey(Model2A, on_delete=models.CASCADE, null=True, blank=True)


class NormalBase(models.Model):
    nb_field = models.IntegerField()

    def add_to_nb(self, value):
        self.nb_field += value
        self.save(update_fields=["nb_field"])


class NormalExtension(NormalBase):
    ne_field = models.CharField(max_length=50)

    def add_to_ne(self, value):
        self.ne_field += value
        self.save(update_fields=["ne_field"])


class PolyExtension(PolymorphicModel, NormalExtension):
    poly_ext_field = models.IntegerField()

    def add_to_ext(self, value):
        self.poly_ext_field += value
        self.save(update_fields=["poly_ext_field"])


class PolyExtChild(PolyExtension):
    poly_child_field = models.CharField(max_length=50)

    def add_to_child(self, value):
        self.poly_child_field += value
        self.save(update_fields=["poly_child_field"])

    def override_add_to_ne(self, value):
        # test that we can still access NormalExtension methods
        self.ne_field += value.upper()
        self.save(update_fields=["ne_field"])

    def override_add_to_ext(self, value):
        # test that we can still access PolyExtension methods
        self.poly_ext_field += value * 2
        self.save(update_fields=["poly_ext_field"])


class DeepCopyTester(PolymorphicModel):
    binary_field = models.BinaryField()


class DeepCopyTester2(DeepCopyTester):
    binary_field2 = models.BinaryField()


class DucksLake(models.Model):
    lake = models.ForeignKey("LakeWithThrough", on_delete=models.CASCADE)
    duck = models.ForeignKey(Duck, on_delete=models.CASCADE)
    time = models.CharField(max_length=10)


class Lake(models.Model):
    ducks = models.ManyToManyField(Duck)


class LakeWithThrough(models.Model):
    ducks = models.ManyToManyField(Duck, through=DucksLake)


class ChoiceBlank(PolymorphicModel):
    pass


class ChoiceAthlete(ChoiceBlank):
    choice = models.CharField(max_length=100)


class BetMultiple(models.Model):
    answer = models.ManyToManyField("ChoiceBlank", blank=True, through="RankedAthlete")


class RankedAthlete(models.Model):
    choiceAthlete = models.ForeignKey("ChoiceBlank", on_delete=models.CASCADE)
    bet = models.ForeignKey("BetMultiple", on_delete=models.CASCADE)
    rank = models.IntegerField()


class RecursionBug(PolymorphicModel):
    status = models.ForeignKey(PlainA, on_delete=models.CASCADE, related_name="recursions")

    def __init__(self, *args, **kwargs):
        """
        https://github.com/jazzband/django-polymorphic/issues/334
        """
        super().__init__(*args, **kwargs)
        self.old_status_id = self.status_id


class TaggedItem(models.Model):
    tag = models.SlugField()
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey("content_type", "object_id")


class BookmarkManager(PolymorphicManager):
    def get_queryset(self) -> PolymorphicQuerySet:
        return super().get_queryset().annotate(cpy=models.F("url"))


class Bookmark(PolymorphicModel):
    url = models.URLField()
    tags = GenericRelation(TaggedItem)
    objects = BookmarkManager()


class Assignment(Bookmark):
    assigned_to = models.CharField(max_length=100)


class Regression295Related(models.Model):
    _real_field = models.CharField(max_length=10)


class Regression295Parent(PolymorphicModel):
    related_object = models.ForeignKey(Regression295Related, on_delete=models.CASCADE)


class RelatedKeyModel(models.Model):
    custom_id = models.UUIDField(primary_key=True, default=uuid.uuid4)


class DisparateKeysParent(PolymorphicModel):
    text = models.CharField(max_length=30)


class DisparateKeysChild1(DisparateKeysParent):
    key = models.OneToOneField(RelatedKeyModel, primary_key=True, on_delete=models.CASCADE)

    text_child1 = models.CharField(max_length=30)


class DisparateKeysChild2(DisparateKeysParent):
    text_child2 = models.CharField(max_length=30)
    key = models.PositiveIntegerField(primary_key=True)


class DisparateKeysGrandChild2(DisparateKeysChild2):
    text_grand_child = models.CharField(max_length=30)


class DisparateKeysGrandChild(DisparateKeysChild1):
    text_grand_child = models.CharField(max_length=30)


class M2MAdminTest(PolymorphicModel):
    name = models.CharField(max_length=30)

    def __str__(self):
        return self.name


class M2MAdminTestChildA(M2MAdminTest):
    child_bs = models.ManyToManyField("M2MAdminTestChildB", related_name="related_as", blank=True)


class M2MAdminTestChildB(M2MAdminTest):
    child_as = models.ManyToManyField("M2MAdminTestChildA", related_name="related_bs", blank=True)


class M2MAdminTestChildC(M2MAdminTestChildB):
    pass


# Models for testing Issue #182 and #375: M2M with through tables to/from polymorphic models
class M2MThroughBase(PolymorphicModel):
    """Base polymorphic model for M2M through table tests."""

    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class M2MThroughPerson(M2MThroughBase):
    """Polymorphic child representing a person who can be on teams."""

    email = models.EmailField(blank=True)


class M2MThroughSpecialPerson(M2MThroughPerson):
    """Polymorphic child representing a special person."""

    special_code = models.CharField(max_length=20, blank=True)


class M2MThroughProject(M2MThroughBase):
    """Polymorphic child representing a project."""

    description = models.TextField(blank=True)


class M2MThroughProjectWithTeam(M2MThroughProject):
    """
    Polymorphic child with M2M to Person through Membership.
    Tests Issue #375: M2M with through table on polymorphic model.
    """

    pass


class M2MThroughMembership(PolymorphicModel):
    """Polymorphic through model for M2M relationship between ProjectWithTeam and Person."""

    project = models.ForeignKey("M2MThroughProjectWithTeam", on_delete=models.CASCADE)
    person = models.ForeignKey(M2MThroughPerson, on_delete=models.CASCADE)
    role = models.CharField(max_length=50)
    joined_date = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.person.name} - {self.role} on {self.project.name}"


class M2MThroughMembershipWithPerson(M2MThroughMembership):
    """Membership for regular Person instances."""

    pass


class M2MThroughMembershipWithSpecialPerson(M2MThroughMembership):
    """Membership for SpecialPerson instances with additional tracking."""

    special_notes = models.TextField(blank=True, default="")


# Add the M2M field after the through model is defined
M2MThroughProjectWithTeam.add_to_class(
    "team",
    models.ManyToManyField(
        M2MThroughPerson, through=M2MThroughMembership, related_name="projects", blank=True
    ),
)


# Additional models for Issue #182: Direct M2M to polymorphic model
class DirectM2MContainer(models.Model):
    """Non-polymorphic model with direct M2M to polymorphic model."""

    name = models.CharField(max_length=50)
    items = models.ManyToManyField(M2MThroughBase, related_name="containers", blank=True)

    def __str__(self):
        return self.name


class Author(models.Model):
    pass


class Book(PolymorphicModel):
    author = models.ForeignKey(Author, on_delete=models.CASCADE)


class SpecialBook(Book):
    pass


class FilteredManager(PolymorphicManager):
    def get_queryset(self):
        return super().get_queryset().exclude(field2=Upper(F("field2")))


class Model2BFiltered(Model2B):
    objects = FilteredManager()


class Model2CFiltered(Model2BFiltered):
    field3 = models.CharField(max_length=30, blank=True, default="")


class CustomBaseManager(PolymorphicManager):
    pass


class FilteredManager2(FilteredManager):
    pass


class Model2CNamedManagers(Model2CFiltered):
    all_objects = CustomBaseManager()
    filtered_objects = FilteredManager2()

    class Meta:
        base_manager_name = "all_objects"
        default_manager_name = "filtered_objects"


class Model2CNamedDefault(Model2CFiltered):
    custom_objects = FilteredManager2()

    class Meta:
        default_manager_name = "custom_objects"


# serialization natural key tests #517
class NatKeyManager(PolymorphicManager):
    def get_by_natural_key(self, slug):
        return self.get(slug=slug)


class NatKeyParent(PolymorphicModel):
    slug = models.SlugField(unique=True)
    content = models.CharField(blank=True, max_length=100)

    objects = NatKeyManager()

    def natural_key(self):
        return (self.slug,)


class NatKeyChild(NatKeyParent):
    foo = models.OneToOneField(NatKeyParent, models.CASCADE, parent_link=True, primary_key=True)
    val = models.IntegerField(default=0)

    def natural_key(self):
        return self.foo.natural_key()

    natural_key.dependencies = ["tests.natkeyparent"]


class ManagerTest(PolymorphicModel):
    name = models.CharField(max_length=30)

    objects = CustomBaseManager()

    class Meta:
        base_manager_name = "objects"


class ManagerTestChild(ManagerTest):
    pass


class PlainManager(models.Manager): ...


class ManagerTestPlain(models.Model):
    objects = PlainManager()

    class Meta:
        base_manager_name = "objects"


class ManagerTestChildPlain(ManagerTestPlain):
    pass


class TriggerRecursionQuerySet(PolymorphicQuerySet):
    def only(self, *fields):
        fields = set(fields)
        fields.update(["field1", "field2"])
        return super().only(*fields)


class TriggerRecursionManager(PolymorphicManager):
    queryset_class = TriggerRecursionQuerySet

    def only(self, *fields):
        fields = set(fields)
        fields.update(["field1", "field2"])
        return super().only(*fields)


class TriggerRecursion(PolymorphicModel):
    field1 = models.IntegerField(blank=True, null=True)
    field2 = models.IntegerField(blank=True, null=True)

    objects = TriggerRecursionManager()
    base_manager = PolymorphicManager()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Accessing field values in __init__ should not trigger recursion
        _ = self.field1
        _ = self.field2


class PlainRecursion(models.Model):
    field1 = models.IntegerField(blank=True, null=True)
    field2 = models.IntegerField(blank=True, null=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        _ = self.field1
        _ = self.field2

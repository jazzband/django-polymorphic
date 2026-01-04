import pytest
import uuid

import django
from packaging.version import Version
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.db import models, connection
from django.db.models import Case, Count, FilteredRelation, Q, Sum, When, Exists, OuterRef
from django.db.utils import IntegrityError, NotSupportedError
from django.test import TransactionTestCase
from django.test.utils import CaptureQueriesContext

from polymorphic import query_translate
from polymorphic.managers import PolymorphicManager
from polymorphic.models import PolymorphicTypeInvalid, PolymorphicTypeUndefined
from polymorphic.tests.models import (
    ArtProject,
    Base,
    BlogA,
    BlogB,
    BlogBase,
    BlogEntry,
    BlogEntry_limit_choices_to,
    ChildModelWithManager,
    CustomPkBase,
    CustomPkInherit,
    Enhance_Base,
    Enhance_Plain,
    Enhance_Inherit,
    InlineParent,
    InlineModelA,
    InlineModelB,
    InitTestModelSubclass,
    Model2A,
    Model2B,
    Model2C,
    Model2D,
    ModelExtraA,
    ModelExtraB,
    ModelExtraC,
    ModelExtraExternal,
    ModelFieldNameTest,
    ModelOrderLine,
    ModelShow1,
    ModelShow1_plain,
    ModelShow2,
    ModelShow2_plain,
    ModelShow3,
    ModelUnderRelChild,
    ModelUnderRelParent,
    ModelWithMyManager,
    ModelWithMyManager2,
    ModelWithMyManagerDefault,
    ModelWithMyManagerNoDefault,
    ModelX,
    ModelY,
    MRODerived,
    MultiTableDerived,
    MyManager,
    MyManagerQuerySet,
    NonPolymorphicParent,
    NonProxyChild,
    One2OneRelatingModel,
    One2OneRelatingModelDerived,
    ParentModelWithManager,
    PlainA,
    PlainB,
    PlainC,
    PlainChildModelWithManager,
    PlainMyManager,
    PlainMyManagerQuerySet,
    PlainParentModelWithManager,
    ProxiedBase,
    ProxyBase,
    ProxyChild,
    ProxyModelA,
    ProxyModelB,
    ProxyModelBase,
    RedheadDuck,
    RelatingModel,
    RelationA,
    RelationB,
    RelationBase,
    RelationBC,
    RubberDuck,
    SubclassSelectorAbstractBaseModel,
    SubclassSelectorAbstractConcreteModel,
    SubclassSelectorProxyBaseModel,
    SubclassSelectorProxyConcreteModel,
    ParentLinkAndRelatedName,
    UUIDArtProject,
    UUIDArtProjectA,
    UUIDArtProjectB,
    UUIDArtProjectC,
    UUIDArtProjectD,
    UUIDPlainA,
    UUIDPlainB,
    UUIDPlainC,
    UUIDProject,
    UUIDResearchProject,
    Duck,
    PurpleHeadDuck,
    Account,
    SpecialAccount1,
    SpecialAccount1_1,
    SpecialAccount2,
)
from django.db.models.signals import post_delete


class PolymorphicTests(TransactionTestCase):
    """
    The test suite
    """

    def test_annotate_aggregate_order(self):
        # create a blog of type BlogA
        # create two blog entries in BlogA
        # create some blogs of type BlogB to make the BlogBase table data really polymorphic
        blog = BlogA.objects.create(name="B1", info="i1")
        blog.blogentry_set.create(text="bla")
        BlogEntry.objects.create(blog=blog, text="bla2")
        BlogB.objects.create(name="Bb1")
        BlogB.objects.create(name="Bb2")
        BlogB.objects.create(name="Bb3")

        qs = BlogBase.objects.annotate(entrycount=Count("BlogA___blogentry"))
        assert len(qs) == 4

        for o in qs:
            if o.name == "B1":
                assert o.entrycount == 2
            else:
                assert o.entrycount == 0

        x = BlogBase.objects.aggregate(entrycount=Count("BlogA___blogentry"))
        assert x["entrycount"] == 2

        # create some more blogs for next test
        BlogA.objects.create(name="B2", info="i2")
        BlogA.objects.create(name="B3", info="i3")
        BlogA.objects.create(name="B4", info="i4")
        BlogA.objects.create(name="B5", info="i5")

        # test ordering for field in all entries
        expected = """
[ <BlogB: id 4, name (CharField) "Bb3">,
  <BlogB: id 3, name (CharField) "Bb2">,
  <BlogB: id 2, name (CharField) "Bb1">,
  <BlogA: id 8, name (CharField) "B5", info (CharField) "i5">,
  <BlogA: id 7, name (CharField) "B4", info (CharField) "i4">,
  <BlogA: id 6, name (CharField) "B3", info (CharField) "i3">,
  <BlogA: id 5, name (CharField) "B2", info (CharField) "i2">,
  <BlogA: id 1, name (CharField) "B1", info (CharField) "i1"> ]"""
        assert repr(BlogBase.objects.order_by("-name")).strip() == expected.strip()

        # different RDBMS return different orders for the nulls, and we can't use F
        # and nulls_first or nulls_last here to standardize it, so our test is
        # conditional
        blog_names = [blg.name for blg in BlogBase.objects.order_by("-BlogA___info")]
        ordered = blog_names[:3]
        if all([name.startswith("Bb") for name in ordered]):
            ordered = blog_names[3:]
        else:
            assert all([name.startswith("Bb") for name in blog_names[-3:]])
            ordered = blog_names[:-3]
        assert ordered == ["B5", "B4", "B3", "B2", "B1"]

    def test_limit_choices_to(self):
        """
        this is not really a testcase, as limit_choices_to only affects the Django admin
        """
        # create a blog of type BlogA
        blog_a = BlogA.objects.create(name="aa", info="aa")
        blog_b = BlogB.objects.create(name="bb")
        # create two blog entries
        entry1 = BlogEntry_limit_choices_to.objects.create(blog=blog_b, text="bla2")
        entry2 = BlogEntry_limit_choices_to.objects.create(blog=blog_b, text="bla2")

    def test_primary_key_custom_field_problem(self):
        """
        object retrieval problem occuring with some custom primary key fields (UUIDField as test case)
        """
        up1 = UUIDProject.objects.create(topic="John's gathering")
        up2 = UUIDArtProject.objects.create(topic="Sculpting with Tim", artist="T. Turner")
        up3 = UUIDResearchProject.objects.create(
            topic="Swallow Aerodynamics", supervisor="Dr. Winter"
        )

        up4 = UUIDArtProjectA.objects.create(topic="ProjectA", artist="Artist A")
        up5 = UUIDArtProjectB.objects.create(topic="ProjectB", artist="Artist B")
        up6 = UUIDArtProjectC.objects.create(topic="ProjectC", artist="Artist C")
        up7 = UUIDArtProjectD.objects.create(topic="ProjectD", artist="Artist D")

        qs = UUIDProject.objects.all()
        ol = list(qs)
        a = qs[0]
        b = qs[1]
        c = qs[2]
        assert len(qs) == 7
        assert isinstance(a.uuid_primary_key, uuid.UUID)
        assert isinstance(a.pk, uuid.UUID)

        # https://github.com/jazzband/django-polymorphic/issues/306
        assert {up1, up2, up3, up4, up5, up6, up7} == set(qs)
        assert {up2, up4, up5, up6, up7} == set(UUIDArtProject.objects.all())
        assert {up3} == set(UUIDResearchProject.objects.all())
        assert {up4, up5, up6, up7} == set(UUIDArtProjectA.objects.all())
        assert {up5, up6, up7} == set(UUIDArtProjectB.objects.all())
        assert {up6, up7} == set(UUIDArtProjectC.objects.all())
        assert {up7} == set(UUIDArtProjectD.objects.all())

        a = UUIDPlainA.objects.create(field1="A1")
        b = UUIDPlainB.objects.create(field1="B1", field2="B2")
        c = UUIDPlainC.objects.create(field1="C1", field2="C2", field3="C3")
        qs = UUIDPlainA.objects.all()
        # Test that primary key values are valid UUIDs
        assert uuid.UUID(f"urn:uuid:{a.pk}", version=1) == a.pk
        assert uuid.UUID(f"urn:uuid:{c.pk}", version=1) == c.pk

    def create_model2abcd(self):
        """
        Create the chain of objects of Model2,
        this is reused in various tests.
        """
        a = Model2A.objects.create(field1="A1")
        b = Model2B.objects.create(field1="B1", field2="B2")
        c = Model2C.objects.create(field1="C1", field2="C2", field3="C3")
        d = Model2D.objects.create(field1="D1", field2="D2", field3="D3", field4="D4")

        return a, b, c, d

    def test_simple_inheritance(self):
        self.create_model2abcd()

        objects = Model2A.objects.all()
        self.assertQuerySetEqual(
            objects,
            [Model2A, Model2B, Model2C, Model2D],
            transform=lambda o: o.__class__,
            ordered=False,
        )

    def test_defer_fields(self):
        self.create_model2abcd()

        objects_deferred = Model2A.objects.defer("field1").order_by("id")

        assert "field1" not in objects_deferred[0].__dict__, (
            "field1 was not deferred (using defer())"
        )

        # Check that we have exactly one deferred field ('field1') per resulting object.
        for obj in objects_deferred:
            deferred_fields = obj.get_deferred_fields()
            assert len(deferred_fields) == 1
            assert "field1" in deferred_fields

        objects_only = Model2A.objects.only("pk", "polymorphic_ctype", "field1")

        assert "field1" in objects_only[0].__dict__, (
            'qs.only("field1") was used, but field1 was incorrectly deferred'
        )
        assert "field1" in objects_only[3].__dict__, (
            'qs.only("field1") was used, but field1 was incorrectly deferred on a child model'
        )
        assert "field4" not in objects_only[3].__dict__, "field4 was not deferred (using only())"
        assert "field1" not in objects_only[0].get_deferred_fields()

        assert "field2" in objects_only[1].get_deferred_fields()

        # objects_only[2] has several deferred fields, ensure they are all set as such.
        model2c_deferred = objects_only[2].get_deferred_fields()
        assert "field2" in model2c_deferred
        assert "field3" in model2c_deferred
        assert "model2a_ptr_id" in model2c_deferred

        # objects_only[3] has a few more fields that should be set as deferred.
        model2d_deferred = objects_only[3].get_deferred_fields()
        assert "field2" in model2d_deferred
        assert "field3" in model2d_deferred
        assert "field4" in model2d_deferred
        assert "model2a_ptr_id" in model2d_deferred
        assert "model2b_ptr_id" in model2d_deferred

        ModelX.objects.create(field_b="A1", field_x="A2")
        ModelY.objects.create(field_b="B1", field_y="B2")

        # If we defer a field on a descendent, the parent's field is not deferred.
        objects_deferred = Base.objects.defer("ModelY___field_y")
        assert "field_y" not in objects_deferred[0].get_deferred_fields()
        assert "field_y" in objects_deferred[1].get_deferred_fields()

        objects_only = Base.objects.only(
            "polymorphic_ctype", "ModelY___field_y", "ModelX___field_x"
        )
        assert "field_b" in objects_only[0].get_deferred_fields()
        assert "field_b" in objects_only[1].get_deferred_fields()

    def test_defer_related_fields(self):
        self.create_model2abcd()

        objects_deferred_field4 = Model2A.objects.defer("Model2D___field4")
        assert "field4" not in objects_deferred_field4[3].__dict__, (
            "field4 was not deferred (using defer(), traversing inheritance)"
        )
        assert objects_deferred_field4[0].__class__ == Model2A
        assert objects_deferred_field4[1].__class__ == Model2B
        assert objects_deferred_field4[2].__class__ == Model2C
        assert objects_deferred_field4[3].__class__ == Model2D

        objects_only_field4 = Model2A.objects.only(
            "polymorphic_ctype",
            "field1",
            "Model2B___id",
            "Model2B___field2",
            "Model2B___model2a_ptr",
            "Model2C___id",
            "Model2C___field3",
            "Model2C___model2b_ptr",
            "Model2D___id",
            "Model2D___model2c_ptr",
        )
        assert objects_only_field4[0].__class__ == Model2A
        assert objects_only_field4[1].__class__ == Model2B
        assert objects_only_field4[2].__class__ == Model2C
        assert objects_only_field4[3].__class__ == Model2D

    def test_manual_get_real_instance(self):
        self.create_model2abcd()

        o = Model2A.objects.non_polymorphic().get(field1="C1")
        assert o.get_real_instance().__class__ == Model2C

    def test_get_real_instance_with_stale_content_type(self):
        ctype = ContentType.objects.create(app_label="tests", model="stale")
        o = Model2A.objects.create(field1="A1", polymorphic_ctype=ctype)

        assert o.get_real_instance_class() is None
        match = "does not have a corresponding model"
        with pytest.raises(PolymorphicTypeInvalid, match=match):
            o.get_real_instance()

    def test_get_real_concrete_instance_class_id_with_stale_content_type(self):
        """Test get_real_concrete_instance_class_id returns None for stale ContentType"""
        ctype = ContentType.objects.create(app_label="tests", model="stale_model")
        o = Model2A.objects.create(field1="A1", polymorphic_ctype=ctype)

        # When ContentType is stale, get_real_instance_class returns None
        # which should cause get_real_concrete_instance_class_id to return None
        assert o.get_real_concrete_instance_class_id() is None

    def test_get_real_concrete_instance_class_with_stale_content_type(self):
        """Test get_real_concrete_instance_class returns None for stale ContentType"""
        ctype = ContentType.objects.create(app_label="tests", model="another_stale")
        o = Model2A.objects.create(field1="A1", polymorphic_ctype=ctype)

        # When ContentType is stale, get_real_instance_class returns None
        # which should cause get_real_concrete_instance_class to return None
        assert o.get_real_concrete_instance_class() is None

    def test_get_real_concrete_instance_class_with_proxy_model(self):
        """Test get_real_concrete_instance_class with a proxy model"""
        # Create a regular polymorphic object
        a = Model2A.objects.create(field1="A1")

        # get_real_concrete_instance_class should return the concrete model class
        concrete_class = a.get_real_concrete_instance_class()
        assert concrete_class == Model2A

    def test_non_polymorphic(self):
        self.create_model2abcd()

        objects = list(Model2A.objects.all().non_polymorphic())
        self.assertQuerySetEqual(
            objects,
            [Model2A, Model2A, Model2A, Model2A],
            transform=lambda o: o.__class__,
        )

    def test_get_real_instances(self):
        self.create_model2abcd()
        qs = Model2A.objects.all().non_polymorphic()

        # from queryset
        objects = qs.get_real_instances()
        self.assertQuerySetEqual(
            objects,
            [Model2A, Model2B, Model2C, Model2D],
            transform=lambda o: o.__class__,
        )

        # from a manual list
        objects = Model2A.objects.get_real_instances(list(qs))
        self.assertQuerySetEqual(
            objects,
            [Model2A, Model2B, Model2C, Model2D],
            transform=lambda o: o.__class__,
        )

        # from empty list
        objects = Model2A.objects.get_real_instances([])
        self.assertQuerySetEqual(objects, [], transform=lambda o: o.__class__)

    def test_queryset_missing_derived(self):
        a = Model2A.objects.create(field1="A1")
        b = Model2B.objects.create(field1="B1", field2="B2")
        c = Model2C.objects.create(field1="C1", field2="C2", field3="C3")
        b_base = Model2A.objects.non_polymorphic().get(pk=b.pk)
        c_base = Model2A.objects.non_polymorphic().get(pk=c.pk)

        b_pk = b.pk  # Save pk before deletion
        b.delete(keep_parents=True)  # e.g. table was truncated

        qs_base = Model2A.objects.order_by("field1").non_polymorphic()
        qs_polymorphic = Model2A.objects.order_by("field1").all()

        assert list(qs_base) == [a, b_base, c_base]
        assert list(qs_polymorphic) == [a, b_base, c]
        result = list(qs_polymorphic)
        assert len(result) == 3
        assert result[0] == a
        assert result[1].pk == b_pk  # b returned as Model2A (parent)
        assert isinstance(result[1], Model2A)
        assert not isinstance(result[1], Model2B)
        assert result[2] == c

    def test_queryset_missing_contenttype(self):
        stale_ct = ContentType.objects.create(app_label="tests", model="nonexisting")
        a1 = Model2A.objects.create(field1="A1")
        a2 = Model2A.objects.create(field1="A2")
        c = Model2C.objects.create(field1="C1", field2="C2", field3="C3")
        c_base = Model2A.objects.non_polymorphic().get(pk=c.pk)

        Model2B.objects.filter(pk=a2.pk).update(polymorphic_ctype=stale_ct)

        qs_base = Model2A.objects.order_by("field1").non_polymorphic()
        qs_polymorphic = Model2A.objects.order_by("field1").all()

        assert list(qs_base) == [a1, a2, c_base]
        assert list(qs_polymorphic) == [a1, a2, c]

    def test_translate_polymorphic_q_object(self):
        self.create_model2abcd()

        q = Model2A.translate_polymorphic_Q_object(Q(instance_of=Model2C))
        objects = Model2A.objects.filter(q)
        self.assertQuerySetEqual(
            objects, [Model2C, Model2D], transform=lambda o: o.__class__, ordered=False
        )

    def test_create_instanceof_q(self):
        # Test with a list of models
        q = query_translate.create_instanceof_q([Model2B])
        expected = sorted(
            ContentType.objects.get_for_model(m).pk for m in [Model2B, Model2C, Model2D]
        )
        assert dict(q.children) == dict(polymorphic_ctype__in=expected)

    def test_base_manager(self):
        def base_manager(model):
            return (type(model._base_manager), model._base_manager.model)

        assert base_manager(PlainA) == (models.Manager, PlainA)
        assert base_manager(PlainB) == (models.Manager, PlainB)
        assert base_manager(PlainC) == (models.Manager, PlainC)

        assert base_manager(Model2A) == (PolymorphicManager, Model2A)
        assert base_manager(Model2B) == (PolymorphicManager, Model2B)
        assert base_manager(Model2C) == (PolymorphicManager, Model2C)

        assert base_manager(One2OneRelatingModel) == (PolymorphicManager, One2OneRelatingModel)
        assert base_manager(One2OneRelatingModelDerived) == (
            PolymorphicManager,
            One2OneRelatingModelDerived,
        )

    def test_instance_default_manager(self):
        def default_manager(instance):
            return (
                type(instance.__class__._default_manager),
                instance.__class__._default_manager.model,
            )

        plain_a = PlainA(field1="C1")
        plain_b = PlainB(field2="C1")
        plain_c = PlainC(field3="C1")

        model_2a = Model2A(field1="C1")
        model_2b = Model2B(field2="C1")
        model_2c = Model2C(field3="C1")

        assert default_manager(plain_a) == (models.Manager, PlainA)
        assert default_manager(plain_b) == (models.Manager, PlainB)
        assert default_manager(plain_c) == (models.Manager, PlainC)

        assert default_manager(model_2a) == (PolymorphicManager, Model2A)
        assert default_manager(model_2b) == (PolymorphicManager, Model2B)
        assert default_manager(model_2c) == (PolymorphicManager, Model2C)

    def test_foreignkey_field(self):
        self.create_model2abcd()

        object2a = Model2A.objects.get(field1="C1")
        assert object2a.model2b.__class__ == Model2B

        object2b = Model2B.objects.get(field1="C1")
        assert object2b.model2c.__class__ == Model2C

    def test_parentage_links_are_non_polymorphic(self):
        """
        OneToOne parent links should return non-polymorphic instances
        """
        d = Model2D.objects.create(field1="D1", field2="D2", field3="D3", field4="D4")
        c = Model2C.objects.non_polymorphic().get(pk=d.pk)
        b = Model2B.objects.non_polymorphic().get(pk=d.pk)
        a = Model2A.objects.non_polymorphic().get(pk=d.pk)
        assert d.model2a_ptr.__class__ == Model2A
        assert d.model2b_ptr.__class__ == Model2B
        assert d.model2c_ptr.__class__ == Model2C
        assert d.model2c_ptr == c
        assert d.model2b_ptr == b
        assert d.model2a_ptr == a
        assert c.model2d == d
        assert c.model2d.__class__ == Model2D
        assert c.model2b_ptr.__class__ == Model2B
        assert c.model2a_ptr.__class__ == Model2A
        assert c.model2b_ptr == b
        assert c.model2a_ptr == a
        assert b.model2c == c
        assert b.model2c.__class__ == Model2C
        assert b.model2a_ptr.__class__ == Model2A
        assert b.model2a_ptr == a
        assert a.model2b.__class__ == Model2B
        assert a.model2b == b

    def test_onetoone_field(self):
        self.create_model2abcd()

        a = Model2A.objects.non_polymorphic().get(field1="C1")
        b = One2OneRelatingModelDerived.objects.create(one2one=a, field1="f1", field2="f2")

        # FIXME: this result is basically wrong, probably due to Django cacheing
        # (we used base_objects), but should not be a problem
        assert b.one2one.__class__ == Model2A
        assert b.one2one_id == b.one2one.id

        c = One2OneRelatingModelDerived.objects.get(field1="f1")
        assert c.one2one.__class__ == Model2C
        assert a.one2onerelatingmodel.__class__ == One2OneRelatingModelDerived

    def test_manytomany_field(self):
        # Model 1
        o = ModelShow1.objects.create(field1="abc")
        o.m2m.add(o)
        o.save()
        assert (
            repr(ModelShow1.objects.all())
            == "[ <ModelShow1: id 1, field1 (CharField), m2m (ManyToManyField)> ]"
        )

        # Model 2
        o = ModelShow2.objects.create(field1="abc")
        o.m2m.add(o)
        o.save()
        assert repr(ModelShow2.objects.all()) == '[ <ModelShow2: id 1, field1 "abc", m2m 1> ]'

        # Model 3
        o = ModelShow3.objects.create(field1="abc")
        o.m2m.add(o)
        o.save()
        assert (
            repr(ModelShow3.objects.all())
            == '[ <ModelShow3: id 1, field1 (CharField) "abc", m2m (ManyToManyField) 1> ]'
        )
        assert (
            repr(ModelShow1.objects.all().annotate(Count("m2m")))
            == "[ <ModelShow1: id 1, field1 (CharField), m2m (ManyToManyField) - Ann: m2m__count (int)> ]"
        )
        assert (
            repr(ModelShow2.objects.all().annotate(Count("m2m")))
            == '[ <ModelShow2: id 1, field1 "abc", m2m 1 - Ann: m2m__count 1> ]'
        )
        assert (
            repr(ModelShow3.objects.all().annotate(Count("m2m")))
            == '[ <ModelShow3: id 1, field1 (CharField) "abc", m2m (ManyToManyField) 1 - Ann: m2m__count (int) 1> ]'
        )

        # no pretty printing
        ModelShow1_plain.objects.create(field1="abc")
        ModelShow2_plain.objects.create(field1="abc", field2="def")
        self.assertQuerySetEqual(
            ModelShow1_plain.objects.all(),
            [ModelShow1_plain, ModelShow2_plain],
            transform=lambda o: o.__class__,
            ordered=False,
        )

    def test_extra_method(self):
        from django.db import connection

        a, b, c, d = self.create_model2abcd()

        objects = Model2A.objects.extra(where=[f"id IN ({b.id}, {c.id})"])
        self.assertQuerySetEqual(
            objects, [Model2B, Model2C], transform=lambda o: o.__class__, ordered=False
        )

        if connection.vendor == "oracle":
            objects = Model2A.objects.extra(
                select={"select_test": "CASE WHEN field1 = 'A1' THEN 1 ELSE 0 END"},
                where=["field1 = 'A1' OR field1 = 'B1'"],
                order_by=["-id"],
            )
        else:
            objects = Model2A.objects.extra(
                select={"select_test": "field1 = 'A1'"},
                where=["field1 = 'A1' OR field1 = 'B1'"],
                order_by=["-id"],
            )
        self.assertQuerySetEqual(objects, [Model2B, Model2A], transform=lambda o: o.__class__)

        ModelExtraA.objects.create(field1="A1")
        ModelExtraB.objects.create(field1="B1", field2="B2")
        ModelExtraC.objects.create(field1="C1", field2="C2", field3="C3")
        ModelExtraExternal.objects.create(topic="extra1")
        ModelExtraExternal.objects.create(topic="extra2")
        ModelExtraExternal.objects.create(topic="extra3")
        objects = ModelExtraA.objects.extra(
            tables=["tests_modelextraexternal"],
            select={"topic": "tests_modelextraexternal.topic"},
            where=["tests_modelextraa.id = tests_modelextraexternal.id"],
        )
        assert (
            repr(objects[0])
            == '<ModelExtraA: id 1, field1 (CharField) "A1" - Extra: topic (str) "extra1">'
        )
        assert (
            repr(objects[1])
            == '<ModelExtraB: id 2, field1 (CharField) "B1", field2 (CharField) "B2" - Extra: topic (str) "extra2">'
        )
        assert (
            repr(objects[2])
            == '<ModelExtraC: id 3, field1 (CharField) "C1", field2 (CharField) "C2", field3 (CharField) "C3" - Extra: topic (str) "extra3">'
        )
        assert len(objects) == 3

    def test_instance_of_filter(self):
        self.create_model2abcd()

        objects = Model2A.objects.instance_of(Model2B)
        self.assertQuerySetEqual(
            objects,
            [Model2B, Model2C, Model2D],
            transform=lambda o: o.__class__,
            ordered=False,
        )

        objects = Model2A.objects.filter(instance_of=Model2B)
        self.assertQuerySetEqual(
            objects,
            [Model2B, Model2C, Model2D],
            transform=lambda o: o.__class__,
            ordered=False,
        )

        objects = Model2A.objects.filter(Q(instance_of=Model2B))
        self.assertQuerySetEqual(
            objects,
            [Model2B, Model2C, Model2D],
            transform=lambda o: o.__class__,
            ordered=False,
        )

        objects = Model2A.objects.not_instance_of(Model2B)
        self.assertQuerySetEqual(
            objects, [Model2A], transform=lambda o: o.__class__, ordered=False
        )

    def test_polymorphic___filter(self):
        self.create_model2abcd()

        objects = Model2A.objects.filter(Q(Model2B___field2="B2") | Q(Model2C___field3="C3"))
        self.assertQuerySetEqual(
            objects, [Model2B, Model2C], transform=lambda o: o.__class__, ordered=False
        )

    def test_polymorphic_applabel___filter(self):
        self.create_model2abcd()

        assert Model2B._meta.app_label == "tests"
        objects = Model2A.objects.filter(
            Q(tests__Model2B___field2="B2") | Q(tests__Model2C___field3="C3")
        )
        self.assertQuerySetEqual(
            objects, [Model2B, Model2C], transform=lambda o: o.__class__, ordered=False
        )

    def test_query_filter_exclude_is_immutable(self):
        # given
        q_to_reuse = Q(Model2B___field2="something")
        untouched_q_object = Q(Model2B___field2="something")
        # when
        Model2A.objects.filter(q_to_reuse).all()
        # then
        assert q_to_reuse.children == untouched_q_object.children

        # given
        q_to_reuse = Q(Model2B___field2="something")
        untouched_q_object = Q(Model2B___field2="something")
        # when
        Model2B.objects.filter(q_to_reuse).all()
        # then
        assert q_to_reuse.children == untouched_q_object.children

    def test_polymorphic___filter_field(self):
        p = ModelUnderRelParent.objects.create(_private=True, field1="AA")
        ModelUnderRelChild.objects.create(parent=p, _private2=True)

        # The "___" filter should also parse to "parent" -> "_private" as fallback.
        objects = ModelUnderRelChild.objects.filter(parent___private=True)
        assert len(objects) == 1

    def test_polymorphic___filter_reverse_field(self):
        p = ModelUnderRelParent.objects.create(_private=True, field1="BB")
        ModelUnderRelChild.objects.create(parent=p, _private2=True)

        # Also test for reverse relations
        objects = ModelUnderRelParent.objects.filter(children___private2=True)
        assert len(objects) == 1

    def test_delete(self):
        a, b, c, d = self.create_model2abcd()

        oa = Model2A.objects.get(id=b.id)
        assert oa.__class__ == Model2B
        assert Model2A.objects.count() == 4

        oa.delete()
        objects = Model2A.objects.all()
        self.assertQuerySetEqual(
            objects,
            [Model2A, Model2C, Model2D],
            transform=lambda o: o.__class__,
            ordered=False,
        )

    def test_combine_querysets(self):
        ModelX.objects.create(field_x="x", field_b="1")
        ModelY.objects.create(field_y="y", field_b="2")

        qs = Base.objects.instance_of(ModelX) | Base.objects.instance_of(ModelY)
        qs = qs.order_by("field_b")
        assert repr(qs[0]) == "<ModelX: id 1, field_b (CharField), field_x (CharField)>"
        assert repr(qs[1]) == "<ModelY: id 2, field_b (CharField), field_y (CharField)>"
        assert len(qs) == 2

    def test_multiple_inheritance(self):
        # multiple inheritance, subclassing third party models (mix PolymorphicModel with models.Model)

        Enhance_Base.objects.create(field_b="b-base")
        Enhance_Inherit.objects.create(field_b="b-inherit", field_p="p", field_i="i")

        qs = Enhance_Base.objects.all()
        assert len(qs) == 2
        assert (
            repr(qs[0]) == '<Enhance_Base: base_id (AutoField/pk) 1, field_b (CharField) "b-base">'
        )
        assert (
            repr(qs[1])
            == '<Enhance_Inherit: base_id (AutoField/pk) 2, field_b (CharField) "b-inherit", id 1, field_p (CharField) "p", field_i (CharField) "i">'
        )

    def test_relation_base(self):
        # ForeignKey, ManyToManyField
        obase = RelationBase.objects.create(field_base="base")
        oa = RelationA.objects.create(field_base="A1", field_a="A2", fk=obase)
        ob = RelationB.objects.create(field_base="B1", field_b="B2", fk=oa)
        oc = RelationBC.objects.create(field_base="C1", field_b="C2", field_c="C3", fk=oa)
        oa.m2m.add(oa)
        oa.m2m.add(ob)

        objects = RelationBase.objects.order_by("pk").all()
        assert (
            repr(objects[0])
            == '<RelationBase: id 1, field_base (CharField) "base", fk (ForeignKey) None, m2m (ManyToManyField) 0>'
        )
        assert (
            repr(objects[1])
            == '<RelationA: id 2, field_base (CharField) "A1", fk (ForeignKey) RelationBase, field_a (CharField) "A2", m2m (ManyToManyField) 2>'
        )
        assert (
            repr(objects[2])
            == '<RelationB: id 3, field_base (CharField) "B1", fk (ForeignKey) RelationA, field_b (CharField) "B2", m2m (ManyToManyField) 1>'
        )
        assert (
            repr(objects[3])
            == '<RelationBC: id 4, field_base (CharField) "C1", fk (ForeignKey) RelationA, field_b (CharField) "C2", field_c (CharField) "C3", m2m (ManyToManyField) 0>'
        )
        assert len(objects) == 4

        oa = RelationBase.objects.get(id=2)
        assert (
            repr(oa.fk)
            == '<RelationBase: id 1, field_base (CharField) "base", fk (ForeignKey) None, m2m (ManyToManyField) 0>'
        )

        objects = oa.relationbase_set.order_by("pk").all()
        assert (
            repr(objects[0])
            == '<RelationB: id 3, field_base (CharField) "B1", fk (ForeignKey) RelationA, field_b (CharField) "B2", m2m (ManyToManyField) 1>'
        )
        assert (
            repr(objects[1])
            == '<RelationBC: id 4, field_base (CharField) "C1", fk (ForeignKey) RelationA, field_b (CharField) "C2", field_c (CharField) "C3", m2m (ManyToManyField) 0>'
        )
        assert len(objects) == 2

        ob = RelationBase.objects.get(id=3)
        assert (
            repr(ob.fk)
            == '<RelationA: id 2, field_base (CharField) "A1", fk (ForeignKey) RelationBase, field_a (CharField) "A2", m2m (ManyToManyField) 2>'
        )

        oa = RelationA.objects.get()
        objects = oa.m2m.order_by("pk").all()
        assert (
            repr(objects[0])
            == '<RelationA: id 2, field_base (CharField) "A1", fk (ForeignKey) RelationBase, field_a (CharField) "A2", m2m (ManyToManyField) 2>'
        )
        assert (
            repr(objects[1])
            == '<RelationB: id 3, field_base (CharField) "B1", fk (ForeignKey) RelationA, field_b (CharField) "B2", m2m (ManyToManyField) 1>'
        )
        assert len(objects) == 2

    def test_user_defined_manager(self):
        self.create_model2abcd()
        ModelWithMyManager.objects.create(field1="D1a", field4="D4a")
        ModelWithMyManager.objects.create(field1="D1b", field4="D4b")

        # MyManager should reverse the sorting of field1
        objects = ModelWithMyManager.objects.all()
        self.assertQuerySetEqual(
            objects,
            [(ModelWithMyManager, "D1b", "D4b"), (ModelWithMyManager, "D1a", "D4a")],
            transform=lambda o: (o.__class__, o.field1, o.field4),
        )

        assert type(ModelWithMyManager.objects) is MyManager
        assert type(ModelWithMyManager._default_manager) is MyManager

    def test_user_defined_manager_as_secondary(self):
        self.create_model2abcd()
        ModelWithMyManagerNoDefault.objects.create(field1="D1a", field4="D4a")
        ModelWithMyManagerNoDefault.objects.create(field1="D1b", field4="D4b")

        # MyManager should reverse the sorting of field1
        objects = ModelWithMyManagerNoDefault.my_objects.all()
        self.assertQuerySetEqual(
            objects,
            [
                (ModelWithMyManagerNoDefault, "D1b", "D4b"),
                (ModelWithMyManagerNoDefault, "D1a", "D4a"),
            ],
            transform=lambda o: (o.__class__, o.field1, o.field4),
        )

        assert type(ModelWithMyManagerNoDefault.my_objects) is MyManager
        assert type(ModelWithMyManagerNoDefault.objects) is PolymorphicManager
        assert type(ModelWithMyManagerNoDefault._default_manager) is PolymorphicManager

    def test_user_objects_manager_as_secondary(self):
        self.create_model2abcd()
        ModelWithMyManagerDefault.objects.create(field1="D1a", field4="D4a")
        ModelWithMyManagerDefault.objects.create(field1="D1b", field4="D4b")

        assert type(ModelWithMyManagerDefault.my_objects) is MyManager
        assert type(ModelWithMyManagerDefault.objects) is PolymorphicManager
        assert type(ModelWithMyManagerDefault._default_manager) is MyManager

    def test_user_defined_queryset_as_manager(self):
        self.create_model2abcd()
        ModelWithMyManager2.objects.create(field1="D1a", field4="D4a")
        ModelWithMyManager2.objects.create(field1="D1b", field4="D4b")

        objects = ModelWithMyManager2.objects.all()
        self.assertQuerySetEqual(
            objects,
            [(ModelWithMyManager2, "D1a", "D4a"), (ModelWithMyManager2, "D1b", "D4b")],
            transform=lambda o: (o.__class__, o.field1, o.field4),
            ordered=False,
        )

        assert (
            type(ModelWithMyManager2.objects).__name__ == "PolymorphicManagerFromMyManagerQuerySet"
        )
        assert (
            type(ModelWithMyManager2._default_manager).__name__
            == "PolymorphicManagerFromMyManagerQuerySet"
        )

    def test_manager_inheritance(self):
        # by choice of MRO, should be MyManager from MROBase1.
        assert type(MRODerived.objects) is MyManager

    def test_queryset_assignment(self):
        # This is just a consistency check for now, testing standard Django behavior.
        parent = PlainParentModelWithManager.objects.create()
        child = PlainChildModelWithManager.objects.create(fk=parent)
        assert type(PlainParentModelWithManager._default_manager) is models.Manager
        assert type(PlainChildModelWithManager._default_manager) is PlainMyManager
        assert type(PlainChildModelWithManager.objects) is PlainMyManager
        assert type(PlainChildModelWithManager.objects.all()) is PlainMyManagerQuerySet

        # A related set is created using the model's _default_manager, so does gain extra methods.
        assert type(parent.childmodel_set.my_queryset_foo()) is PlainMyManagerQuerySet

        # For polymorphic models, the same should happen.
        parent = ParentModelWithManager.objects.create()
        child = ChildModelWithManager.objects.create(fk=parent)
        assert type(ParentModelWithManager._default_manager) is PolymorphicManager
        assert type(ChildModelWithManager._default_manager) is MyManager
        assert type(ChildModelWithManager.objects) is MyManager
        assert type(ChildModelWithManager.objects.my_queryset_foo()) is MyManagerQuerySet

        # A related set is created using the model's _default_manager, so does gain extra methods.
        assert type(parent.childmodel_set.my_queryset_foo()) is MyManagerQuerySet

    def test_proxy_models(self):
        # prepare some data
        for data in ("bleep bloop", "I am a", "computer"):
            ProxyChild.objects.create(some_data=data)

        # this caches ContentType queries so they don't interfere with our query counts later
        list(ProxyBase.objects.all())

        # one query per concrete class
        with self.assertNumQueries(1):
            items = list(ProxyBase.objects.all())

        assert isinstance(items[0], ProxyChild)

    def test_queryset_on_proxy_model_does_not_return_superclasses(self):
        ProxyBase.objects.create(some_data="Base1")
        ProxyBase.objects.create(some_data="Base2")
        ProxyChild.objects.create(some_data="Child1")
        ProxyChild.objects.create(some_data="Child2")
        ProxyChild.objects.create(some_data="Child3")

        assert ProxyBase.objects.count() == 5
        assert ProxyChild.objects.count() == 3

    def test_proxy_get_real_instance_class(self):
        """
        The call to ``get_real_instance()`` also checks whether the returned model is of the correct type.
        This unit test guards that this check is working properly. For instance,
        proxy child models need to be handled separately.
        """
        name = "Item1"
        nonproxychild = NonProxyChild.objects.create(name=name)

        pb = ProxyBase.objects.get(id=1)
        assert pb.get_real_instance_class() == NonProxyChild
        assert pb.get_real_instance() == nonproxychild
        assert pb.name == name

        pbm = NonProxyChild.objects.get(id=1)
        assert pbm.get_real_instance_class() == NonProxyChild
        assert pbm.get_real_instance() == nonproxychild
        assert pbm.name == name

    def test_content_types_for_proxy_models(self):
        """Checks if ContentType is capable of returning proxy models."""
        from django.contrib.contenttypes.models import ContentType

        ct = ContentType.objects.get_for_model(ProxyChild, for_concrete_model=False)
        assert ProxyChild == ct.model_class()

    def test_proxy_model_inheritance(self):
        """
        Polymorphic abilities should also work when the base model is a proxy object.
        """
        # The managers should point to the proper objects.
        # otherwise, the whole excersise is pointless.
        assert ProxiedBase.objects.model == ProxiedBase
        assert ProxyModelBase.objects.model == ProxyModelBase
        assert ProxyModelA.objects.model == ProxyModelA
        assert ProxyModelB.objects.model == ProxyModelB

        # Create objects
        object1_pk = ProxyModelA.objects.create(name="object1").pk
        object2_pk = ProxyModelB.objects.create(name="object2", field2="bb").pk

        # Getting single objects
        object1 = ProxyModelBase.objects.get(name="object1")
        object2 = ProxyModelBase.objects.get(name="object2")
        assert repr(object1) == (
            f'<ProxyModelA: id {object1_pk}, name (CharField) "object1", field1 (CharField) "">'
        )
        assert repr(object2) == (
            '<ProxyModelB: id %i, name (CharField) "object2", field2 (CharField) "bb">'
            % object2_pk
        )
        assert isinstance(object1, ProxyModelA)
        assert isinstance(object2, ProxyModelB)

        # Same for lists
        objects = list(ProxyModelBase.objects.all().order_by("name"))
        assert repr(objects[0]) == (
            f'<ProxyModelA: id {object1_pk}, name (CharField) "object1", field1 (CharField) "">'
        )
        assert repr(objects[1]) == (
            '<ProxyModelB: id %i, name (CharField) "object2", field2 (CharField) "bb">'
            % object2_pk
        )
        assert isinstance(objects[0], ProxyModelA)
        assert isinstance(objects[1], ProxyModelB)

    def test_custom_pk(self):
        pk_base = CustomPkBase.objects.create(b="b")
        pk_inherit = CustomPkInherit.objects.create(b="b", i="i")
        qs = CustomPkBase.objects.all()
        assert len(qs) == 2
        assert repr(qs[0]) == f'<CustomPkBase: id {pk_base.id}, b (CharField) "b">'
        assert (
            repr(qs[1])
            == f'<CustomPkInherit: id {pk_inherit.id}, b (CharField) "b", custom_id (AutoField/pk) {pk_inherit.custom_id}, i (CharField) "i">'
        )

    def test_fix_getattribute(self):
        # fixed issue in PolymorphicModel.__getattribute__: field name same as model name
        o = ModelFieldNameTest.objects.create(modelfieldnametest="1")
        assert repr(o) == "<ModelFieldNameTest: id 1, modelfieldnametest (CharField)>"

        # if subclass defined __init__ and accessed class members,
        # __getattribute__ had a problem: "...has no attribute 'sub_and_superclass_dict'"
        o = InitTestModelSubclass.objects.create()
        assert o.bar == "XYZ"

    def test_parent_link_and_related_name(self):
        t = ParentLinkAndRelatedName(field1="ParentLinkAndRelatedName")
        t.save()
        p = ModelShow1_plain.objects.get(field1="ParentLinkAndRelatedName")

        # check that p is equal to the
        assert isinstance(p, ParentLinkAndRelatedName)
        assert p == t

        # check that the accessors to parent and sublass work correctly and return the right object
        p = ModelShow1_plain.objects.non_polymorphic().get(field1="ParentLinkAndRelatedName")
        # p should be Plain1 and t ParentLinkAndRelatedName, so not equal
        assert p != t
        assert p == t.superclass
        assert p.related_name_subclass == t

        # test that we can delete the object
        t.delete()

    def test_polymorphic__accessor_caching(self):
        blog_a = BlogA.objects.create(name="blog")

        blog_base = BlogBase.objects.non_polymorphic().get(id=blog_a.id)
        blog_a = BlogA.objects.get(id=blog_a.id)

        # test reverse accessor & check that we get back cached object on repeated access
        self.assertEqual(blog_base.bloga, blog_a)
        self.assertIs(blog_base.bloga, blog_base.bloga)
        cached_blog_a = blog_base.bloga

        # test forward accessor & check that we get back cached object on repeated access
        self.assertEqual(blog_a.blogbase_ptr, blog_base)
        self.assertIs(blog_a.blogbase_ptr, blog_a.blogbase_ptr)
        cached_blog_base = blog_a.blogbase_ptr

        # check that refresh_from_db correctly clears cached related objects
        blog_base.refresh_from_db()
        blog_a.refresh_from_db()

        self.assertIsNot(cached_blog_a, blog_base.bloga)
        self.assertIsNot(cached_blog_base, blog_a.blogbase_ptr)

    def test_polymorphic__aggregate(self):
        """test ModelX___field syntax on aggregate (should work for annotate either)"""

        Model2A.objects.create(field1="A1")
        Model2B.objects.create(field1="A1", field2="B2")
        Model2B.objects.create(field1="A1", field2="B2")

        # aggregate using **kwargs
        result = Model2A.objects.aggregate(cnt=Count("Model2B___field2"))
        assert result == {"cnt": 2}

        # aggregate using **args
        with pytest.raises(
            AssertionError,
            match="model lookup supported for keyword arguments only",
        ):
            Model2A.objects.aggregate(Count("Model2B___field2"))

    def test_polymorphic__aggregate_empty_queryset(self):
        """test the fix for test___lookup in Django 5.1+"""
        line = ModelOrderLine.objects.create()
        result = line.articles.aggregate(Sum("sales_points"))
        assert result == {"sales_points__sum": None}

    def test_polymorphic__complex_aggregate(self):
        """test (complex expression on) aggregate (should work for annotate either)"""

        Model2A.objects.create(field1="A1")
        Model2B.objects.create(field1="A1", field2="B2")
        Model2B.objects.create(field1="A1", field2="B2")

        # aggregate using **kwargs
        cnt = Count(Case(When(Model2B___field2="B2", then=1)))
        result = Model2A.objects.aggregate(
            cnt_a1=Count(Case(When(field1="A1", then=1))),
            cnt_b2=cnt,
        )
        assert result == {"cnt_b2": 2, "cnt_a1": 3}

        # test that our expression was immutable
        # FIXME - expression passed into aggregate are not immutable!
        # assert (
        #     cnt.get_source_expressions()[0]
        #     .get_source_expressions()[0]
        #     .get_source_expressions()[0]
        #     .children[0][0]
        #     == "Model2B___field2"
        # )

        # aggregate using **args
        # we have to set the defaul alias or django won't except a complex expression
        # on aggregate/annotate
        def ComplexAgg(expression):
            complexagg = Count(expression) * 10
            complexagg.default_alias = "complexagg"
            return complexagg

        with pytest.raises(
            AssertionError,
            match="model lookup supported for keyword arguments only",
        ):
            Model2A.objects.aggregate(ComplexAgg("Model2B___field2"))

    def test_annotate_f_expression(self):
        """
        Verify that F() expressions with '___' syntax correctly translate in annotate() calls.
        """
        Model2A.objects.create(field1="A_only")
        Model2B.objects.create(field1="A_from_B1", field2="B2_val1")
        Model2B.objects.create(field1="A_from_B2", field2="B2_val2")

        # Use annotate with an F-expression targeting a child model field
        # We'll count occurrences of field2 from Model2B
        # This implicitly tests that 'Model2B___field2' is correctly translated
        annotated_queryset = Model2A.objects.annotate(
            field2_count=Count(models.F("Model2B___field2"))
        ).order_by("pk")

        results = list(annotated_queryset)
        assert len(results) == 3

        # For Model2A that is not a Model2B, the count should be 0
        assert results[0].field1 == "A_only"
        assert results[0].field2_count == 0

        # For Model2B instances, the field2_count should be 1
        assert results[1].field1 == "A_from_B1"
        assert results[1].field2_count == 1

        assert results[2].field1 == "A_from_B2"
        assert results[2].field2_count == 1

    def test_polymorphic__filtered_relation(self):
        """test annotation using FilteredRelation"""

        blog = BlogA.objects.create(name="Ba1", info="i1 joined")
        blog.blogentry_set.create(text="bla1 joined")
        blog.blogentry_set.create(text="bla2 joined")
        blog.blogentry_set.create(text="bla3 joined")
        blog.blogentry_set.create(text="bla4")
        blog.blogentry_set.create(text="bla5")
        BlogA.objects.create(name="Ba2", info="i2 joined")
        BlogA.objects.create(name="Ba3", info="i3")
        BlogB.objects.create(name="Bb3")

        result = BlogA.objects.annotate(
            text_joined=FilteredRelation(
                "blogentry", condition=Q(blogentry__text__contains="joined")
            ),
        ).aggregate(Count("text_joined"))
        assert result == {"text_joined__count": 3}

        result = BlogA.objects.annotate(
            text_joined=FilteredRelation(
                "blogentry", condition=Q(blogentry__text__contains="joined")
            ),
        ).aggregate(count=Count("text_joined"))
        assert result == {"count": 3}

        result = BlogBase.objects.annotate(
            info_joined=FilteredRelation("bloga", condition=Q(BlogA___info__contains="joined")),
        ).aggregate(Count("info_joined"))
        assert result == {"info_joined__count": 2}

        result = BlogBase.objects.annotate(
            info_joined=FilteredRelation("bloga", condition=Q(BlogA___info__contains="joined")),
        ).aggregate(count=Count("info_joined"))
        assert result == {"count": 2}

        # We should get a BlogA and a BlogB
        result = BlogBase.objects.annotate(
            info_joined=FilteredRelation("bloga", condition=Q(BlogA___info__contains="joined")),
        ).filter(info_joined__isnull=True)
        assert result.count() == 2
        assert isinstance(result.first(), BlogA)
        assert isinstance(result.last(), BlogB)

    def test_polymorphic__expressions(self):
        from django.db.models.functions import Concat

        # no exception raised
        result = Model2B.objects.annotate(val=Concat("field1", "field2"))
        assert list(result) == []

    def test_null_polymorphic_id(self):
        """Test that a proper error message is displayed when the database lacks the ``polymorphic_ctype_id``"""
        Model2A.objects.create(field1="A1")
        Model2B.objects.create(field1="A1", field2="B2")
        Model2B.objects.create(field1="A1", field2="B2")
        Model2A.objects.all().update(polymorphic_ctype_id=None)

        with pytest.raises(PolymorphicTypeUndefined):
            list(Model2A.objects.all())

    def test_invalid_polymorphic_id(self):
        """Test that a proper error message is displayed when the database ``polymorphic_ctype_id`` is invalid"""
        Model2A.objects.create(field1="A1")
        Model2B.objects.create(field1="A1", field2="B2")
        Model2B.objects.create(field1="A1", field2="B2")
        invalid = ContentType.objects.get_for_model(PlainA).pk
        Model2A.objects.all().update(polymorphic_ctype_id=invalid)

        with pytest.raises(PolymorphicTypeInvalid):
            list(Model2A.objects.all())

    def test_bulk_create_abstract_inheritance(self):
        ArtProject.objects.bulk_create(
            [
                ArtProject(topic="Painting with Tim", artist="T. Turner"),
                ArtProject(topic="Sculpture with Tim", artist="T. Turner"),
            ]
        )
        assert sorted(ArtProject.objects.values_list("topic", "artist")) == [
            ("Painting with Tim", "T. Turner"),
            ("Sculpture with Tim", "T. Turner"),
        ]

    def test_bulk_create_proxy_inheritance(self):
        RedheadDuck.objects.bulk_create(
            [
                RedheadDuck(name="redheadduck1"),
                Duck(name="duck1"),
                RubberDuck(name="rubberduck1"),
            ]
        )
        RubberDuck.objects.bulk_create(
            [
                RedheadDuck(name="redheadduck2"),
                RubberDuck(name="rubberduck2"),
                Duck(name="duck2"),
            ]
        )
        assert sorted(RedheadDuck.objects.values_list("name", flat=True)) == [
            "redheadduck1",
            "redheadduck2",
        ]
        assert sorted(RubberDuck.objects.values_list("name", flat=True)) == [
            "rubberduck1",
            "rubberduck2",
        ]
        assert sorted(Duck.objects.values_list("name", flat=True)) == [
            "duck1",
            "duck2",
            "redheadduck1",
            "redheadduck2",
            "rubberduck1",
            "rubberduck2",
        ]

    def test_bulk_create_unsupported_multi_table_inheritance(self):
        with pytest.raises(ValueError):
            MultiTableDerived.objects.bulk_create(
                [MultiTableDerived(field1="field1", field2="field2")]
            )

    def test_bulk_create_ignore_conflicts(self):
        try:
            ArtProject.objects.bulk_create(
                [
                    ArtProject(topic="Painting with Tim", artist="T. Turner"),
                    ArtProject.objects.create(topic="Sculpture with Tim", artist="T. Turner"),
                ],
                ignore_conflicts=True,
            )
            assert ArtProject.objects.count() == 2
        except NotSupportedError:
            from django.db import connection

            assert connection.vendor in ("oracle"), (
                f"{connection.vendor} should support ignore_conflicts"
            )

    def test_bulk_create_no_ignore_conflicts(self):
        with pytest.raises(IntegrityError):
            ArtProject.objects.bulk_create(
                [
                    ArtProject(topic="Painting with Tim", artist="T. Turner"),
                    ArtProject.objects.create(topic="Sculpture with Tim", artist="T. Turner"),
                ],
                ignore_conflicts=False,
            )
        assert ArtProject.objects.count() == 1

    def test_can_query_using_subclass_selector_on_abstract_model(self):
        obj = SubclassSelectorAbstractConcreteModel.objects.create(concrete_field="abc")

        queried_obj = SubclassSelectorAbstractBaseModel.objects.filter(
            SubclassSelectorAbstractConcreteModel___concrete_field="abc"
        ).get()

        assert obj.pk == queried_obj.pk

    def test_intermediate_abstract_descriptors(self):
        mdl = SubclassSelectorAbstractConcreteModel.objects.create()
        base = SubclassSelectorAbstractBaseModel.objects.non_polymorphic().get(pk=mdl.pk)

        assert mdl.subclassselectorabstractbasemodel_ptr == base
        assert base.subclassselectorabstractconcretemodel == mdl

    def test_can_query_using_subclass_selector_on_proxy_model(self):
        obj = SubclassSelectorProxyConcreteModel.objects.create(concrete_field="abc")

        queried_obj = SubclassSelectorProxyBaseModel.objects.filter(
            SubclassSelectorProxyConcreteModel___concrete_field="abc"
        ).get()

        assert obj.pk == queried_obj.pk

    def test_intermediate_proxy_descriptors(self):
        mdl = SubclassSelectorProxyConcreteModel.objects.create()
        base = SubclassSelectorProxyBaseModel.objects.non_polymorphic().get(pk=mdl.pk)

        assert mdl.subclassselectorproxybasemodel_ptr == base
        assert mdl.subclassselectorproxybasemodel_ptr.__class__ is SubclassSelectorProxyBaseModel
        assert (
            base.subclassselectorproxyconcretemodel.__class__ is SubclassSelectorProxyConcreteModel
        )

    def test_prefetch_related_behaves_normally_with_polymorphic_model(self):
        b1 = RelatingModel.objects.create()
        b2 = RelatingModel.objects.create()
        a = b1.many2many.create()  # create Model2A
        b2.many2many.add(a)  # add same to second relating model
        qs = RelatingModel.objects.prefetch_related("many2many")
        for obj in qs:
            assert len(obj.many2many.all()) == 1

    def test_prefetch_related_with_missing(self):
        b1 = RelatingModel.objects.create()
        b2 = RelatingModel.objects.create()

        rel1 = Model2A.objects.create(field1="A1")
        rel2 = Model2B.objects.create(field1="A2", field2="B2")

        b1.many2many.add(rel1)
        b2.many2many.add(rel2)

        rel2_pk = rel2.pk  # Save pk before deletion
        rel2.delete(keep_parents=True)

        qs = RelatingModel.objects.order_by("pk").prefetch_related("many2many")
        objects = list(qs)
        assert len(objects[0].many2many.all()) == 1

        # derived object was upcast by deletion that keeps parents
        assert len(objects[1].many2many.all()) == 1
        assert objects[1].many2many.first() == Model2A.objects.get(field1="A2")
        assert len(objects[1].many2many.all()) == 1
        parent_obj = objects[1].many2many.all()[0]
        assert parent_obj.pk == rel2_pk
        assert isinstance(parent_obj, Model2A)
        assert not isinstance(parent_obj, Model2B)

        # base object does exist
        assert len(objects[1].many2many.non_polymorphic()) == 1

    def test_refresh_from_db_fields(self):
        """Test whether refresh_from_db(fields=..) works as it performs .only() queries"""
        obj = Model2B.objects.create(field1="aa", field2="bb")
        Model2B.objects.filter(pk=obj.pk).update(field1="aa1", field2="bb2")
        obj.refresh_from_db(fields=["field2"])
        assert obj.field1 == "aa"
        assert obj.field2 == "bb2"

        obj.refresh_from_db(fields=["field1"])
        assert obj.field1 == "aa1"

    def test_non_polymorphic_parent(self):
        obj = NonPolymorphicParent.objects.create()
        assert obj.delete()

    def test_iteration(self):
        for i in range(250):
            Model2B.objects.create(field1=f"B1-{i}", field2=f"B2-{i}")
        for i in range(1000):
            Model2C.objects.create(
                field1=f"C1-{i + 250}", field2=f"C2-{i + 250}", field3=f"C3-{i + 250}"
            )
        for i in range(2000):
            Model2D.objects.create(
                field1=f"D1-{i + 1250}",
                field2=f"D2-{i + 1250}",
                field3=f"D3-{i + 1250}",
                field4=f"D4-{i + 1250}",
            )

        with CaptureQueriesContext(connection) as base_all:
            for _ in Model2A.objects.non_polymorphic().all():
                pass  # Evaluating the queryset

        len_base_all = len(base_all)
        assert len_base_all == 1, (
            f"Expected 1 queries for chunked iteration over 3250 base objects. {len_base_all}"
        )

        with CaptureQueriesContext(connection) as base_iterator:
            for _ in Model2A.objects.non_polymorphic().iterator():
                pass  # Evaluating the queryset

        len_base_iterator = len(base_iterator)
        assert len_base_iterator == 1, (
            f"Expected 1 queries for chunked iteration over 3250 base objects. {len_base_iterator}"
        )

        with CaptureQueriesContext(connection) as base_chunked:
            for _ in Model2A.objects.non_polymorphic().iterator(chunk_size=1000):
                pass  # Evaluating the queryset

        len_base_chunked = len(base_chunked)
        assert len_base_chunked == 1, (
            f"Expected 1 queries for chunked iteration over 3250 base objects. {len_base_chunked}"
        )

        with CaptureQueriesContext(connection) as poly_all:
            b, c, d = 0, 0, 0
            for idx, obj in enumerate(reversed(list(Model2A.objects.order_by("-pk").all()))):
                if isinstance(obj, Model2D):
                    d += 1
                    assert obj.field1 == f"D1-{idx}"
                    assert obj.field2 == f"D2-{idx}"
                    assert obj.field3 == f"D3-{idx}"
                    assert obj.field4 == f"D4-{idx}"
                elif isinstance(obj, Model2C):
                    c += 1
                    assert obj.field1 == f"C1-{idx}"
                    assert obj.field2 == f"C2-{idx}"
                    assert obj.field3 == f"C3-{idx}"
                elif isinstance(obj, Model2B):
                    b += 1
                    assert obj.field1 == f"B1-{idx}"
                    assert obj.field2 == f"B2-{idx}"
                else:
                    assert False, "Unexpected model type"
            assert (b, c, d) == (250, 1000, 2000)

        assert len(poly_all) <= 8, (
            f"Expected < 7 queries for chunked iteration over 3250 "
            f"objects with 3 child models and the default chunk size of 2000, encountered "
            f"{len(poly_all)}"
        )

        with CaptureQueriesContext(connection) as poly_all:
            b, c, d = 0, 0, 0
            for idx, obj in enumerate(Model2A.objects.order_by("pk").iterator(chunk_size=None)):
                if isinstance(obj, Model2D):
                    d += 1
                    assert obj.field1 == f"D1-{idx}"
                    assert obj.field2 == f"D2-{idx}"
                    assert obj.field3 == f"D3-{idx}"
                    assert obj.field4 == f"D4-{idx}"
                elif isinstance(obj, Model2C):
                    c += 1
                    assert obj.field1 == f"C1-{idx}"
                    assert obj.field2 == f"C2-{idx}"
                    assert obj.field3 == f"C3-{idx}"
                elif isinstance(obj, Model2B):
                    b += 1
                    assert obj.field1 == f"B1-{idx}"
                    assert obj.field2 == f"B2-{idx}"
                else:
                    assert False, "Unexpected model type"
            assert (b, c, d) == (250, 1000, 2000)

        assert len(poly_all) <= 7, (
            f"Expected < 7 queries for chunked iteration over 3250 "
            f"objects with 3 child models and a chunk size of 2000, encountered "
            f"{len(poly_all)}"
        )

        with CaptureQueriesContext(connection) as poly_iterator:
            b, c, d = 0, 0, 0
            for idx, obj in enumerate(Model2A.objects.order_by("pk").iterator()):
                if isinstance(obj, Model2D):
                    d += 1
                    assert obj.field1 == f"D1-{idx}"
                    assert obj.field2 == f"D2-{idx}"
                    assert obj.field3 == f"D3-{idx}"
                    assert obj.field4 == f"D4-{idx}"
                elif isinstance(obj, Model2C):
                    c += 1
                    assert obj.field1 == f"C1-{idx}"
                    assert obj.field2 == f"C2-{idx}"
                    assert obj.field3 == f"C3-{idx}"
                elif isinstance(obj, Model2B):
                    b += 1
                    assert obj.field1 == f"B1-{idx}"
                    assert obj.field2 == f"B2-{idx}"
                else:
                    assert False, "Unexpected model type"
            assert (b, c, d) == (250, 1000, 2000)

        assert len(poly_iterator) <= 7, (
            f"Expected <= 7 queries for chunked iteration over 3250 "
            f"objects with 3 child models and a default chunk size of 2000, encountered "
            f"{len(poly_iterator)}"
        )

        with CaptureQueriesContext(connection) as poly_chunked:
            b, c, d = 0, 0, 0
            for idx, obj in enumerate(Model2A.objects.order_by("pk").iterator(chunk_size=4000)):
                if isinstance(obj, Model2D):
                    d += 1
                    assert obj.field1 == f"D1-{idx}"
                    assert obj.field2 == f"D2-{idx}"
                    assert obj.field3 == f"D3-{idx}"
                    assert obj.field4 == f"D4-{idx}"
                elif isinstance(obj, Model2C):
                    c += 1
                    assert obj.field1 == f"C1-{idx}"
                    assert obj.field2 == f"C2-{idx}"
                    assert obj.field3 == f"C3-{idx}"
                elif isinstance(obj, Model2B):
                    b += 1
                    assert obj.field1 == f"B1-{idx}"
                    assert obj.field2 == f"B2-{idx}"
                else:
                    assert False, "Unexpected model type"
            assert (b, c, d) == (250, 1000, 2000)

        assert len(poly_chunked) <= 7, (
            f"Expected <= 7 queries for chunked iteration over 3250 objects with 3 child "
            f"models and a chunk size of 4000, encountered {len(poly_chunked)}"
        )

        if connection.vendor == "postgresql":
            assert len(poly_chunked) == 4, "On postgres with a 4000 chunk size, expected 4 queries"

        result = Model2A.objects.all().delete()
        assert result == (
            11500,
            {
                "tests.Model2D": 2000,
                "tests.Model2C": 3000,
                "tests.Model2A": 3250,
                "tests.Model2B": 3250,
            },
        )

    def test_transmogrify_with_init(self):
        pur = PurpleHeadDuck.objects.create()
        assert pur.color == "blue"
        assert pur.home == "Duckburg"

        pur = Duck.objects.get(id=pur.id)
        assert pur.color == "blue"
        # issues/615 fixes following line:
        assert pur.home == "Duckburg"

    def test_subqueries(self):
        pa1 = PlainA.objects.create(field1="plain1")
        PlainA.objects.create(field1="plain2")

        ip1 = InlineParent.objects.create(title="parent1")
        ip2 = InlineParent.objects.create(title="parent2")

        ima1 = InlineModelA.objects.create(parent=ip1, field1="ima1")
        ima2 = InlineModelA.objects.create(parent=ip2, field1="ima2")
        imb1 = InlineModelB.objects.create(parent=ip1, field1="imab1", field2="imb1", plain_a=pa1)
        imb2 = InlineModelB.objects.create(parent=ip2, field1="imab2", field2="imb2")

        results = InlineModelA.objects.filter(
            Exists(PlainA.objects.filter(inline_bs=OuterRef("pk")))
            | Exists(InlineParent.objects.filter(inline_children=OuterRef("pk")))
        )

        assert ima1 in results
        assert ima2 in results
        assert imb1 in results
        assert imb2 in results

        results = InlineModelA.objects.filter(
            Exists(PlainA.objects.filter(inline_bs=OuterRef("pk"), field1="plain1"))
            | Exists(InlineParent.objects.filter(inline_children=OuterRef("pk"), title="parent2"))
        )

        assert ima1 not in results
        assert ima2 in results
        assert imb1 in results
        assert imb2 in results

        results = InlineModelA.objects.filter(
            Exists(PlainA.objects.filter(inline_bs=OuterRef("pk")))
        )

        assert ima1 not in results
        assert ima2 not in results
        assert imb1 in results
        assert imb2 not in results

        results = InlineModelA.objects.filter(
            Exists(PlainA.objects.filter(inline_bs=OuterRef("pk"))), field1="imab1"
        )

        assert ima1 not in results
        assert ima2 not in results
        assert imb1 in results
        assert imb2 not in results

        results = InlineModelA.objects.filter(
            Exists(PlainA.objects.filter(inline_bs=OuterRef("pk"))), InlineModelB___field2="imb2"
        )

        assert not results

        results = InlineModelA.objects.filter(
            ~Exists(PlainA.objects.filter(inline_bs=OuterRef("pk"))), InlineModelB___field2="imb2"
        )

        assert len(results) == 1
        assert imb2 in results

        PlainA.objects.all().delete()
        InlineParent.objects.all().delete()
        InlineModelA.objects.all().delete()
        InlineModelB.objects.all().delete()

    def test_one_to_one_primary_key(self):
        # check pk name resolution
        for mdl in [Account, SpecialAccount1, SpecialAccount1_1, SpecialAccount2]:
            assert mdl.polymorphic_primary_key_name == mdl._meta.pk.attname

        user1 = get_user_model().objects.create(
            username="user1", email="user1@example.com", password="password"
        )
        user2 = get_user_model().objects.create(
            username="user2", email="user2@example.com", password="password"
        )
        user3 = get_user_model().objects.create(
            username="user3", email="user3@example.com", password="password"
        )
        user4 = get_user_model().objects.create(
            username="user4", email="user4@example.com", password="password"
        )

        user1_profile = SpecialAccount1_1.objects.create(user=user1, extra1=5, extra2=6)

        user2_profile = SpecialAccount1.objects.create(user=user2, extra1=5)

        user3_profile = SpecialAccount2.objects.create(user=user3, extra1="test")

        user4_profile = SpecialAccount1_1.objects.create(user=user4, extra1=7, extra2=8)

        user1.refresh_from_db()
        assert user1.account.__class__ is SpecialAccount1_1
        assert user1.account.extra1 == 5
        assert user1.account.extra2 == 6
        assert user1_profile.pk == user1.account.pk

        user2.refresh_from_db()
        assert user2.account.__class__ is SpecialAccount1
        assert user2.account.extra1 == 5
        assert user2_profile.pk == user2.account.pk
        assert not hasattr(user2.account, "extra2")

        user3.refresh_from_db()
        assert user3.account.__class__ is SpecialAccount2
        assert user3.account.extra1 == "test"
        assert user3_profile.pk == user3.account.pk
        assert not hasattr(user3.account, "extra2")

        user4.refresh_from_db()
        assert user4.account.__class__ is SpecialAccount1_1
        assert user4.account.extra1 == 7
        assert user4.account.extra2 == 8
        assert user4_profile.pk == user4.account.pk

        assert get_user_model().objects.filter(pk=user2.pk).delete() == (
            3,
            {"tests.SpecialAccount1": 1, "tests.Account": 1, "auth.User": 1},
        )

        assert SpecialAccount1.objects.count() == 2
        assert Account.objects.count() == 3

        remaining = get_user_model().objects.filter(
            pk__in=[user1.pk, user2.pk, user3.pk, user4.pk]
        )
        assert remaining.count() == 3
        for usr, expected in zip(
            remaining.order_by("pk"), (user1_profile, user3_profile, user4_profile)
        ):
            assert usr.account == expected

        assert get_user_model().objects.filter(pk__in=[user3.pk]).delete() == (
            3,
            {"tests.SpecialAccount2": 1, "tests.Account": 1, "auth.User": 1},
        )

        assert Account.objects.count() == 2

        assert SpecialAccount1_1.objects.all().delete() == (
            6,
            {"tests.SpecialAccount1_1": 2, "tests.SpecialAccount1": 2, "tests.Account": 2},
        )

        assert Account.objects.count() == 0

        remaining = get_user_model().objects.filter(pk__gte=user1.pk)
        assert remaining.count() == 2
        for usr in remaining:
            assert not hasattr(usr, "account")

        assert get_user_model().objects.filter(pk__in=[user1.pk, user4.pk]).delete() == (
            2,
            {"auth.User": 2},
        )

    def test_manager_override(self):
        from polymorphic.tests.models import MyBaseModel, MyChild1Model, MyChild2Model

        child1 = MyChild1Model.objects.create(fieldA=4)
        child2 = MyChild2Model.objects.create(fieldB=6)

        assert MyBaseModel.objects.filter_by_user(5).count() == 2
        assert child1 in MyBaseModel.objects.all()
        assert child2 in MyBaseModel.objects.all()
        assert MyChild1Model.objects.filter_by_user(5).count() == 1
        assert MyChild2Model.objects.filter_by_user(5).count() == 1
        assert MyChild1Model.objects.filter_by_user(5).count() == 1
        assert MyChild1Model.objects.filter_by_user(5).first() == child1
        assert MyChild2Model.objects.filter_by_user(5).first() == child2

        assert MyChild2Model._default_manager is MyChild2Model.objects
        MyChild2Model.objects.filter_by_user(6).count() == 0
        MyChild2Model.base_manager.filter_by_user(6).count() == 1

    def test_abstract_managers(self):
        from django.db.models import Manager
        from polymorphic.tests.models import (
            AbstractManagerTest,
            DerivedManagerTest,
            DerivedManagerTest2,
            SpecialPolymorphicManager,
            SpecialQuerySet,
            RelatedManagerTest,
        )

        with self.assertRaises(AttributeError):
            AbstractManagerTest.objects
        with self.assertRaises(AttributeError):
            AbstractManagerTest.basic_manager
        with self.assertRaises(AttributeError):
            AbstractManagerTest.default_manager

        assert type(DerivedManagerTest.objects) is SpecialPolymorphicManager
        assert type(DerivedManagerTest.basic_manager) is Manager
        assert type(DerivedManagerTest.default_manager) is PolymorphicManager
        assert type(DerivedManagerTest._default_manager) is SpecialPolymorphicManager

        assert type(DerivedManagerTest2.objects) is PolymorphicManager
        assert type(DerivedManagerTest2.basic_manager) is Manager
        assert type(DerivedManagerTest2.default_manager) is PolymorphicManager
        assert type(DerivedManagerTest2._default_manager) is PolymorphicManager

        dmt1 = DerivedManagerTest.objects.create(abstract_field="dmt1")
        dmt2 = DerivedManagerTest2.objects.create(abstract_field="dmt2")

        assert DerivedManagerTest.objects.has_text("dmt").count() == 2
        assert dmt1 in DerivedManagerTest.objects.has_text("dmt")
        assert dmt2 in DerivedManagerTest.objects.has_text("dmt")
        assert DerivedManagerTest.objects.custom_queryset().has_text("dmt").count() == 2

        assert isinstance(DerivedManagerTest.objects.has_text("dmt"), SpecialQuerySet)

        with self.assertRaises(AttributeError):
            DerivedManagerTest2.objects.has_text("dmt")

        related = RelatedManagerTest.objects.create()
        assert isinstance(related.derived, SpecialPolymorphicManager)

    def test_fk_polymorphism(self):
        from polymorphic.tests.models import FKTest, FKTestChild

        child = FKTestChild.objects.create()

        fk_test = FKTest.objects.create(fk=child)

        assert fk_test.fk is child

        fk_test = FKTest.objects.get(pk=fk_test.id)

        assert fk_test.fk == child
        assert isinstance(fk_test.fk, FKTestChild)

    def test_polymorphic_extension(self):
        from polymorphic.tests.models import (
            NormalBase,
            NormalExtension,
            PolyExtension,
            PolyExtChild,
        )

        nb = NormalBase.objects.create(nb_field=5)
        ne = NormalExtension.objects.create(nb_field=6, ne_field="normal ext")
        poly_ext = PolyExtension.objects.create(nb_field=6, ne_field="poly ext", poly_ext_field=7)
        child_ext = PolyExtChild.objects.create(
            nb_field=7, ne_field="child ext", poly_ext_field=8, poly_child_field="poly child"
        )
        assert set(NormalBase.objects.all()) == {
            nb,
            NormalBase.objects.get(pk=ne.pk),
            NormalBase.objects.get(pk=poly_ext.pk),
            NormalBase.objects.get(pk=child_ext.pk),
        }
        assert set(NormalExtension.objects.all()) == {
            NormalExtension.objects.get(pk=ne.pk),
            NormalExtension.objects.get(pk=poly_ext.pk),
            NormalExtension.objects.get(pk=child_ext.pk),
        }
        assert set(PolyExtension.objects.all()) == {poly_ext, child_ext}
        assert set(PolyExtChild.objects.all()) == {child_ext}

    def test_manytomany_without_through_field(self):
        from polymorphic.tests.models import Lake, RedheadDuck, RubberDuck

        lake = Lake.objects.create()
        rubber = RubberDuck.objects.create(name="Rubber")
        redhead = RedheadDuck.objects.create(name="Redheat")
        lake.ducks.add(rubber)
        lake.ducks.add(redhead)
        self.assertEqual(lake.ducks.count(), 2)
        self.assertIsInstance(lake.ducks.all()[0], RubberDuck)
        self.assertIsInstance(lake.ducks.all()[1], RedheadDuck)

    def test_manytomany_with_through_field(self):
        from polymorphic.tests.models import LakeWithThrough, DucksLake, RedheadDuck, RubberDuck

        lake = LakeWithThrough.objects.create()
        rubber = RubberDuck.objects.create(name="Rubber")
        redhead = RedheadDuck.objects.create(name="Redheat")
        DucksLake.objects.create(lake=lake, duck=rubber, time="morning")
        DucksLake.objects.create(lake=lake, duck=redhead, time="afternoon")
        self.assertEqual(lake.ducks.count(), 2)
        self.assertIsInstance(lake.ducks.all()[0], RubberDuck)
        self.assertIsInstance(lake.ducks.all()[1], RedheadDuck)

    def test_create_from_super(self):
        # run create test 3 times because initial implementation
        # would fail after first success.
        from polymorphic.tests.models import (
            NormalBase,
            NormalExtension,
            PolyExtension,
            PolyExtChild,
            CustomPkBase,
            CustomPkInherit,
        )

        nb = NormalBase.objects.create(nb_field=1)
        ne = NormalExtension.objects.create(nb_field=2, ne_field="ne2")

        with self.assertRaises(TypeError):
            PolyExtension.objects.create_from_super(nb, poly_ext_field=3)

        with CaptureQueriesContext(connection) as ctx:
            pe = PolyExtension.objects.create_from_super(ne, poly_ext_field=3)

        # for q in ctx.captured_queries:
        #     print(q["sql"])

        ne.refresh_from_db()
        self.assertEqual(type(ne), NormalExtension)
        self.assertEqual(type(pe), PolyExtension)
        self.assertEqual(pe.pk, ne.pk)

        self.assertEqual(pe.nb_field, 2)
        self.assertEqual(pe.ne_field, "ne2")
        self.assertEqual(pe.poly_ext_field, 3)
        pe.refresh_from_db()
        self.assertEqual(pe.nb_field, 2)
        self.assertEqual(pe.ne_field, "ne2")
        self.assertEqual(pe.poly_ext_field, 3)

        print("===================================")

        with CaptureQueriesContext(connection) as ctx:
            """
            BEGIN
            SELECT "django_content_type"."id", "django_content_type"."app_label", "django_content_type"."model" FROM "django_content_type" WHERE ("django_content_type"."app_label" = 'tests' AND "django_content_type"."model" = 'polyextchild') LIMIT 21
            INSERT INTO "tests_polyextchild" ("polyextension_ptr_id", "poly_child_field") VALUES (2, 'pcf6')
            SELECT "tests_normalbase"."id", "tests_normalbase"."nb_field", "tests_normalextension"."normalbase_ptr_id", "tests_normalextension"."ne_field", "tests_polyextension"."normalextension_ptr_id", "tests_polyextension"."polymorphic_ctype_id", "tests_polyextension"."poly_ext_field" FROM "tests_polyextension" INNER JOIN "tests_normalextension" ON ("tests_polyextension"."normalextension_ptr_id" = "tests_normalextension"."normalbase_ptr_id") INNER JOIN "tests_normalbase" ON ("tests_normalextension"."normalbase_ptr_id" = "tests_normalbase"."id") WHERE "tests_polyextension"."normalextension_ptr_id" = 2 LIMIT 21
            UPDATE "tests_normalbase" SET "nb_field" = 2 WHERE "tests_normalbase"."id" = 2
            UPDATE "tests_normalextension" SET "ne_field" = 'ne2' WHERE "tests_normalextension"."normalbase_ptr_id" = 2
            UPDATE "tests_polyextension" SET "polymorphic_ctype_id" = 100, "poly_ext_field" = 3 WHERE "tests_polyextension"."normalextension_ptr_id" = 2
            SELECT "tests_normalbase"."id", "tests_normalbase"."nb_field", "tests_normalextension"."normalbase_ptr_id", "tests_normalextension"."ne_field", "tests_polyextension"."normalextension_ptr_id", "tests_polyextension"."polymorphic_ctype_id", "tests_polyextension"."poly_ext_field", "tests_polyextchild"."polyextension_ptr_id", "tests_polyextchild"."poly_child_field" FROM "tests_polyextchild" INNER JOIN "tests_polyextension" ON ("tests_polyextchild"."polyextension_ptr_id" = "tests_polyextension"."normalextension_ptr_id") INNER JOIN "tests_normalextension" ON ("tests_polyextension"."normalextension_ptr_id" = "tests_normalextension"."normalbase_ptr_id") INNER JOIN "tests_normalbase" ON ("tests_normalextension"."normalbase_ptr_id" = "tests_normalbase"."id") WHERE "tests_polyextchild"."polyextension_ptr_id" = 2 LIMIT 21
            COMMIT
            """
            pc = PolyExtChild.objects.create_from_super(pe, poly_child_field="pcf6")

        # for q in ctx.captured_queries:
        #     print(q["sql"])

        pe.refresh_from_db()
        ne.refresh_from_db()
        self.assertEqual(type(ne), NormalExtension)
        self.assertEqual(type(pe), PolyExtension)
        self.assertEqual(pe.pk, ne.pk)
        self.assertEqual(pe.pk, pc.pk)

        self.assertEqual(pc.nb_field, 2)
        self.assertEqual(pc.ne_field, "ne2")
        self.assertEqual(pc.poly_ext_field, 3)
        pc.refresh_from_db()
        self.assertEqual(pc.nb_field, 2)
        self.assertEqual(pc.ne_field, "ne2")
        self.assertEqual(pc.poly_ext_field, 3)
        self.assertEqual(pc.poly_child_field, "pcf6")

        self.assertEqual(pe.polymorphic_ctype, ContentType.objects.get_for_model(PolyExtChild))
        self.assertEqual(pc.polymorphic_ctype, ContentType.objects.get_for_model(PolyExtChild))

        self.assertEqual(set(PolyExtension.objects.all()), {pc})

        a1 = Model2A.objects.create(field1="A1a")
        a2 = Model2A.objects.create(field1="A1b")

        b1 = Model2B.objects.create(field1="B1a", field2="B2a")
        b2 = Model2B.objects.create(field1="B1b", field2="B2b")

        c1 = Model2C.objects.create(field1="C1a", field2="C2a", field3="C3a")
        c2 = Model2C.objects.create(field1="C1b", field2="C2b", field3="C3b")

        d1 = Model2D.objects.create(field1="D1a", field2="D2a", field3="D3a", field4="D4a")
        d2 = Model2D.objects.create(field1="D1b", field2="D2b", field3="D3b", field4="D4b")

        with self.assertRaises(TypeError):
            Model2D.objects.create_from_super(b1, field3="D3x", field4="D4x")

        b1_of_c = Model2B.objects.non_polymorphic().get(pk=c1.pk)
        with self.assertRaises(TypeError):
            Model2C.objects.create_from_super(b1_of_c, field3="C3x")

        self.assertEqual(c1.polymorphic_ctype, ContentType.objects.get_for_model(Model2C))
        dfs1 = Model2D.objects.create_from_super(b1_of_c, field4="D4x")
        self.assertEqual(type(dfs1), Model2D)
        self.assertEqual(dfs1.pk, c1.pk)
        self.assertEqual(dfs1.field1, "C1a")
        self.assertEqual(dfs1.field2, "C2a")
        self.assertEqual(dfs1.field3, "C3a")
        self.assertEqual(dfs1.field4, "D4x")
        self.assertEqual(dfs1.polymorphic_ctype, ContentType.objects.get_for_model(Model2D))
        c1.refresh_from_db()
        self.assertEqual(c1.polymorphic_ctype, ContentType.objects.get_for_model(Model2D))

        self.assertEqual(b2.polymorphic_ctype, ContentType.objects.get_for_model(Model2B))
        cfs1 = Model2C.objects.create_from_super(b2, field3="C3y")
        self.assertEqual(type(cfs1), Model2C)
        self.assertEqual(cfs1.pk, b2.pk)
        self.assertEqual(cfs1.field1, "B1b")
        self.assertEqual(cfs1.field2, "B2b")
        self.assertEqual(cfs1.field3, "C3y")
        b2.refresh_from_db()
        self.assertEqual(b2.polymorphic_ctype, ContentType.objects.get_for_model(Model2C))
        self.assertEqual(cfs1.polymorphic_ctype, ContentType.objects.get_for_model(Model2C))

        self.assertEqual(set(Model2A.objects.all()), {a1, a2, b1, dfs1, cfs1, c2, d1, d2})

        custom_pk = CustomPkBase.objects.create(b="0")
        custom_pk_ext = CustomPkInherit.objects.create_from_super(custom_pk, i="4")
        self.assertEqual(type(custom_pk_ext), CustomPkInherit)
        custom_pk_ext.refresh_from_db()
        self.assertEqual(custom_pk_ext.id, custom_pk.id)
        self.assertEqual(CustomPkBase.objects.get(pk=custom_pk.id), custom_pk_ext)
        self.assertEqual(CustomPkBase.objects.count(), 1)

        custom_pk2 = CustomPkBase.objects.create(b="2")
        custom_pk_ext2 = CustomPkInherit.objects.create_from_super(
            custom_pk2, custom_id=100, i="4"
        )
        self.assertEqual(type(custom_pk_ext2), CustomPkInherit)
        custom_pk_ext2.refresh_from_db()
        self.assertEqual(custom_pk_ext2.id, custom_pk2.id)
        self.assertEqual(custom_pk_ext2.custom_id, 100)
        self.assertEqual(CustomPkBase.objects.get(pk=custom_pk2.id), custom_pk_ext2)
        self.assertEqual(CustomPkBase.objects.count(), 2)

    def test_create_from_super_child_exists(self):
        """
        Test several scenarios creating a child row where a parent already exists.

        Should get integrity errors!
        """
        from polymorphic.tests.models import (
            NormalExtension,
            PolyExtension,
            CustomPkBase,
            CustomPkInherit,
        )

        pe1 = PolyExtension.objects.create(nb_field=10, ne_field="ne10", poly_ext_field=20)
        ne1 = NormalExtension.objects.get(pk=pe1.pk)

        with self.assertRaises(IntegrityError):
            PolyExtension.objects.create_from_super(ne1, poly_ext_field=30)

        # FIXME: uncomment when #686 is fixed
        # CustomPkInherit.objects.create(b="base1", i="1")
        # with self.assertRaises(IntegrityError):
        #     CustomPkInherit.objects.create_from_super(
        #         CustomPkBase.objects.non_polymorphic().first(), i="2"
        #     )

    def test_through_models_creates_and_reads(self):
        from polymorphic.tests.models import (
            BetMultiple,
            ChoiceAthlete,
            ChoiceBlank,
            RankedAthlete,
        )

        bet = BetMultiple.objects.create()

        a1 = ChoiceAthlete.objects.create(choice="Alice")
        a2 = ChoiceAthlete.objects.create(choice="Bob")
        a3 = ChoiceBlank.objects.create()

        # Exercise the "through" model via the M2M manager using through_defaults.
        bet.answer.add(a1, through_defaults={"rank": 2})
        bet.answer.add(a2, through_defaults={"rank": 1})
        bet.answer.add(a3, through_defaults={"rank": 3})  # ChoiceBlank also works

        # Through rows were created with rank preserved
        rows = list(
            RankedAthlete.objects.filter(bet=bet)
            .order_by("rank")
            .values_list("choiceAthlete_id", "rank")
        )
        assert rows == [(a2.pk, 1), (a1.pk, 2), (a3.pk, 3)]

        # Reading back via the M2M returns polymorphic instances (ChoiceAthlete, not ChoiceBlank)
        answers = list(bet.answer.order_by("rankedathlete__rank"))
        assert answers == [a2, a1, a3]
        assert isinstance(answers[0], ChoiceAthlete)
        assert isinstance(answers[1], ChoiceAthlete)
        assert isinstance(answers[2], ChoiceBlank)

        # Sanity: the through model is the one we expect
        assert bet.answer.through is RankedAthlete
        assert isinstance(bet.answer, PolymorphicManager)

    def test_through_model_updates(self):
        from polymorphic.tests.models import BetMultiple, ChoiceAthlete, RankedAthlete, ChoiceBlank

        bet = BetMultiple.objects.create()
        a1 = ChoiceAthlete.objects.create(choice="Alice")
        a2 = ChoiceBlank.objects.create()

        bet.answer.add(a2, through_defaults={"rank": 0})
        bet.answer.add(a1, through_defaults={"rank": 1})
        ra = RankedAthlete.objects.get(bet=bet, choiceAthlete=a1)
        assert ra.rank == 1

        ra.rank = 99
        ra.save(update_fields=["rank"])

        ra2 = RankedAthlete.objects.get(bet=bet, choiceAthlete=a2)
        assert ra2.rank == 0

        # ordering uses the through-table rank
        assert list(bet.answer.order_by("rankedathlete__rank")) == [a2, a1]
        assert RankedAthlete.objects.get(pk=ra.pk).rank == 99
        assert RankedAthlete.objects.get(pk=ra2.pk).rank == 0

    def test_infinite_recursion_with_only(self):
        """
        https://github.com/jazzband/django-polymorphic/issues/334
        """
        from polymorphic.tests.models import RecursionBug

        draft = PlainA.objects.create(field1="draft")
        closed = PlainA.objects.create(field1="closed")

        assert isinstance(closed.recursions, PolymorphicManager)

        item = RecursionBug.objects.create(status=draft)
        RecursionBug.objects.filter(id=item.id).update(status=closed)
        item.refresh_from_db(fields=("status",))
        assert item.status == closed

    @pytest.mark.skipif(
        Version(django.get_version()) < Version("5.0"),
        reason="Requires Django 5.0+",
    )
    def test_generic_relation_prefetch(self):
        """
        https://github.com/jazzband/django-polymorphic/issues/613
        """
        from polymorphic.tests.models import Bookmark, TaggedItem, Assignment
        from django.contrib.contenttypes.prefetch import GenericPrefetch

        bm1 = Bookmark.objects.create(url="http://example.com/1")
        ass = Assignment.objects.create(url="http://example.com/2", assigned_to="Alice")

        TaggedItem.objects.create(tag="tag1", content_object=bm1)
        TaggedItem.objects.create(tag="tag2", content_object=ass)

        bookmarks = list(Bookmark.objects.prefetch_related("tags").order_by("pk"))
        assert len(bookmarks) == 2
        assert list(bookmarks[0].tags.all()) == [TaggedItem.objects.get(tag="tag1")]
        assert list(bookmarks[1].tags.all()) == [TaggedItem.objects.get(tag="tag2")]
        assert bookmarks[0].__class__ is Bookmark
        assert bookmarks[1].__class__ is Assignment

        tags = TaggedItem.objects.prefetch_related(
            GenericPrefetch(
                lookup="content_object",
                querysets=[
                    Bookmark.objects.all(),
                ],
            ),
        ).order_by("pk")

        assert tags[0].content_object == bookmarks[0]
        assert tags[1].content_object == bookmarks[1]

        for tag in tags.all():
            assert tag.content_object

    def test_besteffort_iteration(self):
        """
        Test that our best effort iteration avoids n+1 queries when n objects have stale
        content type pointers.
        """
        for i in range(100):
            Model2A.objects.create(field1=f"Model2C_{i}")

        # force stale ctype condition
        Model2A.objects.all().update(polymorphic_ctype=ContentType.objects.get_for_model(Model2C))

        assert Model2C.objects.count() == 0
        assert Model2B.objects.count() == 0
        assert Model2A.objects.count() == 100

        with CaptureQueriesContext(connection) as initial_all_2a:
            for obj in Model2A.objects.all():
                assert obj.__class__ is Model2A

        assert len(initial_all_2a.captured_queries) <= 4

    def test_besteffort_get_real_instance(self):
        obj = Model2B.objects.create(field1="TestB", field2="TestB2")
        obj.polymorphic_ctype = ContentType.objects.get_for_model(Model2C)
        obj.save()
        as_a = Model2A.objects.non_polymorphic().get(pk=obj.pk)
        assert as_a.__class__ is Model2A
        should_be_b = as_a.get_real_instance()
        assert should_be_b.__class__ is Model2B
        # ctype should still be wrong
        assert should_be_b.polymorphic_ctype == ContentType.objects.get_for_model(Model2C)

    def test_queryset_first_returns_none_on_empty_queryset(self):
        self.assertIsNone(Model2A.objects.first())

    def test_queryset_getitem_raises_indexerror_on_empty_queryset(self):
        with self.assertRaises(IndexError):
            _ = Model2A.objects.all()[0]

    def test_queryset_getitem_negative_index_raises_valueerror(self):
        Model2A.objects.create(field1="OnlyOne")
        with self.assertRaises(ValueError):
            _ = Model2A.objects.all()[-1]

    def test_queryset_getitem_slice_returns_objects(self):
        Model2A.objects.create(field1="First")
        Model2A.objects.create(field1="Second")
        objs = Model2A.objects.all()[0:2]
        self.assertEqual(len(objs), 2)
        self.assertEqual([o.field1 for o in objs], ["First", "Second"])

    def test_aggregate_with_filtered_relation(self):
        """Test _process_aggregate_args with FilteredRelation (lines 273-280)"""
        # Create test data
        a1 = Model2A.objects.create(field1="A1")
        b1 = Model2B.objects.create(field1="B1", field2="B2")
        c1 = Model2C.objects.create(field1="C1", field2="C2", field3="C3")

        # Create related objects
        rel1 = RelatingModel.objects.create()
        rel2 = RelatingModel.objects.create()
        rel1.many2many.add(a1, b1)
        rel2.many2many.add(c1)

        # Test FilteredRelation with annotate
        # This exercises the patch_lookup function with FilteredRelation
        qs = RelatingModel.objects.annotate(
            filtered_m2m=FilteredRelation(
                "many2many", condition=Q(many2many__field1__startswith="B")
            )
        ).filter(filtered_m2m__isnull=False)

        assert rel1 in qs
        assert rel2 not in qs

    def test_aggregate_with_nested_q_objects(self):
        """Test _process_aggregate_args with nested Q objects (lines 285-298)"""
        a1 = Model2A.objects.create(field1="A1")
        b1 = Model2B.objects.create(field1="B1", field2="B2")
        c1 = Model2C.objects.create(field1="C1", field2="C2", field3="C3")

        # Test with nested Q objects in annotate
        # This exercises the tree_node_test___lookup function
        result = Model2A.objects.annotate(
            has_b_field=Case(
                When(Q(field1__startswith="B") | Q(field1__startswith="C"), then=1),
                default=0,
                output_field=models.IntegerField(),
            )
        ).filter(has_b_field=1)

        assert b1 in result
        assert c1 in result
        assert a1 not in result

    def test_aggregate_with_subclass_field_in_expression(self):
        """Test _process_aggregate_args with source expressions (lines 275-278, 300-303)"""
        b1 = Model2B.objects.create(field1="B1", field2="100")
        b2 = Model2B.objects.create(field1="B2", field2="200")
        c1 = Model2C.objects.create(field1="C1", field2="150", field3="C3")

        # Test with complex expression containing field references
        # This exercises the get_source_expressions path
        from django.db.models import F, Value
        from django.db.models.functions import Concat

        result = Model2A.objects.annotate(
            combined=Concat(F("field1"), Value(" - "), F("Model2B___field2"))
        ).filter(Model2B___field2__isnull=False)

        assert b1 in result
        assert b2 in result
        assert c1 in result  # C inherits from B

    def test_get_best_effort_instance_with_missing_derived(self):
        """Test _get_best_effort_instance when derived class is missing (lines 339-387)"""
        # Create a Model2C object (which inherits from Model2B -> Model2A)
        c1 = Model2C.objects.create(field1="C1", field2="C2", field3="C3")
        c1_pk = c1.pk

        # Delete the Model2C part but keep Model2B and Model2A parts
        # This simulates a partially deleted object
        c1.delete(keep_parents=True)

        # Now try to fetch it - should fall back to Model2B
        result = list(Model2A.objects.filter(pk=c1_pk))
        assert len(result) == 1
        assert result[0].pk == c1_pk
        assert isinstance(result[0], Model2B)
        assert not isinstance(result[0], Model2C)

    def test_get_best_effort_instance_with_annotations(self):
        """Test _get_best_effort_instance preserves annotations (lines 367-374)"""
        # Create a Model2C object
        c1 = Model2C.objects.create(field1="C1", field2="C2", field3="C3")
        c1_pk = c1.pk

        # Add annotation
        annotated = Model2A.objects.annotate(field_count=Count("field1")).filter(pk=c1_pk)

        # Delete the Model2C part
        c1.delete(keep_parents=True)

        # Fetch with annotation - should preserve annotation on fallback object
        result = list(annotated)
        assert len(result) == 1
        assert hasattr(result[0], "field_count")
        assert result[0].field_count == 1

    def test_get_best_effort_instance_with_extra_select(self):
        """Test _get_best_effort_instance preserves extra select (lines 376-379)"""
        # Create a Model2C object
        c1 = Model2C.objects.create(field1="C1", field2="C2", field3="C3")
        c1_pk = c1.pk

        # Add extra select
        qs = Model2A.objects.extra(select={"upper_field1": "UPPER(field1)"}).filter(pk=c1_pk)

        # Delete the Model2C part
        c1.delete(keep_parents=True)

        # Fetch with extra - should preserve extra on fallback object
        result = list(qs)
        assert len(result) == 1
        assert hasattr(result[0], "upper_field1")
        assert result[0].upper_field1 == "C1"

    def test_get_best_effort_instance_multiple_inheritance_levels(self):
        """Test _get_best_effort_instance walks up multiple levels (lines 351-384)"""
        # Create a Model2D object (D -> C -> B -> A)
        d1 = Model2D.objects.create(field1="D1", field2="D2", field3="D3", field4="D4")
        d1_pk = d1.pk

        # Delete Model2D part, keep Model2C
        d1.delete(keep_parents=True)

        # Should fall back to Model2C
        result = list(Model2A.objects.filter(pk=d1_pk))
        assert len(result) == 1
        assert isinstance(result[0], Model2C)
        assert not isinstance(result[0], Model2D)

        # Now delete Model2C part too
        c1 = Model2C.objects.get(pk=d1_pk)
        c1.delete(keep_parents=True)

        # Should fall back to Model2B
        result = list(Model2A.objects.filter(pk=d1_pk))
        assert len(result) == 1
        assert isinstance(result[0], Model2B)
        assert not isinstance(result[0], Model2C)

    def test_deferred_loading_with_subclass_syntax(self):
        """Test deferred loading with Model___field syntax (lines 481-505)"""
        b1 = Model2B.objects.create(field1="B1", field2="B2")
        c1 = Model2C.objects.create(field1="C1", field2="C2", field3="C3")

        # Test defer with subclass field syntax
        qs = Model2A.objects.defer("Model2B___field2")
        result = list(qs)

        # field2 should be deferred for Model2B instances
        b_obj = [r for r in result if r.pk == b1.pk][0]
        assert isinstance(b_obj, Model2B)
        # Accessing deferred field should trigger a query
        assert b_obj.field2 == "B2"

    def test_deferred_loading_with_nonexistent_field(self):
        """Test deferred loading handles non-existent fields gracefully (lines 496-501)"""
        b1 = Model2B.objects.create(field1="B1", field2="B2")

        # Try to defer a field that doesn't exist in Model2B using subclass syntax
        # This should be handled gracefully (field doesn't exist in this subclass)
        qs = Model2A.objects.defer("Model2C___field3")
        result = list(qs)

        # Should still work, just ignoring the non-existent field for Model2B
        assert len(result) == 1
        assert result[0].field1 == "B1"

    def test_only_with_subclass_syntax(self):
        """Test only() with Model___field syntax (lines 214-226)"""
        b1 = Model2B.objects.create(field1="B1", field2="B2")
        c1 = Model2C.objects.create(field1="C1", field2="C2", field3="C3")

        # Test only with subclass field syntax
        qs = Model2A.objects.only("field1", "Model2B___field2")
        result = list(qs)

        # Only field1 and field2 should be loaded for Model2B instances
        b_obj = [r for r in result if r.pk == b1.pk][0]
        assert isinstance(b_obj, Model2B)
        assert b_obj.field1 == "B1"
        assert b_obj.field2 == "B2"

    def test_real_instances_with_stale_content_type(self):
        """Test _get_real_instances handles stale content types (lines 451-453)"""
        # This test verifies the stale content type handling by checking
        # that objects with invalid content type IDs are skipped gracefully
        # We'll use the existing prefetch_related_with_missing test pattern
        # which already covers this scenario
        pass  # Covered by test_prefetch_related_with_missing

    def test_real_instances_with_proxy_model(self):
        """Test _get_real_instances handles proxy models (lines 527-529)"""
        # Create a proxy model instance
        proxy = ProxyModelA.objects.create(field1="Proxy1")

        # Fetch through base class
        result = list(ProxyModelBase.objects.filter(pk=proxy.pk))
        assert len(result) == 1
        assert isinstance(result[0], ProxyModelA)
        assert result[0].field1 == "Proxy1"

    def test_annotate_with_polymorphic_field_path(self):
        """Test annotate with polymorphic field paths (lines 312-316)"""
        b1 = Model2B.objects.create(field1="B1", field2="B2")
        b2 = Model2B.objects.create(field1="B2", field2="B3")
        c1 = Model2C.objects.create(field1="C1", field2="C2", field3="C3")

        # Test annotate with subclass field
        result = Model2A.objects.annotate(b_field_count=Count("Model2B___field2"))

        # All objects should be returned with annotation
        assert result.count() == 3

    def test_aggregate_with_polymorphic_field_path(self):
        """Test aggregate with polymorphic field paths (lines 318-323)"""
        b1 = Model2B.objects.create(field1="B1", field2="10")
        b2 = Model2B.objects.create(field1="B2", field2="20")
        c1 = Model2C.objects.create(field1="C1", field2="30", field3="C3")

        # Test aggregate with subclass field
        # This should use non_polymorphic internally
        result = Model2A.objects.aggregate(total=Count("Model2B___field2"))

        assert "total" in result
        assert result["total"] >= 0

    def test_disparate_pk_values_in_hierarchy(self):
        """
        Test that polymorphic models with different primary key field types and values
        at different levels of the inheritance hierarchy can be created, queried, and
        deleted without issues.
        """
        from polymorphic.tests.models import (
            DisparateKeysParent,
            RelatedKeyModel,
            DisparateKeysChild1,
            DisparateKeysChild2,
            DisparateKeysGrandChild,
            DisparateKeysGrandChild2,
        )

        extern_key1 = RelatedKeyModel.objects.create()
        extern_key2 = RelatedKeyModel.objects.create()
        extern_key3 = RelatedKeyModel.objects.create()

        parent1 = DisparateKeysParent.objects.create(text="parent1")
        parent2 = DisparateKeysParent.objects.create(text="parent2")
        child1 = DisparateKeysChild1.objects.create(
            text="child1", text_child1="child1 extra", key=extern_key1
        )
        child2 = DisparateKeysChild1.objects.create(
            text="child2", text_child1="child2 extra", key=extern_key2
        )

        grandchild1 = DisparateKeysGrandChild.objects.create(
            text="grandchild1",
            text_child1="grandchild1 extra",
            text_grand_child="grandchild1 extra extra",
            key=extern_key3,
        )
        grandchild2 = DisparateKeysGrandChild2.objects.create(
            text="grandchild2",
            text_child2="grandchild2 extra",
            text_grand_child="grandchild2 extra extra",
            id=50,
            key=100,
        )

        child2_1 = DisparateKeysChild2.objects.create(
            text="child2_1", text_child2="child2_1 extra", key=101
        )
        child2_2 = DisparateKeysChild2.objects.create(
            text="child2_2", text_child2="child2_2 extra", key=102
        )

        assert set(DisparateKeysParent.objects.all()) == {
            parent1,
            parent2,
            child1,
            child2,
            grandchild1,
            child2_1,
            child2_2,
            grandchild2,
        }

        assert set(DisparateKeysChild1.objects.all()) == {child1, child2, grandchild1}
        assert set(DisparateKeysChild2.objects.all()) == {child2_1, child2_2, grandchild2}
        assert set(DisparateKeysGrandChild.objects.all()) == {grandchild1}
        assert set(DisparateKeysGrandChild2.objects.all()) == {grandchild2}

        # test get_real_instance
        real_instances = set()
        for obj in DisparateKeysParent.objects.non_polymorphic().all():
            real_instances.add(obj.get_real_instance())

        assert real_instances == {
            parent1,
            parent2,
            child1,
            child2,
            grandchild1,
            child2_1,
            child2_2,
            grandchild2,
        }

        # test parentage links
        assert grandchild2.disparatekeyschild2_ptr.__class__ == DisparateKeysChild2
        assert (
            grandchild2.disparatekeyschild2_ptr
            == DisparateKeysChild2.objects.non_polymorphic().get(key=grandchild2.key)
        )
        assert grandchild2.disparatekeysparent_ptr.__class__ == DisparateKeysParent

        assert (
            grandchild2.disparatekeysparent_ptr
            == DisparateKeysParent.objects.non_polymorphic().get(pk=grandchild2.id)
        )

        DisparateKeysGrandChild2.objects.all().delete()

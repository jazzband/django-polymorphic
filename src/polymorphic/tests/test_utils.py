import pytest
from django.test import TransactionTestCase
from django.contrib.contenttypes.models import ContentType

from polymorphic.models import PolymorphicModel, PolymorphicTypeUndefined
from polymorphic.tests.models import (
    Enhance_Base,
    Enhance_Inherit,
    Model2A,
    Model2B,
    Model2C,
    Model2D,
)
from polymorphic.utils import (
    get_base_polymorphic_model,
    reset_polymorphic_ctype,
    sort_by_subclass,
    route_to_ancestor,
    concrete_descendants,
)


class UtilsTests(TransactionTestCase):
    def test_sort_by_subclass(self):
        assert sort_by_subclass(Model2D, Model2B, Model2D, Model2A, Model2C) == [
            Model2A,
            Model2B,
            Model2C,
            Model2D,
            Model2D,
        ]

    def test_reset_polymorphic_ctype(self):
        """
        Test the the polymorphic_ctype_id can be restored.
        """
        Model2A.objects.create(field1="A1")
        Model2D.objects.create(field1="A1", field2="B2", field3="C3", field4="D4")
        Model2B.objects.create(field1="A1", field2="B2")
        Model2B.objects.create(field1="A1", field2="B2")
        Model2A.objects.all().update(polymorphic_ctype_id=None)

        with pytest.raises(PolymorphicTypeUndefined):
            list(Model2A.objects.all())

        reset_polymorphic_ctype(Model2D, Model2B, Model2D, Model2A, Model2C)

        self.assertQuerySetEqual(
            Model2A.objects.order_by("pk"),
            [Model2A, Model2D, Model2B, Model2B],
            transform=lambda o: o.__class__,
        )

    def test_get_base_polymorphic_model(self):
        """
        Test that finding the base polymorphic model works.
        """
        # Finds the base from every level (including lowest)
        assert get_base_polymorphic_model(Model2D) is Model2A
        assert get_base_polymorphic_model(Model2C) is Model2A
        assert get_base_polymorphic_model(Model2B) is Model2A
        assert get_base_polymorphic_model(Model2A) is Model2A

        # Properly handles multiple inheritance
        assert get_base_polymorphic_model(Enhance_Inherit) is Enhance_Base

        # Ignores PolymorphicModel itself.
        assert get_base_polymorphic_model(PolymorphicModel) is None

    def test_get_base_polymorphic_model_skip_abstract(self):
        """
        Skipping abstract models that can't be used for querying.
        """

        class A(PolymorphicModel):
            class Meta:
                abstract = True

        class B(A):
            pass

        class C(B):
            pass

        assert get_base_polymorphic_model(A) is None
        assert get_base_polymorphic_model(B) is B
        assert get_base_polymorphic_model(C) is B

        assert get_base_polymorphic_model(C, allow_abstract=True) is A

    def test_concrete_descendants(self):
        """
        Test that finding concrete descendants works.
        """
        from .models import (
            Model2A,
            Model2B,
            Model2C,
            Model2D,
            ModelWithMyManager,
            ModelWithMyManagerNoDefault,
            ModelWithMyManagerDefault,
            ModelWithMyManager2,
            Base,
            ModelX,
            ModelY,
            BlogBase,
            BlogA,
            BlogB,
            RelationBase,
            RelationA,
            RelationB,
            RelationBC,
            ProxyBase,
            NonProxyChild,
            ProxiedBase,
            ProxyModelA,
            ProxyModelB,
            ProxyModelBase,
            CustomPkBase,
            CustomPkInherit,
            MultiTableBase,
            MultiTableDerived,
            FKTestChild,
            Model2BFiltered,
            Model2CFiltered,
            Model2CNamedDefault,
            Model2CNamedManagers,
        )

        # Model2A hierarchy (with manager variants)
        assert concrete_descendants(Model2A) == [
            Model2B,
            Model2C,
            Model2D,
            Model2BFiltered,
            Model2CFiltered,
            Model2CNamedManagers,
            Model2CNamedDefault,
            ModelWithMyManager,
            ModelWithMyManagerNoDefault,
            ModelWithMyManagerDefault,
            ModelWithMyManager2,
        ]
        assert concrete_descendants(Model2B) == [
            Model2C,
            Model2D,
            Model2BFiltered,
            Model2CFiltered,
            Model2CNamedManagers,
            Model2CNamedDefault,
        ]
        assert concrete_descendants(Model2C) == [Model2D]
        assert len(concrete_descendants(Model2D)) == 0

        # ModelWithMyManager variants (no further descendants)
        assert len(concrete_descendants(ModelWithMyManager)) == 0
        assert len(concrete_descendants(ModelWithMyManagerNoDefault)) == 0
        assert len(concrete_descendants(ModelWithMyManagerDefault)) == 0
        assert len(concrete_descendants(ModelWithMyManager2)) == 0

        # Base hierarchy (tree order: ModelX defined before ModelY)
        assert concrete_descendants(Base) == [ModelX, ModelY, FKTestChild]
        assert len(concrete_descendants(ModelX)) == 0
        assert len(concrete_descendants(ModelY)) == 0

        # BlogBase hierarchy (tree order: BlogA defined before BlogB)
        assert concrete_descendants(BlogBase) == [BlogA, BlogB]
        assert len(concrete_descendants(BlogA)) == 0
        assert len(concrete_descendants(BlogB)) == 0

        # RelationBase hierarchy (tree order: RelationA before RelationB, RelationBC is child of RelationB)
        assert concrete_descendants(RelationBase) == [
            RelationA,
            RelationB,
            RelationBC,
        ]
        assert len(concrete_descendants(RelationA)) == 0
        assert concrete_descendants(RelationB) == [RelationBC]
        assert len(concrete_descendants(RelationBC)) == 0

        # ProxyBase hierarchy (ProxyChild is proxy, so excluded)
        assert concrete_descendants(ProxyBase) == [NonProxyChild]
        assert len(concrete_descendants(NonProxyChild)) == 0

        # ProxiedBase hierarchy (tree order: ProxyModelA defined before ProxyModelB)
        # ProxyModelBase is proxy, but has concrete children
        assert concrete_descendants(ProxiedBase) == [ProxyModelA, ProxyModelB]
        # ProxyModelBase is proxy but should still return its concrete descendants
        assert concrete_descendants(ProxyModelBase) == [ProxyModelA, ProxyModelB]
        assert len(concrete_descendants(ProxyModelA)) == 0
        assert len(concrete_descendants(ProxyModelB)) == 0

        # CustomPkBase hierarchy
        assert concrete_descendants(CustomPkBase) == [CustomPkInherit]
        assert len(concrete_descendants(CustomPkInherit)) == 0

        # MultiTableBase hierarchy
        assert concrete_descendants(MultiTableBase) == [MultiTableDerived]
        assert len(concrete_descendants(MultiTableDerived)) == 0

        # Enhance_Base hierarchy
        assert concrete_descendants(Enhance_Base) == [Enhance_Inherit]
        assert len(concrete_descendants(Enhance_Inherit)) == 0

    def test_route_to_ancestor(self):
        """
        Test that finding routes to ancestors works correctly.
        """
        from .models import (
            Model2A,
            Model2B,
            Model2C,
            Model2D,
            Base,
            ModelX,
            ModelY,
            BlogBase,
            BlogA,
            RelationBase,
            RelationA,
            RelationB,
            RelationBC,
            Enhance_Base,
            Enhance_Inherit,
            PurpleHeadDuck,
            Duck,
        )

        # Test direct parent (one hop)
        route = route_to_ancestor(Model2B, Model2A)
        assert len(route) == 1
        assert route[0].model == Model2A
        assert route[0].link.name == "model2a_ptr"

        # Test grandparent (two hops)
        route = route_to_ancestor(Model2C, Model2A)
        assert len(route) == 2
        assert route[0].model == Model2B
        assert route[0].link.name == "model2b_ptr"
        assert route[1].model == Model2A
        assert route[1].link.name == "model2a_ptr"

        # Test great-grandparent (three hops)
        route = route_to_ancestor(Model2D, Model2A)
        assert len(route) == 3
        assert route[0].model == Model2C
        assert route[0].link.name == "model2c_ptr"
        assert route[1].model == Model2B
        assert route[1].link.name == "model2b_ptr"
        assert route[2].model == Model2A
        assert route[2].link.name == "model2a_ptr"

        # Test intermediate ancestor (skip one level)
        route = route_to_ancestor(Model2D, Model2B)
        assert len(route) == 2
        assert route[0].model == Model2C
        assert route[0].link.name == "model2c_ptr"
        assert route[1].model == Model2B
        assert route[1].link.name == "model2b_ptr"

        route = route_to_ancestor(Model2D, Model2C)
        assert len(route) == 1
        assert route[0].model == Model2C
        assert route[0].link.name == "model2c_ptr"

        # Test self (should return empty)
        assert route_to_ancestor(Model2A, Model2A) == []
        assert route_to_ancestor(Model2B, Model2B) == []
        assert route_to_ancestor(Model2D, Model2D) == []

        # Test non-ancestor (should return empty)
        assert route_to_ancestor(Model2A, Model2B) == []
        assert route_to_ancestor(Model2B, Model2C) == []
        assert route_to_ancestor(Model2C, Model2D) == []

        # Test unrelated models (should return empty)
        assert route_to_ancestor(ModelX, Model2A) == []
        assert route_to_ancestor(Model2A, ModelX) == []
        assert route_to_ancestor(BlogA, RelationA) == []

        # Test different hierarchy - Base -> ModelX
        route = route_to_ancestor(ModelX, Base)
        assert len(route) == 1
        assert route[0].model == Base
        assert route[0].link.name == "base_ptr"

        # Test different hierarchy - Base -> ModelY
        route = route_to_ancestor(ModelY, Base)
        assert len(route) == 1
        assert route[0].model == Base
        assert route[0].link.name == "base_ptr"

        # Test BlogBase hierarchy
        route = route_to_ancestor(BlogA, BlogBase)
        assert len(route) == 1
        assert route[0].model == BlogBase
        assert route[0].link.name == "blogbase_ptr"

        # Test multi-level RelationBase hierarchy
        route = route_to_ancestor(RelationBC, RelationBase)
        assert len(route) == 2
        assert route[0].model == RelationB
        assert route[0].link.name == "relationb_ptr"
        assert route[1].model == RelationBase
        assert route[1].link.name == "relationbase_ptr"

        route = route_to_ancestor(RelationBC, RelationB)
        assert len(route) == 1
        assert route[0].model == RelationB
        assert route[0].link.name == "relationb_ptr"

        route = route_to_ancestor(RelationB, RelationBase)
        assert len(route) == 1
        assert route[0].model == RelationBase
        assert route[0].link.name == "relationbase_ptr"

        # Test multiple inheritance - Enhance_Inherit
        route = route_to_ancestor(Enhance_Inherit, Enhance_Base)
        assert len(route) == 1
        assert route[0].model == Enhance_Base
        assert route[0].link.name == "enhance_base_ptr"

        route = route_to_ancestor(PurpleHeadDuck, Duck)
        assert len(route) == 1
        assert route[0].model == Duck
        assert route[0].link.name == "duck_ptr"


class PrepareForCopyTests(TransactionTestCase):
    def test_copy_polymorphic_objects(self):
        """
        Test copying polymorphic objects with multi-level inheritance.
        https://github.com/jazzband/django-polymorphic/issues/414

        This test verifies that the prepare_for_copy() method
        correctly handles copying objects with 2, 3, and 4 levels of inheritance.
        """
        from polymorphic.utils import prepare_for_copy
        from polymorphic.tests.models import Model2B, Model2C, Model2D

        # Create original objects
        obj_b = Model2B.objects.create(field1="B1", field2="B2")
        obj_c = Model2C.objects.create(field1="C1", field2="C2", field3="C3")
        obj_d = Model2D.objects.create(field1="D1", field2="D2", field3="D3", field4="D4")

        original_b_pk = obj_b.pk
        original_c_pk = obj_c.pk
        original_d_pk = obj_d.pk

        # Note: Model2C and Model2D inherit from Model2B, so they're also counted in Model2B.objects
        # Initial counts: Model2B=3 (obj_b, obj_c, obj_d), Model2C=2 (obj_c, obj_d), Model2D=1 (obj_d)
        assert Model2B.objects.count() == 3  # obj_b + obj_c + obj_d
        assert Model2C.objects.count() == 2  # obj_c + obj_d
        assert Model2D.objects.count() == 1  # obj_d

        # Test 1: Copy Model2B (2-level inheritance) using new method
        copy_b = Model2B.objects.get(pk=obj_b.pk)
        copy_b.field1 = "B1_copy"
        prepare_for_copy(copy_b)
        copy_b.save()

        # Verify the copy
        assert copy_b.pk != original_b_pk
        assert copy_b.field1 == "B1_copy"
        assert copy_b.field2 == "B2"
        assert Model2B.objects.filter(pk=original_b_pk).exists()
        assert Model2B.objects.filter(pk=copy_b.pk).exists()
        # Now we have: obj_b, copy_b, obj_c, obj_d
        assert Model2B.objects.count() == 4

        # Test 2: Copy Model2C (3-level inheritance) using new method
        # This is the main issue from #414 - previously failed
        copy_c = Model2C.objects.get(pk=obj_c.pk)
        copy_c.field1 = "C1_copy"
        prepare_for_copy(copy_c)
        copy_c.save()

        # Verify the copy
        assert copy_c.pk != original_c_pk
        assert copy_c.field1 == "C1_copy"
        assert copy_c.field2 == "C2"
        assert copy_c.field3 == "C3"
        assert Model2C.objects.filter(pk=original_c_pk).exists()
        assert Model2C.objects.filter(pk=copy_c.pk).exists()
        # Now we have Model2C: obj_c, copy_c, obj_d
        assert Model2C.objects.count() == 3
        # And Model2B: obj_b, copy_b, obj_c, copy_c, obj_d
        assert Model2B.objects.count() == 5

        # Test 3: Copy Model2D (4-level inheritance) using new method
        copy_d = Model2D.objects.get(pk=obj_d.pk)
        copy_d.field1 = "D1_copy"
        prepare_for_copy(copy_d)
        copy_d.save()

        # Verify the copy
        assert copy_d.pk != original_d_pk
        assert copy_d.field1 == "D1_copy"
        assert copy_d.field2 == "D2"
        assert copy_d.field3 == "D3"
        assert copy_d.field4 == "D4"
        assert Model2D.objects.filter(pk=original_d_pk).exists()
        assert Model2D.objects.filter(pk=copy_d.pk).exists()
        # Now we have Model2D: obj_d, copy_d
        assert Model2D.objects.count() == 2
        # Model2C: obj_c, copy_c, obj_d, copy_d
        assert Model2C.objects.count() == 4
        # Model2B: obj_b, copy_b, obj_c, copy_c, obj_d, copy_d
        assert Model2B.objects.count() == 6

        # Test 4: Verify old manual method still works for 2-level inheritance
        manual_copy_b = Model2B.objects.get(pk=obj_b.pk)
        manual_copy_b.field1 = "B1_manual"
        manual_copy_b.pk = None
        manual_copy_b.id = None
        manual_copy_b.save()

        assert manual_copy_b.pk not in [original_b_pk, copy_b.pk]
        assert manual_copy_b.field1 == "B1_manual"
        assert manual_copy_b.field2 == "B2"
        # Now we have Model2B: obj_b, copy_b, manual_copy_b, obj_c, copy_c, obj_d, copy_d
        assert Model2B.objects.count() == 7

        # Test 5: Verify that polymorphic queries work correctly on copied objects
        all_b = list(Model2B.objects.all().order_by("pk"))
        assert len(all_b) == 7  # obj_b, copy_b, manual_copy_b, obj_c, copy_c, obj_d, copy_d
        # Check that each is the correct type
        b_only = [obj for obj in all_b if type(obj).__name__ == "Model2B"]
        assert len(b_only) == 3  # obj_b, copy_b, manual_copy_b

        all_c = list(Model2C.objects.all().order_by("pk"))
        assert len(all_c) == 4  # obj_c, copy_c, obj_d, copy_d
        c_only = [obj for obj in all_c if type(obj).__name__ == "Model2C"]
        assert len(c_only) == 2  # obj_c, copy_c

        all_d = list(Model2D.objects.all().order_by("pk"))
        assert len(all_d) == 2  # obj_d, copy_d
        assert all(type(obj).__name__ == "Model2D" for obj in all_d)

        # Test 6: Verify polymorphic_ctype is set correctly on copied objects
        assert copy_b.polymorphic_ctype == ContentType.objects.get_for_model(Model2B)
        assert copy_c.polymorphic_ctype == ContentType.objects.get_for_model(Model2C)
        assert copy_d.polymorphic_ctype == ContentType.objects.get_for_model(Model2D)

    def test_prepare_for_copy_edge_cases(self):
        """
        Test edge cases in prepare_for_copy() method.


        The method should only reset parent link fields within the inheritance chain,
        not regular OneToOneFields to external models.
        """
        from polymorphic.utils import prepare_for_copy
        from polymorphic.tests.models import One2OneRelatingModel, Model2A, Model2C

        # Clean up
        One2OneRelatingModel.objects.all().delete()
        Model2A.objects.all().delete()

        # Create a Model2A instance to link to
        related_obj = Model2A.objects.create(field1="Related")

        # Create a One2OneRelatingModel with a regular OneToOneField
        obj_with_o2o = One2OneRelatingModel.objects.create(field1="Test1", one2one=related_obj)

        original_pk = obj_with_o2o.pk
        original_one2one_id = obj_with_o2o.one2one_id

        # Now copy the object
        copy_obj = One2OneRelatingModel.objects.get(pk=obj_with_o2o.pk)
        copy_obj.field1 = "Test1_copy"
        prepare_for_copy(copy_obj)

        # Verify that pk and polymorphic_ctype_id are reset
        assert copy_obj.pk is None
        assert copy_obj.id is None
        assert copy_obj.polymorphic_ctype_id is None

        assert copy_obj.one2one_id == original_one2one_id, (
            "Regular OneToOneField should NOT be reset by prepare_for_copy()"
        )
        assert copy_obj.one2one == related_obj

        # To save the copy, we need to create a new related object or clear the field
        # because the OneToOneField constraint prevents duplicate links
        new_related = Model2A.objects.create(field1="Related2")
        copy_obj.one2one = new_related
        copy_obj.save()

        # Verify the copy was created successfully
        assert copy_obj.pk != original_pk
        assert copy_obj.field1 == "Test1_copy"
        assert One2OneRelatingModel.objects.count() == 2

        # Create a 3-level inheritance object
        obj_c = Model2C.objects.create(field1="C1", field2="C2", field3="C3")
        original_c_pk = obj_c.pk

        # Model2C -> Model2B -> Model2A
        # Model2C should have model2b_ptr (parent link)

        copy_c = Model2C.objects.get(pk=obj_c.pk)
        copy_c.field1 = "C1_copy"

        # Before reset, the parent link fields should have values
        assert copy_c.model2b_ptr_id is not None

        prepare_for_copy(copy_c)

        # After reset, parent link fields should be None
        assert copy_c.pk is None
        assert copy_c.id is None
        assert copy_c.polymorphic_ctype_id is None
        assert copy_c.model2b_ptr_id is None  # Parent link should be reset

        copy_c.save()

        # Verify the copy was created
        assert copy_c.pk != original_c_pk
        assert copy_c.field1 == "C1_copy"
        assert copy_c.field2 == "C2"
        assert copy_c.field3 == "C3"

        # Create another object with OneToOneField to Model2A
        related_obj2 = Model2A.objects.create(field1="Related3")
        obj_with_o2o2 = One2OneRelatingModel.objects.create(field1="Test2", one2one=related_obj2)

        copy_obj2 = One2OneRelatingModel.objects.get(pk=obj_with_o2o2.pk)
        copy_obj2.field1 = "Test2_copy"

        # Store the one2one_id before reset
        one2one_id_before = copy_obj2.one2one_id

        prepare_for_copy(copy_obj2)

        # The one2one field should NOT be reset because Model2A is not in the inheritance tree
        # of One2OneRelatingModel
        assert copy_obj2.one2one_id == one2one_id_before, (
            "OneToOneField to model outside inheritance tree should NOT be reset"
        )

        # Create a new related object for the copy
        new_related2 = Model2A.objects.create(field1="Related4")
        copy_obj2.one2one = new_related2
        copy_obj2.save()

        assert One2OneRelatingModel.objects.count() == 4  # original, copy, obj2, copy2

    def test_prepare_for_copy_upcast(self):
        from polymorphic.utils import prepare_for_copy
        from polymorphic.tests.models import Model2B, Model2C

        c = Model2C.objects.create(field1="C1", field2="C2", field3="C3")
        c_as_b = Model2B.objects.non_polymorphic().get(pk=c.pk)

        # copy c as a b instance
        prepare_for_copy(c_as_b)
        c_as_b.save()

        assert Model2B.objects.count() == 2
        assert Model2C.objects.count() == 1

        c_as_b.refresh_from_db()
        assert c_as_b.field1 == "C1"
        assert c_as_b.field2 == "C2"
        assert not hasattr(c_as_b, "field3")
        assert c_as_b.polymorphic_ctype == ContentType.objects.get_for_model(Model2B)
        assert c_as_b.pk != c.pk

    def test_prepare_for_copy_plain(self):
        """
        Test that prepare_for_copy works on non-polymorphic (plain) multi-table models.
        """
        from polymorphic.utils import prepare_for_copy
        from polymorphic.tests.models import PlainC

        plain_c = PlainC.objects.create(field1="PC1", field2="PC2", field3="PC3")
        prepare_for_copy(plain_c)
        plain_c.save()
        plain_c.refresh_from_db()

        assert PlainC.objects.count() == 2
        assert PlainC.objects.filter(field1="PC1").count() == 2
        assert PlainC.objects.order_by("pk").last() == plain_c

    def test_copy_with_abstract_base(self):
        """
        Test copying polymorphic objects with an abstract base class.
        """
        from polymorphic.utils import prepare_for_copy
        from polymorphic.tests.models import RelationBase, RelationA, RelationB, RelationBC

        obase = RelationBase.objects.create(field_base="base")
        oa = RelationA.objects.create(field_base="A1", field_a="A2", fk=obase)
        ob = RelationB.objects.create(field_base="B1", field_b="B2", fk=oa)
        oc = RelationBC.objects.create(field_base="C1", field_b="C2", field_c="C3", fk=oa)
        oc.m2m.add(oa)
        oc.m2m.add(ob)

        assert set(oc.m2m.all()) == {oa, ob}
        prepare_for_copy(oc)
        oc.save()

        assert oc.m2m.count() == 0  # M2M should not be copied
        assert RelationBC.objects.count() == 2
        assert oc.field_base == "C1"
        assert oc.field_b == "C2"
        assert oc.field_c == "C3"
        assert oc.fk == oa  # FK to parent should remain unchanged

    def test_copy_with_proxies(self):
        """
        Test that copying walks up proxy model chains correctly.
        """
        from polymorphic.utils import prepare_for_copy
        from polymorphic.tests.models import Duck, PurpleHeadDuck

        daffy1 = PurpleHeadDuck.objects.create(name="daffy")
        assert Duck.objects.count() == 1
        daffy2 = PurpleHeadDuck.objects.get(pk=daffy1.pk)
        prepare_for_copy(daffy2)
        daffy2.save()
        daffy2.refresh_from_db()
        assert daffy2.pk != daffy1.pk
        assert Duck.objects.count() == 2
        assert PurpleHeadDuck.objects.count() == 2
        assert Duck.objects.filter(name="daffy").count() == 2

        daffy3 = Duck.objects.non_polymorphic().last()
        prepare_for_copy(daffy3)
        daffy3.save()
        assert Duck.objects.count() == 3
        assert PurpleHeadDuck.objects.count() == 2
        assert Duck.objects.filter(name="daffy").count() == 3
        assert set(Duck.objects.all()) == {daffy1, daffy2, daffy3}

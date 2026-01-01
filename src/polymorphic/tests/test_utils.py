import pytest
from django.test import TransactionTestCase

from polymorphic.models import PolymorphicModel, PolymorphicTypeUndefined
from polymorphic.tests.models import (
    Enhance_Base,
    Enhance_Inherit,
    Model2A,
    Model2B,
    Model2C,
    Model2D,
)
from polymorphic.utils import get_base_polymorphic_model, reset_polymorphic_ctype, sort_by_subclass


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
        )

        # Model2A hierarchy (with manager variants)
        assert Model2A._concrete_descendants == [
            Model2B,
            Model2C,
            Model2D,
            ModelWithMyManager,
            ModelWithMyManagerNoDefault,
            ModelWithMyManagerDefault,
            ModelWithMyManager2,
        ]
        assert Model2B._concrete_descendants == [Model2C, Model2D]
        assert Model2C._concrete_descendants == [Model2D]
        assert len(Model2D._concrete_descendants) == 0

        # ModelWithMyManager variants (no further descendants)
        assert len(ModelWithMyManager._concrete_descendants) == 0
        assert len(ModelWithMyManagerNoDefault._concrete_descendants) == 0
        assert len(ModelWithMyManagerDefault._concrete_descendants) == 0
        assert len(ModelWithMyManager2._concrete_descendants) == 0

        # Base hierarchy (tree order: ModelX defined before ModelY)
        assert Base._concrete_descendants == [ModelX, ModelY, FKTestChild]
        assert len(ModelX._concrete_descendants) == 0
        assert len(ModelY._concrete_descendants) == 0

        # BlogBase hierarchy (tree order: BlogA defined before BlogB)
        assert BlogBase._concrete_descendants == [BlogA, BlogB]
        assert len(BlogA._concrete_descendants) == 0
        assert len(BlogB._concrete_descendants) == 0

        # RelationBase hierarchy (tree order: RelationA before RelationB, RelationBC is child of RelationB)
        assert RelationBase._concrete_descendants == [RelationA, RelationB, RelationBC]
        assert len(RelationA._concrete_descendants) == 0
        assert RelationB._concrete_descendants == [RelationBC]
        assert len(RelationBC._concrete_descendants) == 0

        # ProxyBase hierarchy (ProxyChild is proxy, so excluded)
        assert ProxyBase._concrete_descendants == [NonProxyChild]
        assert len(NonProxyChild._concrete_descendants) == 0

        # ProxiedBase hierarchy (tree order: ProxyModelA defined before ProxyModelB)
        # ProxyModelBase is proxy, but has concrete children
        assert ProxiedBase._concrete_descendants == [ProxyModelA, ProxyModelB]
        # ProxyModelBase is proxy but should still return its concrete descendants
        assert ProxyModelBase._concrete_descendants == [ProxyModelA, ProxyModelB]
        assert len(ProxyModelA._concrete_descendants) == 0
        assert len(ProxyModelB._concrete_descendants) == 0

        # CustomPkBase hierarchy
        assert CustomPkBase._concrete_descendants == [CustomPkInherit]
        assert len(CustomPkInherit._concrete_descendants) == 0

        # MultiTableBase hierarchy
        assert MultiTableBase._concrete_descendants == [MultiTableDerived]
        assert len(MultiTableDerived._concrete_descendants) == 0

        # Enhance_Base hierarchy
        assert Enhance_Base._concrete_descendants == [Enhance_Inherit]
        assert len(Enhance_Inherit._concrete_descendants) == 0

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
        )

        # Test direct parent (one hop)
        route = Model2B._route_to_ancestor(Model2A)
        assert len(route) == 1
        assert route[0].model == Model2A
        assert route[0].link.name == "model2a_ptr"

        # Test grandparent (two hops)
        route = Model2C._route_to_ancestor(Model2A)
        assert len(route) == 2
        assert route[0].model == Model2B
        assert route[0].link.name == "model2b_ptr"
        assert route[1].model == Model2A
        assert route[1].link.name == "model2a_ptr"

        # Test great-grandparent (three hops)
        route = Model2D._route_to_ancestor(Model2A)
        assert len(route) == 3
        assert route[0].model == Model2C
        assert route[0].link.name == "model2c_ptr"
        assert route[1].model == Model2B
        assert route[1].link.name == "model2b_ptr"
        assert route[2].model == Model2A
        assert route[2].link.name == "model2a_ptr"

        # Test intermediate ancestor (skip one level)
        route = Model2D._route_to_ancestor(Model2B)
        assert len(route) == 2
        assert route[0].model == Model2C
        assert route[0].link.name == "model2c_ptr"
        assert route[1].model == Model2B
        assert route[1].link.name == "model2b_ptr"

        route = Model2D._route_to_ancestor(Model2C)
        assert len(route) == 1
        assert route[0].model == Model2C
        assert route[0].link.name == "model2c_ptr"

        # Test self (should return empty)
        assert Model2A._route_to_ancestor(Model2A) == []
        assert Model2B._route_to_ancestor(Model2B) == []
        assert Model2D._route_to_ancestor(Model2D) == []

        # Test non-ancestor (should return empty)
        assert Model2A._route_to_ancestor(Model2B) == []
        assert Model2B._route_to_ancestor(Model2C) == []
        assert Model2C._route_to_ancestor(Model2D) == []

        # Test unrelated models (should return empty)
        assert ModelX._route_to_ancestor(Model2A) == []
        assert Model2A._route_to_ancestor(ModelX) == []
        assert BlogA._route_to_ancestor(RelationA) == []

        # Test different hierarchy - Base -> ModelX
        route = ModelX._route_to_ancestor(Base)
        assert len(route) == 1
        assert route[0].model == Base
        assert route[0].link.name == "base_ptr"

        # Test different hierarchy - Base -> ModelY
        route = ModelY._route_to_ancestor(Base)
        assert len(route) == 1
        assert route[0].model == Base
        assert route[0].link.name == "base_ptr"

        # Test BlogBase hierarchy
        route = BlogA._route_to_ancestor(BlogBase)
        assert len(route) == 1
        assert route[0].model == BlogBase
        assert route[0].link.name == "blogbase_ptr"

        # Test multi-level RelationBase hierarchy
        route = RelationBC._route_to_ancestor(RelationBase)
        assert len(route) == 2
        assert route[0].model == RelationB
        assert route[0].link.name == "relationb_ptr"
        assert route[1].model == RelationBase
        assert route[1].link.name == "relationbase_ptr"

        route = RelationBC._route_to_ancestor(RelationB)
        assert len(route) == 1
        assert route[0].model == RelationB
        assert route[0].link.name == "relationb_ptr"

        route = RelationB._route_to_ancestor(RelationBase)
        assert len(route) == 1
        assert route[0].model == RelationBase
        assert route[0].link.name == "relationbase_ptr"

        # Test multiple inheritance - Enhance_Inherit
        route = Enhance_Inherit._route_to_ancestor(Enhance_Base)
        assert len(route) == 1
        assert route[0].model == Enhance_Base
        assert route[0].link.name == "enhance_base_ptr"

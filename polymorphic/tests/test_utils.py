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

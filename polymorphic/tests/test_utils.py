from django.test import TransactionTestCase

from polymorphic.models import PolymorphicTypeUndefined
from polymorphic.tests import Model2A, Model2B, Model2C, Model2D
from polymorphic.utils import reset_polymorphic_ctype, sort_by_subclass


class UtilsTests(TransactionTestCase):

    def test_sort_by_subclass(self):
        self.assertEqual(
            sort_by_subclass(Model2D, Model2B, Model2D, Model2A, Model2C),
            [Model2A, Model2B, Model2C, Model2D, Model2D]
        )

    def test_reset_polymorphic_ctype(self):
        """
        Test the the polymorphic_ctype_id can be restored.
        """
        Model2A.objects.create(field1='A1')
        Model2D.objects.create(field1='A1', field2='B2', field3='C3', field4='D4')
        Model2B.objects.create(field1='A1', field2='B2')
        Model2B.objects.create(field1='A1', field2='B2')
        Model2A.objects.all().update(polymorphic_ctype_id=None)

        with self.assertRaises(PolymorphicTypeUndefined):
            list(Model2A.objects.all())

        reset_polymorphic_ctype(Model2D, Model2B, Model2D, Model2A, Model2C)

        self.assertQuerysetEqual(
            Model2A.objects.order_by("pk"),
            [
                Model2A,
                Model2D,
                Model2B,
                Model2B,
            ],
            transform=lambda o: o.__class__,
        )

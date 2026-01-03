from django.test import TransactionTestCase
from polymorphic.tests.models import (
    Model2A,
    Model2B,
    Model2C,
    Model2D,
)


class PerformanceTests(TransactionTestCase):
    def test_baseline_number_of_queries(self):
        """
        Test that the number of queries for loading polymorphic models is within
        expected limits.
        """
        for idx in range(100):
            Model2A.objects.create(field1=f"A{idx}")
            Model2B.objects.create(field1=f"A{idx}", field2=f"B{idx}")
            Model2C.objects.create(field1=f"A{idx}", field2=f"B{idx}", field3=f"C{idx}")
            Model2D.objects.create(
                field1=f"A{idx}", field2=f"B{idx}", field3=f"C{idx}", field4=f"D{idx}"
            )

        with self.assertNumQueries(4):
            list(Model2A.objects.all().order_by("pk"))

        with self.assertNumQueries(3):
            list(Model2B.objects.all().order_by("pk"))

        with self.assertNumQueries(2):
            list(Model2C.objects.all().order_by("pk"))

        with self.assertNumQueries(1):
            list(Model2D.objects.all().order_by("pk"))

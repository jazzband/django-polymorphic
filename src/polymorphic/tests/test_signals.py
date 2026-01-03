from django.test import TestCase
from django.db.models.signals import post_delete
from django.db import connection
from .models import Model2A, Model2B, Model2C, PlainA, PlainB, PlainC

from django.test.utils import CaptureQueriesContext


class TestSignals(TestCase):
    def test_first_behavior_during_post_delete_signal_1(self):
        """
        Regression test for issue #347: first() returning None in post_delete signals.

        The bug occurs when:
        1. An object with a post_delete signal is created first
        2. Another object is created second
        3. The first object is deleted
        4. In the post_delete signal, first() should return the second object but
           returned None
        """
        obj1 = Model2B.objects.create(field1="First", field2="B")
        obj2 = Model2A.objects.create(field1="Second")

        def log_first_with_first_method(sender, instance, **kwargs):
            self.assertEqual(Model2A.objects.order_by("pk").first().pk, obj1.pk)
            self.assertEqual(Model2A.objects.order_by("pk").last().pk, obj2.pk)
            self.assertEqual(Model2B.objects.count(), 0)
            self.assertEqual(Model2A.objects.count(), 2)

        post_delete.connect(log_first_with_first_method, sender=Model2B)
        obj1.delete()
        post_delete.disconnect(log_first_with_first_method, sender=Model2C)

    def test_first_behavior_during_post_delete_signal_2(self):
        """
        Test that the fix works when the object with signal is created second.
        The bug only occurred when the signaled object was created first.
        """
        obj1 = Model2A.objects.create(field1="Second")
        obj2 = Model2B.objects.create(field1="First", field2="B")

        def log_first_with_first_method(sender, instance, **kwargs):
            self.assertEqual(Model2A.objects.order_by("pk").first(), obj1)
            self.assertEqual(Model2B.objects.count(), 0)

        post_delete.connect(log_first_with_first_method, sender=Model2B)
        obj2.delete()
        post_delete.disconnect(log_first_with_first_method, sender=Model2C)

    def test_getitem_behavior_during_post_delete_signal(self):
        """
        Regression test for issue #347: [0] returning None in post_delete signals.
        """
        obj1 = Model2C.objects.create(field1="First", field2="C", field3="C3")
        obj2 = Model2A.objects.create(field1="Second")

        def log_first_with_brackets(sender, instance, **kwargs):
            try:
                self.assertEqual(Model2A.objects.order_by("pk")[0].pk, obj1.pk)
                self.assertEqual(Model2A.objects.order_by("pk")[1].pk, obj2.pk)
                self.assertEqual(Model2C.objects.count(), 0)
                self.assertEqual(Model2A.objects.count(), 2)
            except IndexError:
                self.fail("Queryset __getitem__[0] returned IndexError unexpectedly")

        post_delete.connect(log_first_with_brackets, sender=Model2C)
        obj1.delete()  # trigger signal handling
        post_delete.disconnect(log_first_with_brackets, sender=Model2C)

    def test_normal_getitem_behavior_during_post_delete_signal(self):
        """
        Illustrate standard Django multi-table inheritance during this test.
        """
        obj1 = PlainC.objects.create(field1="First", field2="C", field3="C3")
        obj2 = PlainA.objects.create(field1="Second")

        def log_first_with_brackets(sender, instance, **kwargs):
            try:
                self.assertEqual(PlainA.objects.order_by("pk")[0].pk, obj1.pk)
                self.assertEqual(PlainA.objects.order_by("pk")[1], obj2)
                self.assertEqual(PlainC.objects.count(), 0)
            except IndexError:
                self.fail("Queryset __getitem__[0] returned IndexError unexpectedly")

        post_delete.connect(log_first_with_brackets, sender=PlainC)
        obj1.delete()  # trigger signal handling
        post_delete.disconnect(log_first_with_brackets, sender=PlainC)

    def test_queryset_first_returns_remaining_object_in_post_delete_signal(self):
        """
        Regression test for issue #347: first() returning None in post_delete signals.

        The bug occurs when:
        1. An object with a post_delete signal is created first
        2. Another object is created second
        3. The first object is deleted
        4. In the post_delete signal, first() should return the second object but returned None
        """
        obj1 = Model2B.objects.create(field1="First", field2="B")
        obj1_base = Model2A.objects.non_polymorphic().get(pk=obj1.pk)
        obj2 = Model2A.objects.create(field1="Second")

        def check_2b_delete(sender, instance, **kwargs):
            assert Model2B.objects.count() == 0
            assert Model2A.objects.order_by("pk").first() == obj1_base
            assert Model2A.objects.count() == 2

        def check_2a_delete(sender, instance, **kwargs):
            assert Model2A.objects.order_by("pk").first() == obj2
            assert Model2A.objects.count() == 1

        try:
            post_delete.connect(check_2b_delete, sender=Model2B)
            post_delete.connect(check_2a_delete, sender=Model2A)

            # This will trigger the post_delete signal, first for the deletion of the
            # 2b row - then for the deletion of the 2a row - at each signal the database
            # should be consistent with the staged deletion of rows most derived first
            # order.
            obj1.delete()

        finally:
            post_delete.disconnect(check_2b_delete, sender=Model2B)
            post_delete.disconnect(check_2a_delete, sender=Model2A)

    def test_queryset_getitem_returns_remaining_object_in_post_delete_signal(self):
        """
        Regression test for issue #347: [0] returning None in post_delete signals.
        """
        obj1 = Model2C.objects.create(field1="First", field2="C", field3="C3")
        obj1_baseb = Model2B.objects.non_polymorphic().get(pk=obj1.pk)
        obj1_basea = Model2A.objects.non_polymorphic().get(pk=obj1.pk)
        obj2 = Model2A.objects.create(field1="Second")

        def check_2c_delete(sender, instance, **kwargs):
            assert Model2C.objects.count() == 0
            assert Model2B.objects.count() == 1
            assert Model2A.objects.count() == 2
            assert Model2B.objects.order_by("pk")[0] == obj1_baseb
            assert Model2A.objects.order_by("pk")[0] == obj1_baseb

        def check_2b_delete(sender, instance, **kwargs):
            assert Model2C.objects.count() == 0
            assert Model2B.objects.count() == 0
            assert Model2A.objects.count() == 2
            assert Model2A.objects.order_by("pk")[0] == obj1_basea

        def check_2a_delete(sender, instance, **kwargs):
            assert Model2C.objects.count() == 0
            assert Model2B.objects.count() == 0
            assert Model2A.objects.count() == 1
            assert Model2A.objects.order_by("pk")[0] == obj2

        # Connect signal
        try:
            post_delete.connect(check_2c_delete, sender=Model2C)
            post_delete.connect(check_2b_delete, sender=Model2B)
            post_delete.connect(check_2a_delete, sender=Model2A)
            obj1.delete()
        finally:
            post_delete.disconnect(check_2c_delete, sender=Model2C)
            post_delete.disconnect(check_2b_delete, sender=Model2B)
            post_delete.disconnect(check_2a_delete, sender=Model2A)

    def test_queryset_first_works_when_deleted_object_created_second(self):
        """
        Test that the fix works when the object with signal is created second.
        The bug only occurred when the signaled object was created first.
        """
        obj1 = Model2A.objects.create(field1="Second")
        obj2 = Model2B.objects.create(field1="First", field2="B")
        obj2_base = Model2A.objects.non_polymorphic().get(pk=obj2.pk)

        def check_2b_delete(sender, instance, **kwargs):
            assert Model2B.objects.count() == 0
            assert Model2A.objects.order_by("pk").first() == obj1
            assert Model2A.objects.last() == obj2_base
            assert Model2A.objects.count() == 2

        def check_2a_delete(sender, instance, **kwargs):
            assert Model2A.objects.order_by("pk").first() == obj1
            assert Model2A.objects.count() == 1

        try:
            post_delete.connect(check_2a_delete, sender=Model2A)
            post_delete.connect(check_2b_delete, sender=Model2B)

            # This will trigger the post_delete signal, first for the deletion of the
            # 2b row - then for the deletion of the 2a row - at each signal the database
            # should be consistent with the staged deletion of rows most derived first
            # order.
            obj2.delete()

        finally:
            post_delete.disconnect(check_2b_delete, sender=Model2B)
            post_delete.disconnect(check_2a_delete, sender=Model2A)

    def test_besteffort_iteration_avoids_nplusone(self):
        """
        Test that our best effort iteration avoids n+1 queries when n objects have stale
        content type pointers.
        """
        for i in range(100):
            Model2C.objects.create(
                field1=f"Model2C_{i}", field2="Model2C_{i}", field3="Model2C_{i}"
            )

        def check_2c_delete(sender, instance, **kwargs):
            assert Model2C.objects.count() == 0
            assert Model2B.objects.count() == 100
            assert Model2A.objects.count() == 100

            from django.db.backends.utils import CursorWrapper

            for _ in Model2B.objects.all():
                pass  # Evaluating the queryset

            with CaptureQueriesContext(connection) as all_2b:
                for _ in Model2B.objects.all():
                    pass  # Evaluating the queryset

            assert len(all_2b.captured_queries) <= 3

            with CaptureQueriesContext(connection) as all_2a:
                for _ in Model2A.objects.all():
                    pass  # Evaluating the queryset

            assert len(all_2a.captured_queries) <= 4

        def check_2b_delete(sender, instance, **kwargs):
            assert Model2C.objects.count() == 0
            assert Model2B.objects.count() == 0
            assert Model2A.objects.count() == 100

            with CaptureQueriesContext(connection) as all_2a:
                for _ in Model2A.objects.all():
                    pass  # Evaluating the queryset

            assert len(all_2a.captured_queries) <= 3

        def check_2a_delete(sender, instance, **kwargs):
            assert Model2C.objects.count() == 0
            assert Model2B.objects.count() == 0
            assert Model2A.objects.count() == 0

            with CaptureQueriesContext(connection) as all_2a:
                for _ in Model2A.objects.all():
                    pass  # Evaluating the queryset

            assert len(all_2a.captured_queries) <= 3

        try:
            post_delete.connect(check_2b_delete, sender=Model2B)
            post_delete.connect(check_2a_delete, sender=Model2A)
            post_delete.connect(check_2c_delete, sender=Model2C)

            Model2C.objects.all().delete()

        finally:
            post_delete.disconnect(check_2b_delete, sender=Model2B)
            post_delete.disconnect(check_2a_delete, sender=Model2A)
            post_delete.disconnect(check_2c_delete, sender=Model2C)

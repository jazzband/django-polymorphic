from django.test import TestCase
from django.db.models.signals import post_delete
from .models import Model2A, Model2B, Model2C, PlainA, PlainB, PlainC


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
            self.assertEqual(Model2A.objects.order_by("pk").last().pk, obj2)
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
                self.assertEqual(Model2A.objects.order_by("pk")[1], obj2)
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

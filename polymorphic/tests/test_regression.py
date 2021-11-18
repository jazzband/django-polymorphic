import django
from django.test import TestCase

from polymorphic.tests.models import Bottom, Middle, Top

transform_arg = {"transform": repr} if django.VERSION >= (3, 2) else {}


class RegressionTests(TestCase):
    def test_for_query_result_incomplete_with_inheritance(self):
        """ https://github.com/bconstantin/django_polymorphic/issues/15 """

        top = Top()
        top.save()
        middle = Middle()
        middle.save()
        bottom = Bottom()
        bottom.save()

        expected_queryset = [top, middle, bottom]
        self.assertQuerysetEqual(
            Top.objects.order_by("pk"), [repr(r) for r in expected_queryset], **transform_arg
        )

        expected_queryset = [middle, bottom]
        self.assertQuerysetEqual(
            Middle.objects.order_by("pk"), [repr(r) for r in expected_queryset], **transform_arg
        )

        expected_queryset = [bottom]
        self.assertQuerysetEqual(
            Bottom.objects.order_by("pk"), [repr(r) for r in expected_queryset], **transform_arg
        )

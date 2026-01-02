from django.test import TestCase

from django.db import models
from django.db.models import functions
from polymorphic.models import PolymorphicTypeInvalid
from polymorphic.tests.models import (
    Bottom,
    Middle,
    Top,
    Team,
    UserProfile,
    Model2A,
    Model2B,
    Regression295Parent,
    Regression295Related,
)


class RegressionTests(TestCase):
    def test_for_query_result_incomplete_with_inheritance(self):
        """https://github.com/bconstantin/django_polymorphic/issues/15"""

        top = Top()
        top.save()
        middle = Middle()
        middle.save()
        bottom = Bottom()
        bottom.save()

        expected_queryset = [top, middle, bottom]
        self.assertQuerySetEqual(
            Top.objects.order_by("pk"),
            [repr(r) for r in expected_queryset],
            transform=repr,
        )

        expected_queryset = [middle, bottom]
        self.assertQuerySetEqual(
            Middle.objects.order_by("pk"),
            [repr(r) for r in expected_queryset],
            transform=repr,
        )

        expected_queryset = [bottom]
        self.assertQuerySetEqual(
            Bottom.objects.order_by("pk"),
            [repr(r) for r in expected_queryset],
            transform=repr,
        )

    def test_pr_254(self):
        user_a = UserProfile.objects.create(name="a")
        user_b = UserProfile.objects.create(name="b")
        user_c = UserProfile.objects.create(name="c")

        team1 = Team.objects.create(team_name="team1")
        team1.user_profiles.add(user_a, user_b, user_c)
        team1.save()

        team2 = Team.objects.create(team_name="team2")
        team2.user_profiles.add(user_c)
        team2.save()

        # without prefetch_related, the test passes
        my_teams = (
            Team.objects.filter(user_profiles=user_c)
            .order_by("team_name")
            .prefetch_related("user_profiles")
            .distinct()
        )

        self.assertEqual(len(my_teams[0].user_profiles.all()), 3)

        self.assertEqual(len(my_teams[1].user_profiles.all()), 1)

        self.assertEqual(len(my_teams[0].user_profiles.all()), 3)
        self.assertEqual(len(my_teams[1].user_profiles.all()), 1)

        # without this "for" loop, the test passes
        for _ in my_teams:
            pass

        # This time, test fails.  PR 254 claim
        # with sqlite:      4 != 3
        # with postgresql:  2 != 3
        self.assertEqual(len(my_teams[0].user_profiles.all()), 3)
        self.assertEqual(len(my_teams[1].user_profiles.all()), 1)

    def test_alias_queryset(self):
        """
        Test that .alias() works works correctly with polymorphic querysets.
        It should not raise AttributeError, and the aliased field should NOT be present on the instance.
        """
        Model2B.objects.create(field1="val1", field2="val2")

        # Scenario 1: .alias() only
        # Should not crash, and 'lower_field1' should NOT be an attribute
        qs = Model2A.objects.alias(lower_field1=functions.Lower("field1"))
        results = list(qs)
        self.assertEqual(len(results), 1)
        self.assertIsInstance(results[0], Model2B)
        self.assertFalse(hasattr(results[0], "lower_field1"))

        # Scenario 2: .annotate()
        # Should work, and 'upper_field1' SHOULD be an attribute
        qs = Model2A.objects.annotate(upper_field1=functions.Upper("field1"))
        results = list(qs)
        self.assertEqual(len(results), 1)
        self.assertTrue(hasattr(results[0], "upper_field1"))
        self.assertEqual(results[0].upper_field1, "VAL1")

        # Scenario 3: Mixed alias() and annotate()
        qs = Model2A.objects.alias(alias_val=functions.Lower("field1")).annotate(
            anno_val=functions.Upper("field1")
        )
        results = list(qs)
        self.assertEqual(len(results), 1)
        self.assertFalse(hasattr(results[0], "alias_val"))
        self.assertTrue(hasattr(results[0], "anno_val"))
        self.assertEqual(results[0].anno_val, "VAL1")

    def test_alias_advanced(self):
        """
        Test .alias() interactions with filter, order_by, only, and defer.
        """
        obj1 = Model2B.objects.create(field1="Alpha", field2="One")
        obj2 = Model2B.objects.create(field1="Beta", field2="Two")
        obj3 = Model2B.objects.create(field1="Gamma", field2="Three")

        # 1. Filter by alias
        qs = Model2A.objects.alias(lower_f1=functions.Lower("field1")).filter(lower_f1="beta")
        self.assertEqual(qs.count(), 1)
        self.assertEqual(qs[0], obj2)
        self.assertFalse(hasattr(qs[0], "lower_f1"))

        # 2. Order by alias
        qs = Model2A.objects.alias(len_f2=functions.Length("model2b__field2")).order_by("len_f2")
        # Lengths: One=3, Two=3, Three=5. (Ordering of equal values is DB dep, but logic holds)
        results = list(qs)
        self.assertEqual(len(results), 3)
        self.assertFalse(hasattr(results[0], "len_f2"))

        # 3. Alias + Only
        qs = Model2A.objects.alias(lower_f1=functions.Lower("field1")).only("field1")
        # Should not crash
        results = list(qs)
        self.assertEqual(len(results), 3)
        # Verify deferral logic didn't break
        # accessing field1 should not trigger refresh (hard to test without internals, but basic access works)
        self.assertEqual(results[0].field1, "Alpha")

        # 4. Alias + Defer
        qs = Model2A.objects.alias(lower_f1=functions.Lower("field1")).defer("field1")
        results = list(qs)
        self.assertEqual(len(results), 3)
        # accessing field1 should trigger refresh
        self.assertEqual(results[0].field1, "Alpha")

    def test_upcasting_to_sibling_class(self):
        """
        Test that querying a model that has been upcasted to a sibling
        polymorphic class does not raise a TypeError.
        Reproduces issue #280.
        """
        # Create a Model2A instance with a specific pk
        Model2A.objects.create(pk=1, field1="original")

        # "Upcast" it to a Model2B by creating an object with the same pk.
        # The polymorphic_ctype will now point to Model2B.
        Model2B.objects.create(pk=1, field1="updated", field2="new")

        # The original bug raised TypeError. We expect that accessing the
        # queryset should not raise TypeError. It should either be empty,
        # or raise a clean PolymorphicTypeInvalid error.
        try:
            list(Model2A.objects.all())
        except PolymorphicTypeInvalid:
            pass  # This is an acceptable outcome.
        except TypeError as e:
            self.fail(f"Querying for upcasted sibling raised TypeError: {e}")

    def test_mixed_inheritance_save_issue_495(self):
        """
        Test that saving models with mixed polymorphic and non-polymorphic
        inheritance works correctly. This addresses issue #495.
        """
        from polymorphic.tests.models import NormalExtension, PolyExtension, PolyExtChild

        # Create and save NormalExtension
        normal_ext = NormalExtension.objects.create(nb_field=1, ne_field="normal")
        normal_ext.add_to_ne(" extended")
        normal_ext.refresh_from_db()
        self.assertEqual(normal_ext.ne_field, "normal extended")
        normal_ext.add_to_nb(5)
        normal_ext.refresh_from_db()
        self.assertEqual(normal_ext.nb_field, 6)

        # Create and save PolyExtension
        poly_ext = PolyExtension.objects.create(nb_field=1, ne_field="normal", poly_ext_field=10)
        poly_ext.add_to_ne(" extended")
        poly_ext.refresh_from_db()
        self.assertEqual(poly_ext.ne_field, "normal extended")
        poly_ext.add_to_ext(5)
        poly_ext.refresh_from_db()
        self.assertEqual(poly_ext.poly_ext_field, 15)
        poly_ext.add_to_nb(5)
        poly_ext.refresh_from_db()
        self.assertEqual(poly_ext.nb_field, 6)

        # Create and save PolyExtChild
        poly_child = PolyExtChild.objects.create(
            nb_field=1, ne_field="normal", poly_ext_field=20, poly_child_field="child"
        )
        poly_child.add_to_ne(" extended")
        poly_child.add_to_nb(5)
        poly_child.add_to_ext(10)
        poly_child.add_to_child(" added")
        poly_child.refresh_from_db()
        self.assertEqual(poly_child.nb_field, 6)
        self.assertEqual(poly_child.ne_field, "normal extended")
        self.assertEqual(poly_child.poly_ext_field, 30)
        self.assertEqual(poly_child.poly_child_field, "child added")

        poly_child.override_add_to_ne(" overridden")
        poly_child.override_add_to_ext(5)
        poly_child.refresh_from_db()
        self.assertEqual(poly_child.ne_field, "normal extended OVERRIDDEN")
        self.assertEqual(poly_child.poly_ext_field, 40)

    def test_create_or_update(self):
        """
        https://github.com/jazzband/django-polymorphic/issues/494
        """
        from polymorphic.tests.models import Model2B, Model2C

        obj, created = Model2B.objects.update_or_create(
            field1="value1", defaults={"field2": "value2"}
        )
        self.assertTrue(created)
        self.assertEqual(obj.field1, "value1")
        self.assertEqual(obj.field2, "value2")

        obj2, created = Model2B.objects.update_or_create(
            field1="value1", defaults={"field2": "new_value2"}
        )
        self.assertFalse(created)
        self.assertEqual(obj2.pk, obj.pk)
        self.assertEqual(obj2.field1, "value1")
        self.assertEqual(obj2.field2, "new_value2")

        self.assertEqual(Model2B.objects.count(), 1)

        obj3, created = Model2C.objects.update_or_create(
            field1="value1", defaults={"field2": "new_value3", "field3": "value3"}
        )

        self.assertTrue(created)
        self.assertEqual(Model2B.objects.count(), 2)
        self.assertEqual(Model2C.objects.count(), 1)
        self.assertEqual(obj3, Model2B.objects.order_by("pk").last())

    def test_double_underscore_in_related_name(self):
        """
        Test filtering on a related field when the relation name itself contains '__'.
        This reproduces the issue in #295, where 'my__relation___real_field' was
        being incorrectly parsed as a polymorphic lookup.
        """

        related = Regression295Related.objects.create(_real_field="test_value")
        Regression295Parent.objects.create(related_object=related)

        # The following filter would be translated to 'related_object___real_field'
        # by Django's query machinery.
        qs = Regression295Parent.objects.filter(related_object___real_field="test_value")
        self.assertEqual(qs.count(), 1)

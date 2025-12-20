from django.test import TestCase

from django.db import models
from django.db.models import functions
from polymorphic.tests.models import Bottom, Middle, Top, Team, UserProfile, Model2A, Model2B


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

from django.test import TestCase

from polymorphic.tests.models import Bottom, Middle, Top, Team, UserProfile


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

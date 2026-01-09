from django.test import TestCase
from polymorphic.tests.models import (
    Bottom as Bottom,
    Middle as Middle,
    Team as Team,
    Top as Top,
    UserProfile as UserProfile,
)

class RegressionTests(TestCase):
    def test_for_query_result_incomplete_with_inheritance(self) -> None: ...
    def test_pr_254(self) -> None: ...

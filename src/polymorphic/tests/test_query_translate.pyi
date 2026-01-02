from django.test import TestCase
from polymorphic.query_translate import (
    translate_polymorphic_filter_definitions_in_args as translate_polymorphic_filter_definitions_in_args,
)
from polymorphic.tests.models import Bottom as Bottom, Middle as Middle, Top as Top

class QueryTranslateTests(TestCase):
    def test_translate_with_not_pickleable_query(self) -> None: ...
    def test_deep_copy_of_q_objects(self) -> None: ...

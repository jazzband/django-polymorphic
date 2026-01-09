from django.test import TestCase
from polymorphic.contrib.guardian import (
    get_polymorphic_base_content_type as get_polymorphic_base_content_type,
)
from polymorphic.tests.models import Model2D as Model2D, PlainC as PlainC

class ContribTests(TestCase):
    def test_contrib_guardian(self) -> None: ...

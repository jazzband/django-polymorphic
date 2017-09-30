from unittest import TestCase

from polymorphic.contrib.guardian import get_polymorphic_base_content_type
from polymorphic.tests.models import (
    Model2D,
    PlainC,
)


class ContribTests(TestCase):
    """
    The test suite
    """


    def test_contrib_guardian(self):
        # Regular Django inheritance should return the child model content type.
        obj = PlainC()
        ctype = get_polymorphic_base_content_type(obj)
        self.assertEqual(ctype.name, 'plain c')

        ctype = get_polymorphic_base_content_type(PlainC)
        self.assertEqual(ctype.name, 'plain c')

        # Polymorphic inheritance should return the parent model content type.
        obj = Model2D()
        ctype = get_polymorphic_base_content_type(obj)
        self.assertEqual(ctype.name, 'model2a')

        ctype = get_polymorphic_base_content_type(Model2D)
        self.assertEqual(ctype.name, 'model2a')

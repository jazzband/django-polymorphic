from polymorphic.tests.models import Foo, Bar, Baz
from polymorphic.managers import PolymorphicManager
from django.test import TestCase


class InheritanceTests(TestCase):
    def test_mixin_inherited_managers(self):
        self.assertIsInstance(Foo._base_manager, PolymorphicManager)
        self.assertIsInstance(Bar._base_manager, PolymorphicManager)
        self.assertIsInstance(Baz._base_manager, PolymorphicManager)

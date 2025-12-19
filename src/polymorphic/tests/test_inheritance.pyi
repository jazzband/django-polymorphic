from django.test import TestCase
from polymorphic.managers import PolymorphicManager as PolymorphicManager
from polymorphic.tests.models import Bar as Bar, Baz as Baz, Foo as Foo

class InheritanceTests(TestCase):
    def test_mixin_inherited_managers(self) -> None: ...

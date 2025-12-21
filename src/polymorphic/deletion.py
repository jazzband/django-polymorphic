"""
Classes and utilities for handling deletions in polymorphic models.
"""

from django.db.migrations.serializer import BaseSerializer, serializer_factory
from django.db.migrations.writer import MigrationWriter

from .query import PolymorphicQuerySet


class PolymorphicGuard:
    """
    Wrap an :attr:`django.db.models.ForeignKey.on_delete` callable
    (CASCADE/PROTECT/SET_NULL/SET(...)/custom), but serialize as the underlying
    callable.

    :param action: The :attr:`django.db.models.ForeignKey.on_delete` callable to wrap.
    """

    def __init__(self, action):
        if not callable(action):
            raise TypeError("action must be callable")
        self.action = action

    def __call__(self, collector, field, sub_objs, using):
        """
        This guard wraps an on_delete action to ensure that any polymorphic queryset
        passed to it is converted to a non-polymorphic queryset before proceeding.
        This prevents issues with cascading deletes on polymorphic models.

        This guard should be automatically applied to reverse relations such that

        .. code-block:: python

            class MyModel(PolymorphicModel):
                related = models.ForeignKey(
                    OtherModel,
                    on_delete=models.CASCADE # <- equal to PolymorphicGuard(models.CASCADE)
                )

        """
        if isinstance(sub_objs, PolymorphicQuerySet) and not sub_objs.polymorphic_disabled:
            sub_objs = sub_objs.non_polymorphic()
        return self.action(collector, field, sub_objs, using)


class PolymorphicGuardSerializer(BaseSerializer):
    """
    A serializer for PolymorphicGuard that serializes the underlying action.

    There is no need to serialize the PolymorphicGuard itself, as it is just a wrapper
    that ensures that polymorphic querysets are converted to non-polymorphic but no
    polymorphic managers are present in migrations. This also ensures that new
    migrations will not be generated.
    """

    def serialize(self):
        """
        Serialize the underlying action of the PolymorphicGuard.
        """
        return serializer_factory(self.value.action).serialize()


MigrationWriter.register_serializer(PolymorphicGuard, PolymorphicGuardSerializer)

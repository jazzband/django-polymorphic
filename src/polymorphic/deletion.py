"""
Classes and utilities for handling deletions in polymorphic models.
"""

from functools import cached_property

from django.db.migrations.serializer import BaseSerializer, serializer_factory
from django.db.migrations.writer import MigrationWriter

from .query import PolymorphicQuerySet


def migration_fingerprint(value):
    """
    Produce a stable, hashable fingerprint for a value as Django would represent
    it in migrations, but in a structured form when possible.
    """
    # Canonical deconstruction path for SET(...), @deconstructible, etc.
    deconstruct = getattr(value, "deconstruct", None)
    if callable(deconstruct):
        path, args, kwargs = value.deconstruct()
        return (
            path,
            tuple(migration_fingerprint(a) for a in args),
            tuple(sorted((k, migration_fingerprint(v)) for k, v in kwargs.items())),
        )

    # Fallback: canonical "code string" Django would emit in a migration.
    # (Works for CASCADE/PROTECT/SET_NULL, primitives, etc.)
    code, _imports = serializer_factory(value).serialize()
    return code


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

    @cached_property
    def migration_key(self):
        return migration_fingerprint(self.action)

    def __eq__(self, other):
        if (
            isinstance(other, tuple)
            and len(other) == 3
            and callable(getattr(self.action, "deconstruct", None))
        ):
            # In some cases the autodetector compares us to a reconstructed,
            # deconstruct() tuple. This has been seen for SET(...) callables.
            # The arguments element may be a list instead of a tuple though, this
            # handles that special case
            return self.action.deconstruct() == (
                other[0],
                tuple(other[1]) if isinstance(other[1], list) else other[1],
                other[2],
            )
        if isinstance(other, PolymorphicGuard):
            return self.migration_key == other.migration_key
        else:
            try:
                return self.migration_key == migration_fingerprint(other)
            except Exception:
                return False

    def __hash__(self):
        return hash(self.migration_key)


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

"""
The manager class for use in the models.
"""

from __future__ import annotations

from collections.abc import Iterable
from typing import TYPE_CHECKING, Any, overload

from django.contrib.contenttypes.models import ContentType
from django.db import DEFAULT_DB_ALIAS, models, transaction
from typing_extensions import Self, TypeVar

from polymorphic.query import PolymorphicQuerySet

if TYPE_CHECKING:
    from .models import PolymorphicModel  # noqa: F401

__all__ = ["PolymorphicManager", "PolymorphicQuerySet"]

_T = TypeVar("_T", bound="PolymorphicModel", default="PolymorphicModel", covariant=True)
_A = TypeVar("_A", bound="PolymorphicModel")
_B = TypeVar("_B", bound="PolymorphicModel")
_C = TypeVar("_C", bound="PolymorphicModel")
_D = TypeVar("_D", bound="PolymorphicModel")


class PolymorphicManager(models.Manager[_T]):
    """
    Manager for PolymorphicModel

    Usually not explicitly needed, except if a custom manager or
    a custom queryset class is to be used.
    """

    queryset_class: type[PolymorphicQuerySet[_T]] = PolymorphicQuerySet

    if TYPE_CHECKING:

        def all(self) -> PolymorphicQuerySet[_T]: ...

    @classmethod
    def from_queryset(
        cls, queryset_class: type[models.query.QuerySet[_T, _T]], class_name: str | None = None
    ) -> type[Self]:
        manager = super().from_queryset(queryset_class, class_name=class_name)
        # also set our version, Django uses _queryset_class
        manager.queryset_class = queryset_class  # type: ignore[assignment]
        return manager

    def get_queryset(self) -> PolymorphicQuerySet[_T]:
        qs = self.queryset_class(self.model, using=self._db, hints=getattr(self, "_hints", None))
        if self.model._meta.proxy:
            qs = qs.instance_of(self.model)
        return qs

    def __str__(self) -> str:
        return (
            f"{self.__class__.__name__} (PolymorphicManager) using {self.queryset_class.__name__}"
        )

    # Proxied methods
    def non_polymorphic(self) -> PolymorphicQuerySet[_T]:
        return self.all().non_polymorphic()

    # fixme: remove overloads when/if typing ever supports variadic generic unions
    @overload
    def instance_of(self, __a: type[_A], /) -> PolymorphicQuerySet[_A]: ...

    @overload
    def instance_of(self, __a: type[_A], __b: type[_B], /) -> PolymorphicQuerySet[_A | _B]: ...

    @overload
    def instance_of(
        self, __a: type[_A], __b: type[_B], __c: type[_C], /
    ) -> PolymorphicQuerySet[_A | _B | _C]: ...

    @overload
    def instance_of(
        self, __a: type[_A], __b: type[_B], __c: type[_C], __d: type[_D], /
    ) -> PolymorphicQuerySet[_A | _B | _C | _D]: ...

    @overload
    def instance_of(self, *args: type[PolymorphicModel]) -> PolymorphicQuerySet[_T]: ...

    def instance_of(
        self: PolymorphicManager[_T], *args: type[PolymorphicModel]
    ) -> PolymorphicQuerySet["PolymorphicModel"]:
        return self.all().instance_of(*args)

    def not_instance_of(self, *args: type[PolymorphicModel]) -> PolymorphicQuerySet[_T]:
        return self.all().not_instance_of(*args)

    def get_real_instances(self, base_result_objects: Iterable[_T] | None = None) -> list[_T]:
        return self.all().get_real_instances(base_result_objects=base_result_objects)

    def create_from_super(self, obj: models.Model, **kwargs: Any) -> _T:
        """
        Create an instance of this manager's model class from the given instance of a
        parent class.

        This is useful when "promoting" an instance down the inheritance chain.

        :param obj: An instance of a parent class of the manager's model class.
        :param kwargs: Additional fields to set on the new instance.
        :return: The newly created instance.
        """
        from .models import PolymorphicModel

        with transaction.atomic(using=obj._state.db or DEFAULT_DB_ALIAS):
            # ensure we have the most derived real instance
            if isinstance(obj, PolymorphicModel):
                obj = obj.get_real_instance()

            parent_ptr = self.model._meta.parents.get(type(obj), None)

            if not parent_ptr:
                raise TypeError(
                    f"{obj.__class__.__name__} is not a direct parent of {self.model.__name__}"
                )
            kwargs[parent_ptr.get_attname()] = obj.pk  # type: ignore[union-attr]

            # create the new base class with only fields that apply to  it.
            ctype = ContentType.objects.db_manager(
                using=(obj._state.db or DEFAULT_DB_ALIAS)
            ).get_for_model(self.model)
            nobj = self.model(**kwargs, polymorphic_ctype=ctype)
            nobj.save_base(raw=True, using=obj._state.db or DEFAULT_DB_ALIAS, force_insert=True)
            # force update the content type, but first we need to
            # retrieve a clean copy from the db to fill in the null
            # fields otherwise they would be overwritten.
            if isinstance(obj, PolymorphicModel):
                parent = obj.__class__.objects.using(obj._state.db or DEFAULT_DB_ALIAS).get(
                    pk=obj.pk
                )
                parent.polymorphic_ctype = ctype
                parent.save()

            nobj.refresh_from_db()  # cast to cls
            return nobj

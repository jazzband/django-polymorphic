"""
The manager class for use in the models.
"""

import inspect

from django.contrib.contenttypes.models import ContentType
from django.db import DEFAULT_DB_ALIAS, models

from polymorphic.query import PolymorphicQuerySet

__all__ = ("PolymorphicManager", "PolymorphicQuerySet")


class PolymorphicManager(models.Manager):
    """
    Manager for PolymorphicModel

    Usually not explicitly needed, except if a custom manager or
    a custom queryset class is to be used.
    """

    queryset_class = PolymorphicQuerySet

    @classmethod
    def from_queryset(cls, queryset_class, class_name=None):
        manager = super().from_queryset(queryset_class, class_name=class_name)
        # also set our version, Django uses _queryset_class
        manager.queryset_class = queryset_class
        return manager

    def get_queryset(self):
        qs = self.queryset_class(self.model, using=self._db, hints=self._hints)
        if self.model._meta.proxy:
            qs = qs.instance_of(self.model)
        return qs

    def __str__(self):
        return (
            f"{self.__class__.__name__} (PolymorphicManager) using {self.queryset_class.__name__}"
        )

    # Proxied methods
    def non_polymorphic(self):
        return self.all().non_polymorphic()

    def instance_of(self, *args):
        return self.all().instance_of(*args)

    def not_instance_of(self, *args):
        return self.all().not_instance_of(*args)

    def get_real_instances(self, base_result_objects=None):
        return self.all().get_real_instances(base_result_objects=base_result_objects)

    def create_from_super(self, obj, **kwargs):
        """Creates an instance of self.model (cls) from existing super class.
        The new subclass will be the same object with same database id
        and data as obj, but will be an instance of cls.

        obj must be an instance of the direct superclass of cls.
        kwargs should contain all required fields of the subclass (cls).

        returns obj as an instance of cls.
        """
        cls = self.model

        scls = inspect.getmro(cls)[1]
        if scls is not type(obj):
            raise TypeError(
                "create_from_super can only be used if obj is one level of inheritance up from cls"
            )

        parent_link_field = None
        for parent, field in cls._meta.parents.items():
            if parent is scls:
                parent_link_field = field
                break
        if parent_link_field is None:
            raise TypeError(f"Could not find parent link field for {scls.__name__}")
        kwargs[parent_link_field.get_attname()] = obj.id

        # create the new base class with only fields that apply to  it.
        nobj = cls(**kwargs)
        nobj.save_base(raw=True)
        # force update the content type, but first we need to
        # retrieve a clean copy from the db to fill in the null
        # fields otherwise they would be overwritten.
        nobj = obj.__class__.objects.using(obj._state.db or DEFAULT_DB_ALIAS).get(pk=obj.pk)
        nobj.polymorphic_ctype = ContentType.objects.db_manager(
            using=(obj._state.db or DEFAULT_DB_ALIAS)
        ).get_for_model(cls)
        nobj.save()

        return nobj.get_real_instance()  # cast to cls

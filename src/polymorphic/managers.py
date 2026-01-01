"""
The manager class for use in the models.
"""

from django.contrib.contenttypes.models import ContentType
from django.db import DEFAULT_DB_ALIAS, models, transaction

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
            kwargs[parent_ptr.get_attname()] = obj.pk

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

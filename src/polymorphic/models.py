"""
Seamless Polymorphic Inheritance for Django Models
"""

import warnings

from django.contrib.contenttypes.models import ContentType
from django.db import models, transaction
from django.db.utils import DEFAULT_DB_ALIAS
from django.utils.functional import classproperty

from .base import PolymorphicModelBase
from .managers import PolymorphicManager
from .query_translate import translate_polymorphic_Q_object
from .utils import get_base_polymorphic_model, lazy_ctype

###################################################################################
# PolymorphicModel


class PolymorphicTypeUndefined(LookupError):
    pass


class PolymorphicTypeInvalid(RuntimeError):
    pass


class PolymorphicModel(models.Model, metaclass=PolymorphicModelBase):
    """
    Abstract base class that provides polymorphic behaviour
    for any model directly or indirectly derived from it.

    PolymorphicModel declares one field for internal use (:attr:`polymorphic_ctype`)
    and provides a polymorphic manager as the default manager (and as 'objects').
    """

    _meta_skip = True

    # for PolymorphicModelBase, so it can tell which models are polymorphic and which are not (duck typing)
    polymorphic_model_marker = True

    # for PolymorphicQuery, True => an overloaded __repr__ with nicer multi-line output is used by PolymorphicQuery
    polymorphic_query_multiline_output = False

    # avoid ContentType related field accessor clash (an error emitted by model validation)
    #: The model field that stores the :class:`~django.contrib.contenttypes.models.ContentType` reference to the actual class.
    polymorphic_ctype = models.ForeignKey(
        ContentType,
        null=True,
        editable=False,
        on_delete=models.CASCADE,
        related_name="polymorphic_%(app_label)s.%(class)s_set+",
    )

    # some applications want to know the name of the fields that are added to its models
    polymorphic_internal_model_fields = ["polymorphic_ctype"]

    objects = PolymorphicManager()

    class Meta:
        abstract = True

    @classproperty
    def polymorphic_primary_key_name(cls):
        """
        The name of the root primary key field of this polymorphic inheritance chain.
        """
        warnings.warn(
            "polymorphic_primary_key_name is deprecated and will be removed in "
            "version 5.0, use get_base_polymorphic_model(Model)._meta.pk.attname "
            "instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        return get_base_polymorphic_model(cls, allow_abstract=True)._meta.pk.attname

    @classmethod
    def translate_polymorphic_Q_object(cls, q):
        return translate_polymorphic_Q_object(cls, q)

    def pre_save_polymorphic(self, using=DEFAULT_DB_ALIAS):
        """
        Make sure the ``polymorphic_ctype`` value is correctly set on this model.

        This method automatically updates the polymorphic_ctype when:
        - The object is being saved for the first time
        - The object is being saved to a different database than it was loaded from

        This ensures cross-database saves work correctly without ForeignKeyViolation.
        """
        # This function may be called manually in special use-cases. When the object
        # is saved for the first time, we store its real class in polymorphic_ctype.
        # When the object later is retrieved by PolymorphicQuerySet, it uses this
        # field to figure out the real class of this object
        # (used by PolymorphicQuerySet._get_real_instances)

        # Update polymorphic_ctype if:
        # 1. It's not set yet (new object), OR
        # 2. The database has changed (cross-database save)
        needs_update = not self.polymorphic_ctype_id or (
            self._state.db and self._state.db != using
        )

        if needs_update:
            # Set polymorphic_ctype_id directly to avoid database router issues
            # when saving across databases
            ctype = ContentType.objects.db_manager(using).get_for_model(
                self, for_concrete_model=False
            )
            self.polymorphic_ctype_id = ctype.pk

    def save(self, *args, **kwargs):
        """Calls :meth:`pre_save_polymorphic` and saves the model."""
        # Determine the database to use:
        # 1. Explicit 'using' parameter takes precedence
        # 2. Otherwise use self._state.db (the database the object was loaded from)
        # 3. Fall back to DEFAULT_DB_ALIAS
        # This ensures database routers are respected when no explicit database is specified
        using = kwargs.get("using")
        if using is None:
            using = self._state.db or DEFAULT_DB_ALIAS

        self.pre_save_polymorphic(using=using)
        return super().save(*args, **kwargs)

    save.alters_data = True

    def get_real_instance_class(self):
        """
        Return the actual model type of the object.

        If a non-polymorphic manager (like base_objects) has been used to
        retrieve objects, then the real class/type of these objects may be
        determined using this method.
        """
        if self.polymorphic_ctype_id is None:
            raise PolymorphicTypeUndefined(
                f"The model {self.__class__.__name__}#{self.pk} does not have a `polymorphic_ctype_id` value defined.\n"
                f"If you created models outside polymorphic, e.g. through an import or migration, "
                f"make sure the `polymorphic_ctype_id` field points to the ContentType ID of the model subclass."
            )

        # the following line would be the easiest way to do this, but it produces sql queries
        # return self.polymorphic_ctype.model_class()
        # so we use the following version, which uses the ContentType manager cache.
        # Note that model_class() can return None for stale content types;
        # when the content type record still exists but no longer refers to an existing model.
        model = (
            ContentType.objects.db_manager(self._state.db)
            .get_for_id(self.polymorphic_ctype_id)
            .model_class()
        )

        # Protect against bad imports (dumpdata without --natural) or other
        # issues missing with the ContentType models.
        if (
            model is not None
            and not issubclass(model, self.__class__)
            and (
                self.__class__._meta.proxy_for_model is None
                or not issubclass(model, self.__class__._meta.proxy_for_model)
            )
        ):
            raise PolymorphicTypeInvalid(
                f"ContentType {self.polymorphic_ctype_id} for {model} #{self.pk} does "
                "not point to a subclass!"
            )

        return model

    def get_real_concrete_instance_class_id(self):
        model_class = self.get_real_instance_class()
        if model_class is None:
            return None
        return (
            ContentType.objects.db_manager(self._state.db)
            .get_for_model(model_class, for_concrete_model=True)
            .pk
        )

    def get_real_concrete_instance_class(self):
        model_class = self.get_real_instance_class()
        if model_class is None:
            return None
        return (
            ContentType.objects.db_manager(self._state.db)
            .get_for_model(model_class, for_concrete_model=True)
            .model_class()
        )

    def get_real_instance(self):
        """
        Upcast an object to it's actual type.

        If a non-polymorphic manager (like base_objects) has been used to
        retrieve objects, then the complete object with it's real class/type
        and all fields may be retrieved with this method.

        If the model of the object's actual type does not exist (i.e. its
        ContentType is stale), this method raises a
        :class:`~polymorphic.models.PolymorphicTypeInvalid` exception.

        .. note::
            Each method call executes one db query (if necessary).
            Use the :meth:`~polymorphic.managers.PolymorphicQuerySet.get_real_instances`
            to upcast a complete list in a single efficient query.
        """
        real_model = self.get_real_instance_class()
        if real_model is self.__class__:
            return self
        if real_model is None:
            raise PolymorphicTypeInvalid(
                f"ContentType {self.polymorphic_ctype_id} for {self.__class__} "
                f"#{self.pk} does not have a corresponding model!"
            )
        return self.__class__.objects.db_manager(self._state.db).get(pk=self.pk)

    def delete(self, using=None, keep_parents=False):
        """
        Behaves the same as Django's default :meth:`~django.db.models.Model.delete()`,
        but with support for upcasting when ``keep_parents`` is True. When keeping
        parents (upcasting the row) the ``polymorphic_ctype`` fields of the parent rows
        are updated accordingly in a transaction with the child row deletion.
        """
        # if we are keeping parents, we must first determine which polymorphic_ctypes we
        # need to update
        parent_updates = (
            [
                (parent_model, getattr(self, parent_field.get_attname()))
                for parent_model, parent_field in self._meta.parents.items()
                if issubclass(parent_model, PolymorphicModel)
            ]
            if keep_parents
            else []
        )
        if parent_updates:
            with transaction.atomic(using=using):
                # If keeping the parents (upcasting) we need to update the relevant
                # content types for all parent inheritance paths.
                ret = super().delete(using=using, keep_parents=keep_parents)
                for parent_model, pk in parent_updates:
                    parent_model.objects.db_manager(using=using).non_polymorphic().filter(
                        pk=pk
                    ).update(polymorphic_ctype=lazy_ctype(parent_model, using=using))
                return ret
        return super().delete(using=using, keep_parents=keep_parents)

    delete.alters_data = True

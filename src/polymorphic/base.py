"""
PolymorphicModel Meta Class
"""

import sys
import warnings

from django.db import models
from django.db.models.base import ModelBase
from django.db.models.options import Options

from .deletion import PolymorphicGuard
from .managers import PolymorphicManager
from .related_descriptors import (
    NonPolymorphicForwardOneToOneDescriptor,
    NonPolymorphicReverseOneToOneDescriptor,
)
from .utils import _clear_utility_caches

# PolymorphicQuerySet Q objects (and filter()) support these additional key words.
# These are forbidden as field names (a descriptive exception is raised)
POLYMORPHIC_SPECIAL_Q_KWORDS = {"instance_of", "not_instance_of"}


class ManagerInheritanceWarning(RuntimeWarning):
    pass


# check that we're on cpython to enable dumpdata frame inspection guard
check_dump = hasattr(sys, "_getframe")


# We wrap the base_manager property to return a PolymorphicManager
# for polymorphic models when the base manager would otherwise
# be the default auto-created manager. This ensures that
# reverse relations to polymorphic models also use polymorphic
# querysets by default.
# https://github.com/jazzband/django-polymorphic/pull/858
dj_base_manager = Options.base_manager.func


def polymorphic_base_manager(self):
    """
    Return a polymorphic base manager for polymorphic models.
    """
    from polymorphic.models import PolymorphicModel

    mgr = dj_base_manager(self)
    if (
        issubclass(self.model, PolymorphicModel)
        and mgr.__class__ is models.Manager
        and mgr.auto_created
    ):
        manager = PolymorphicManager()
        manager.name = "_base_manager"
        manager.model = self.model
        manager.auto_created = True
        return manager
    return mgr


Options.base_manager.func = polymorphic_base_manager


class PolymorphicModelBase(ModelBase):
    """
    Manager inheritance is a pretty complex topic which may need
    more thought regarding how this should be handled for polymorphic
    models.

    In any case, we probably should propagate 'objects' and 'base_objects'
    from PolymorphicModel to every subclass. We also want to somehow
    inherit/propagate _default_manager as well, as it needs to be polymorphic.

    The current implementation below is an experiment to solve this
    problem with a very simplistic approach: We unconditionally
    inherit/propagate any and all managers (using _copy_to_model),
    as long as they are defined on polymorphic models
    (the others are left alone).

    Like Django ModelBase, we special-case _default_manager:
    if there are any user-defined managers, it is set to the first of these.

    We also require that _default_manager as well as any user defined
    polymorphic managers produce querysets that are derived from
    PolymorphicQuerySet.

    We also replace the parent/child relation field descriptors with versions that will
    use non-polymorphic querysets.

    If we have inheritance of the form ModelA -> ModelB ->ModelC then
    Django creates accessors like this:
    - ModelA: modelb
    - ModelB: modela_ptr, modelb, modelc
    - ModelC: modela_ptr, modelb, modelb_ptr, modelc

    These accessors allow Django (and everyone else) to travel up and down
    the inheritance tree for the db object at hand. This is important for deletion among
    other things.
    """

    def __new__(cls, model_name, bases, attrs, **kwargs):
        # skip special setup for PolymorphicModel itself
        if attrs.pop("_meta_skip", False):
            return super().__new__(cls, model_name, bases, attrs, **kwargs)

        from .models import PolymorphicModel

        new_class = super().__new__(cls, model_name, bases, attrs, **kwargs)

        # wrap on_delete handlers of reverse relations back to this model with the
        # polymorphic deletion guard
        for fk in new_class._meta.fields:
            if isinstance(fk, (models.ForeignKey, models.OneToOneField)) and not isinstance(
                fk.remote_field.on_delete, PolymorphicGuard
            ):
                fk.remote_field.on_delete = PolymorphicGuard(fk.remote_field.on_delete)

        # replace the parent/child descriptors
        if new_class._meta.parents and not (new_class._meta.abstract or new_class._meta.proxy):

            def replace_inheritance_descriptors(model):
                for super_cls, field_to_super in model._meta.parents.items():
                    if issubclass(super_cls, PolymorphicModel):
                        if field_to_super is not None:
                            setattr(
                                new_class,
                                field_to_super.name,
                                NonPolymorphicForwardOneToOneDescriptor(field_to_super),
                            )
                            setattr(
                                super_cls,
                                field_to_super.remote_field.related_name
                                or field_to_super.remote_field.name,
                                NonPolymorphicReverseOneToOneDescriptor(
                                    field_to_super.remote_field
                                ),
                            )
                        else:  # pragma: no cover
                            # proxy models have no field_to_super because the relations
                            # are to the parent model - the else here should never
                            # happen b/c we filter out proxy models above
                            pass
                        replace_inheritance_descriptors(super_cls)

            replace_inheritance_descriptors(new_class)
        _clear_utility_caches()
        return new_class

    @property
    def base_objects(self):
        warnings.warn(
            "Using PolymorphicModel.base_objects is deprecated.\n"
            f"Use {self.__class__.__name__}.objects.non_polymorphic() instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        return self._base_objects

    @property
    def _base_objects(self):
        # Create a manager so the API works as expected. Just don't register it
        # anymore in the Model Meta, so it doesn't substitute our polymorphic
        # manager as default manager for the third level of inheritance when
        # that third level doesn't define a manager at all.
        manager = models.Manager()
        manager.name = "base_objects"
        manager.model = self
        return manager

    @property
    def _default_manager(cls):
        mgr = super()._default_manager
        if (
            check_dump
            and sys._getframe(1).f_globals.get("__name__")
            == "django.core.management.commands.dumpdata"
        ):
            # The downcasting of polymorphic querysets breaks dumpdata because it
            # expects to serialize multi-table models at each inheritance level.
            # dumpdata uses Model._default_manager to retrieve the objects by default
            # and uses Model._base_manager to retrieve objects if the --all flag is
            # specified. We need to make both of these managers polymorphic to satisfy
            # our contract that both Model.objects (_default_manager) is polymorphic and
            # reverse relations Other.related (_base_manager) to our polymorphic models
            # are also polymorphic.
            #
            # It would be best if load/dump data constructed its own managers like
            # migrations do, but it doesn't. The only way to get around this is to
            # detect when dumpdata is running and return the non-polymorphic manager in
            # that case. We do this here by inspecting the call stack and checking if
            # it came from the dumpdata command module. We use a CPython specific API
            # sys._getframe to inspect the call stack because it is very fast
            # (10s of nanoseconds) and disable the check if not on CPython
            # conceding that dumpdata will just not work in that case. It is important
            # that this check be fast because _default_manager is accessed very often.
            # inspect.stack() builds the entire stack frame and a bunch of complicated
            # datastructures - its use here should be avoided.
            #
            # Note that if you are stepping through this code in the debugger it will
            # be looking at the wrong frame because a bunch of debugging frames will be
            # on the top of the stack.
            return mgr.non_polymorphic() if isinstance(mgr, PolymorphicManager) else mgr
        return mgr

    @property
    def _base_manager(cls):
        mgr = super()._base_manager
        if (
            check_dump
            and sys._getframe(1).f_globals.get("__name__")
            == "django.core.management.commands.dumpdata"
        ):
            # base manager is used when the --all flag is passed - see analogous comment
            # for _default_manager
            return mgr.non_polymorphic() if isinstance(mgr, PolymorphicManager) else mgr
        return mgr

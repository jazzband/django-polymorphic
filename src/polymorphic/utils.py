from django.contrib.contenttypes.models import ContentType
from django.db import DEFAULT_DB_ALIAS

from polymorphic.base import PolymorphicModelBase
from polymorphic.models import PolymorphicModel


def reset_polymorphic_ctype(*models, **filters):
    """
    Set the polymorphic content-type ID field to the proper model
    Sort the ``*models`` from base class to descending class,
    to make sure the content types are properly assigned.

    Add ``ignore_existing=True`` to skip models which already
    have a polymorphic content type.
    """
    using = filters.pop("using", DEFAULT_DB_ALIAS)
    ignore_existing = filters.pop("ignore_existing", False)

    models = sort_by_subclass(*models)
    if ignore_existing:
        # When excluding models, make sure we don't ignore the models we
        # just assigned the an content type to. hence, start with child first.
        models = reversed(models)

    for new_model in models:
        new_ct = ContentType.objects.db_manager(using).get_for_model(
            new_model, for_concrete_model=False
        )

        qs = new_model.objects.db_manager(using)
        if ignore_existing:
            qs = qs.filter(polymorphic_ctype__isnull=True)
        if filters:
            qs = qs.filter(**filters)
        qs.update(polymorphic_ctype=new_ct)


def _compare_mro(cls1, cls2):
    if cls1 is cls2:
        return 0

    try:
        index1 = cls1.mro().index(cls2)
    except ValueError:
        return -1  # cls2 not inherited by 1

    try:
        index2 = cls2.mro().index(cls1)
    except ValueError:
        return 1  # cls1 not inherited by 2

    return (index1 > index2) - (index1 < index2)  # python 3 compatible cmp.


def sort_by_subclass(*classes):
    """
    Sort a series of models by their inheritance order.
    """
    from functools import cmp_to_key

    return sorted(classes, key=cmp_to_key(_compare_mro))


def get_base_polymorphic_model(ChildModel, allow_abstract=False):
    """
    First the first concrete model in the inheritance chain that inherited from the PolymorphicModel.
    """
    for Model in reversed(ChildModel.mro()):
        if (
            isinstance(Model, PolymorphicModelBase)
            and Model is not PolymorphicModel
            and (allow_abstract or not Model._meta.abstract)
        ):
            return Model
    return None


def prepare_for_copy(obj):
    """
    Prepare a model instance for copying by resetting all primary keys and parent table
    pointers in the inheritance chain. **Copy semantics are application specific.** This
    function only resets the fields required to create a new instance when saved, it
    does not deep copy related objects or save the new instance
    (See :ref:`copying discussion in the Django documentation.
    <topics/db/queries:copying model instances>`):

    .. code-block:: python

        from polymorphic.utils import prepare_for_copy

        original = YourModel.objects.get(pk=1)
        prepare_for_copy(original)
        # update any related fields here as needed
        original.save()  # creates a new object in the database

    .. tip::

        Preparation is at the inheritance level of the passed in model. This means you
        can copy and upcast at the same time. Suppose you have A->B->C inheritance chain,
        and you have an instance of C that you want to copy as a B instance:

        .. code-block:: python

            c = C.objects.create()
            c_as_b = B.objects.non_polymorphic().get(pk=c.pk)

            # copy c as a b instance
            prepare_for_copy(c_as_b)
            c_as_b.save()

            assert B.objects.count() == 2
            assert C.objects.count() == 1

        If you want polymorphic copying instead:

        .. code-block:: python

            prepare_for_copy(b_instance.get_real_instance())

    **This function also works for non-polymorphic multi-table models.**

    :param obj: The model instance to prepare for copying.
    """
    obj.pk = None
    if isinstance(obj, PolymorphicModel):
        # we might be upcasting - allow ctype to be reset automatically on save
        obj.polymorphic_ctype_id = None

    def reset_parent_pointers(mdl):
        """
        Reset all parent table pointers and pks in the inheritance chain.
        """
        for parent, ptr in mdl._meta.parents.items():
            reset_parent_pointers(parent)
            if ptr is not None:
                setattr(obj, ptr.attname, None)
                setattr(obj, parent._meta.pk.attname, None)

    reset_parent_pointers(obj)
    obj._state.adding = True  # Mark as new object

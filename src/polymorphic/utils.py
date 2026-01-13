from collections import defaultdict
from dataclasses import dataclass
from functools import lru_cache

from django.apps import apps
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import FieldError
from django.db import DEFAULT_DB_ALIAS, models
from django.db.models import Q, Subquery


@dataclass(frozen=True)
class ParentLinkInfo:
    """
    Information about a parent table link in a polymorphic model.
    """

    model: models.Model
    link: models.Field


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


@lru_cache(maxsize=None)
def get_base_polymorphic_model(ChildModel, allow_abstract=False):
    """
    First the first concrete model in the inheritance chain that inherited from the
    PolymorphicModel.
    """
    from polymorphic.models import PolymorphicModel

    for Model in reversed(ChildModel.mro()):
        if (
            issubclass(Model, PolymorphicModel)
            and Model is not PolymorphicModel
            and (allow_abstract or not Model._meta.abstract)
        ):
            return Model
    return None


@lru_cache(maxsize=None)
def route_to_ancestor(model_class, ancestor_model):
    """
    Returns the first (highest mro precedence - depth first on parents) model
    inheritance route to the given ancestor model - or an empty list if no such
    route exists. Results are cached

    .. warning::

        This only works for concrete ancestors!

    Returns a :class:`list` of :class:`ParentLinkInfo`
    """
    route = []

    def find_route(model, target_model, current_route):
        if model is target_model:
            return current_route

        for parent_model, field_to_parent in model._meta.parents.items():
            if field_to_parent is not None:
                new_route = current_route + [ParentLinkInfo(parent_model, field_to_parent)]
                found_route = find_route(parent_model, target_model, new_route)
                if found_route is not None:
                    return found_route
            else:
                return find_route(parent_model, target_model, current_route)
        return None

    found_route = find_route(model_class, ancestor_model, route)
    if found_route is None:
        return []
    return found_route


def is_model_loaded(model):
    try:
        apps.get_model(model._meta.app_label, model._meta.model_name)
        return True
    except LookupError:
        return False


@lru_cache(maxsize=None)
def concrete_descendants(model_class, include_proxy=False):
    """
    Get a list of all concrete (non-abstract, non-proxy) descendant model classes in
    tree order with leaf descendants last. Results are cached.
    """
    from django.apps import apps

    apps.check_models_ready()

    def add_concrete_descendants(model, result):
        """Add concrete descendants in tree order (ancestors before descendants)."""
        for sub_cls in model.__subclasses__():
            # Add concrete models in pre-order (parent before children)
            if not sub_cls._meta.abstract and (include_proxy or not sub_cls._meta.proxy):
                if is_model_loaded(sub_cls):
                    result.append(sub_cls)

            # Always recurse to find descendants through abstract and proxy models
            add_concrete_descendants(sub_cls, result)

    result = []
    add_concrete_descendants(model_class, result)
    return result


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
    from polymorphic.models import PolymorphicModel

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


def _lazy_ctype(model, using=DEFAULT_DB_ALIAS):
    """
    Return the content type id for the given model class if it is in the cache,
    otherwise return a subquery that can be used to match the content type as part
    of a larger query. Safe to call before apps are fully loaded.

    :param model: The model class to get the content type for.
    :return: The content type for the model class.
    :rtype: int or Subquery
    """
    mgr = ContentType.objects.db_manager(using=using)
    if apps.models_ready and (
        cid := mgr._cache.get(using, {}).get((model._meta.app_label, model._meta.model_name))
    ):
        return cid
    return Q(app_label=model._meta.app_label) & Q(model=model._meta.model_name)


def lazy_ctype(model, using=DEFAULT_DB_ALIAS):
    ctype = _lazy_ctype(model, using=using)
    return (
        ctype
        if isinstance(ctype, ContentType)
        else Subquery(ContentType.objects.db_manager(using=using).filter(ctype).values("pk")[:1])
    )


@lru_cache(maxsize=None)
def _map_queryname_to_class(base_model, qry_name):
    """Try to match a model name in a query to a model class"""
    name_map = defaultdict(list)
    name_map[base_model.__name__.lower()].append(base_model)
    for cls in concrete_descendants(base_model, include_proxy=True):
        name_map[cls.__name__.lower()].append(cls)

    matches = name_map.get(qry_name.lower(), [])
    if len(matches) == 1:
        return matches[0]
    elif len(matches) > 1:
        raise FieldError(
            f"{qry_name} could refer to any of {[m._meta.label for m in matches]}. In "
            f"this case, please use the syntax: applabel__ModelName___field"
        )

    # FIXME: raise a FieldError - upstream code currently relies on this AssertionError
    # and it will be thrown in legitimate cases because this function ends up being
    # called on subclasses of the original query model in _get_real_instances. That
    # code should be refactored to avoiid this.
    raise AssertionError(f"{qry_name} is not a subclass of {base_model._meta.label}")


def _clear_utility_caches():
    """Clear all lru_cache caches in this module."""
    get_base_polymorphic_model.cache_clear()
    route_to_ancestor.cache_clear()
    concrete_descendants.cache_clear()
    _map_queryname_to_class.cache_clear()

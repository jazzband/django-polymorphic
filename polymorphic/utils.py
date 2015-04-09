import weakref

from django.db.backends import util
from django.db.models.query_utils import DeferredAttribute


def transmogrify(cls, obj):
    """
    Upcast a class to a different type without asking questions.
    """
    # Run constructor, reassign values
    new = cls()
    for k, v in obj.__dict__.items():
        new.__dict__[k] = v
    new.pk = obj.pk
    return new


def get_roots(model_class, only_roots=False):
    result = set()
    for parent in model_class._meta.parents:
        roots = get_roots(parent)
        if roots:
            result.update(roots)
        elif not only_roots or not parent._meta.parents:
            result.add(parent)
    return result


def get_related_fields(real_model, field=None):
    """
    This helper function returns a set of attribute names
    related to a given field (or the primary key) of a real_model.

    For example, if no field parameter is passed it uses the pk, and figures
    out what other field name attributes point to the same value pk points to.

    """
    field = real_model._meta.pk
    roots = get_roots(real_model, only_roots=True)
    common = set()
    for root in get_roots(real_model):
        child = real_model
        for parent in real_model._meta.get_base_chain(root):
            rel_field = child._meta.get_ancestor_link(parent)
            if rel_field == field:
                child = parent
                if child in roots:
                    common.add(rel_field)
                    common.add(rel_field.related_field)
                    break
    return common


class BulkDeferredAttribute(DeferredAttribute):
    def __init__(self, field_name, model):
        self.field_name = field_name
        self.model_ref = weakref.ref(model)

    def _query_filters(self, instance):
        non_deferred_model = instance._meta.proxy_for_model
        opts = non_deferred_model._meta
        val = None
        for root in get_roots(non_deferred_model):
            child = non_deferred_model
            for parent in non_deferred_model._meta.get_base_chain(root):
                rel_field = child._meta.get_ancestor_link(parent)
                if rel_field:
                    child = parent
                    name = rel_field.related_field.name
                    f = opts.get_field_by_name(name)[0]
                    if f.primary_key and f != rel_field:
                        if not isinstance(instance.__class__.__dict__.get(rel_field.attname), BulkDeferredAttribute):
                            val = getattr(instance, rel_field.attname)
                            return {rel_field.name: val}

    def __get__(self, instance, owner):
        """
        Retrieves and caches the value from the datastore on the first lookup.
        Returns the cached value.
        """
        non_deferred_model = instance._meta.proxy_for_model

        assert instance is not None
        data = instance.__dict__
        if data.get(self.field_name, self) is self:
            fields = {}
            for field in non_deferred_model._meta.fields:
                field_name = field.attname
                if isinstance(instance.__class__.__dict__.get(field_name), BulkDeferredAttribute):
                    fields[field_name] = field.name
            # We use only() instead of values() here because we want the
            # various data coersion methods (to_python(), etc.) to be called
            # here.
            if fields and self.field_name in fields:
                # Find out a suitable filter value to get the object.
                filters = self._query_filters(instance)
                obj = non_deferred_model._base_manager.only(*fields.values()).using(
                    instance._state.db).get(**filters)
                for field_name in fields.keys():
                    val = getattr(obj, field_name)
                    data[field_name] = val
        try:
            return data[self.field_name]
        except KeyError:
            # Fallback to try the real object's getattr:
            obj = transmogrify(non_deferred_model, instance)
            return getattr(obj, self.field_name)

    def __set__(self, instance, value):
        """
        Deferred loading attributes can be set normally (which means there will
        never be a database lookup involved.
        """
        cls = self.model_ref()
        for field in cls._meta.fields:
            if field.attname == self.field_name:
                if hasattr(field, '__set__'):
                    field.__set__(instance, value)
                    if hasattr(field, '__get__'):
                        value = field.__get__(instance, cls)
                break
        instance.__dict__[self.field_name] = value


def deferred_class_factory(model, attrs, bulk_attrs):
    """
    Returns a class object that is a copy of "model" with the specified "attrs"
    being replaced with BulkDeferredAttribute objects. The "pk_value" ties the
    deferred attributes to a particular instance of the model.
    """
    if not attrs:
        attrs = set()

    if not bulk_attrs:
        bulk_attrs = set()

    class Meta:
        proxy = True
        app_label = model._meta.app_label

    # The app_cache wants a unique name for each model, otherwise the new class
    # won't be created (we get an old one back). Therefore, we generate the
    # name using the passed in attrs. It's OK to reuse an existing class
    # object if the attrs are identical.
    name = "%s_Polymorphic_%s" % (model.__name__, '_'.join(sorted(list(attrs | bulk_attrs))))
    name = util.truncate_name(name, 80, 32)

    overrides = dict([(attr, BulkDeferredAttribute(attr, model)) for attr in bulk_attrs - attrs])
    overrides.update(dict([(attr, DeferredAttribute(attr, model)) for attr in attrs]))
    overrides["Meta"] = Meta
    overrides["__module__"] = model.__module__
    overrides["_deferred"] = True
    return type(str(name), (model,), overrides)

# The above function is also used to unpickle model instances with deferred
# fields.
deferred_class_factory.__safe_for_unpickling__ = True

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


class BulkDeferredAttribute(DeferredAttribute):
    def __init__(self, field_name, model, parent):
        self.field_name = field_name
        self.model_ref = weakref.ref(model)
        self.parent_ref = weakref.ref(parent)

    def __get__(self, instance, owner):
        """
        Retrieves and caches the value from the datastore on the first lookup.
        Returns the cached value.
        """
        non_deferred_model = instance._meta.proxy_for_model
        opts = non_deferred_model._meta

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
                parent = self.parent_ref()
                rel_field = opts.get_ancestor_link(parent._meta.proxy_for_model or parent)
                val = self._check_parent_chain(instance, rel_field.related_field.name)
                filters = {rel_field.name: val}
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


def deferred_class_factory(model, parent, attrs, bulk_attrs):
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
    name = "%s_Deferred_%s" % (model.__name__, '_'.join(sorted(list(attrs | bulk_attrs))))
    name = util.truncate_name(name, 80, 32)

    overrides = dict([(attr, BulkDeferredAttribute(attr, model, parent)) for attr in bulk_attrs - attrs])
    overrides.update(dict([(attr, DeferredAttribute(attr, model)) for attr in attrs]))
    overrides["Meta"] = Meta
    overrides["__module__"] = model.__module__
    overrides["_deferred"] = True
    return type(str(name), (model,), overrides)

# The above function is also used to unpickle model instances with deferred
# fields.
deferred_class_factory.__safe_for_unpickling__ = True

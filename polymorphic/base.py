# -*- coding: utf-8 -*-
from __future__ import absolute_import

import weakref

import django
from django.db import models
from django.db.models.query_utils import DeferredAttribute
from django.db.models.base import ModelBase
from django.db.models.fields.related import SingleRelatedObjectDescriptor, ReverseSingleRelatedObjectDescriptor
from django.contrib.contenttypes.models import ContentType

from .query import PolymorphicSingleRelatedObjectDescriptor, PolymorphicReverseSingleRelatedObjectDescriptor, polymorphic
from .utils import deferred_class_factory, get_roots


class PolymorphicModelBase(ModelBase):
    def __new__(cls, name, bases, attrs):
        super_new = super(PolymorphicModelBase, cls).__new__

        # six.with_metaclass() inserts an extra class called 'NewBase' in the
        # inheritance tree: Model -> NewBase -> object. But the initialization
        # should be executed only once for a given model class.

        # attrs will never be empty for classes declared in the standard way
        # (ie. with the `class` keyword). This is quite robust.
        if name == 'NewBase' and attrs == {}:
            if django.VERSION < (1, 5):
                # Let Django fully ignore the class which is inserted in between.
                # Django 1.5 fixed this, see https://code.djangoproject.com/ticket/19688
                attrs['__module__'] = 'django.utils.six'
                attrs['Meta'] = type('Meta', (), {'abstract': True})
            return super_new(cls, name, bases, attrs)

        # Also ensure initialization is only performed for subclasses of Model
        # (excluding Model class itself).
        parents = [b for b in bases if isinstance(b, ModelBase) and b.__name__ != 'NewBase']
        if not parents:
            return super_new(cls, name, bases, attrs)

        # Find out if the polymorphic class can be a proxy.
        is_proxy = True
        inherit_managers = False

        if is_proxy:
            attr_meta = attrs.get('Meta', None)
            abstract = getattr(attr_meta, 'abstract', False)
            if abstract:
                is_proxy = False

        if is_proxy:
            base = None
            for parent in [p for p in parents if hasattr(p, '_meta')]:
                if parent._meta.abstract:
                    if parent._meta.fields:
                        is_proxy = False  # Abstract parent classes with fields cannot be proxied
                        break
                if base is not None:
                    is_proxy = False
                    inherit_managers = True
                    break
                else:
                    base = parent
            if base is None:
                is_proxy = False

        if is_proxy:
            fields = [f for f in attrs.values() if isinstance(f, models.Field)]
            if fields:
                is_proxy = False

        if is_proxy:
            if 'Meta' in attrs:
                parent = (attrs['Meta'], object,)
            else:
                parent = (object,)
            meta = type('Meta', parent, {'proxy': True})
            attrs['Meta'] = meta

        # Create the class.
        new_class = super_new(cls, name, bases, attrs)
        opts = new_class._meta

        # Add instance_of to parents
        opts.instance_of = set([weakref.ref(new_class)])
        if not new_class._deferred and \
           not opts.abstract and \
           not opts.auto_created and \
           not opts.swapped:
            for b in opts.get_parent_list():
                if hasattr(b._meta, 'instance_of'):
                    b._meta.instance_of.add(weakref.ref(new_class))

        # Polymorphic classes inherit parent's default manager, if none is
        # set explicitly.
        if inherit_managers:
            _default_manager = None
            _base_manager = None
            for parent in parents:
                _default_manager = _default_manager or getattr(parent, '_default_manager')
                _base_manager = _base_manager or getattr(parent, '_base_manager')

            if _default_manager:
                new_class._default_manager = _default_manager._copy_to_model(new_class)
            if _base_manager:
                new_class._base_manager = _base_manager._copy_to_model(new_class)

        return new_class

    def __call__(cls, *args, **kwargs):
        polymorphic_disabled = getattr(polymorphic, 'disabled', False)

        if args and not kwargs and not polymorphic_disabled:
            fields_attrs = [f.attname for f in cls._meta.concrete_fields]

            # Build kwargs from args.
            kwargs = dict(zip(fields_attrs, args))

            # Get the polymorphic child model class.
            polymorphic_ctype_id = args[fields_attrs.index('polymorphic_ctype_id')]
            real_model = ContentType.objects.get_for_id(polymorphic_ctype_id).model_class()

            if not issubclass(real_model, cls):
                raise TypeError("expected a subclass of %s (got %s class instead)" % (cls._meta.object_name, real_model._meta.object_name))

            # Descriptors patching must be done as late as possible,
            # but only once for each polymorphic model.
            if not hasattr(real_model, '_polymorphic_descriptors'):
                # Inheritance creates a ForeignKey to it's parent model by appending
                # ``_ptr`` to the ``model_name``, and a reverse to ``model_name``.
                # In those cases, a real (non-polymorphic) object must be returned by
                # the descriptors. Use our polymorphic ``SingleRelatedObjectDescriptor``
                # and ``ReverseSingleRelatedObjectDescriptor``.
                for n, f in real_model.__dict__.items():
                    if isinstance(f, SingleRelatedObjectDescriptor) and not isinstance(f, PolymorphicSingleRelatedObjectDescriptor):
                        if n == f.related.model._meta.model_name:
                            setattr(real_model, n, PolymorphicSingleRelatedObjectDescriptor(f.related))
                    elif isinstance(f, ReverseSingleRelatedObjectDescriptor) and not isinstance(f, PolymorphicReverseSingleRelatedObjectDescriptor):
                        if n == '%s_ptr' % f.field.rel.to._meta.model_name:
                            setattr(real_model, n, PolymorphicReverseSingleRelatedObjectDescriptor(f.field))
                real_model._polymorphic_descriptors = True

            # Figure out if it has to defer field loading.
            skip = set(f.field_name for f in cls.__dict__.values() if isinstance(f, DeferredAttribute))
            bulk_skip = set(f.attname for f in real_model._meta.concrete_fields) - set(fields_attrs)

            # Figure out all ancestors (and remove them from the bulk loading)
            modelclass = cls._meta.proxy_for_model or cls
            for root in get_roots(real_model):
                child = real_model
                for parent in real_model._meta.get_base_chain(root):
                    rel_field = child._meta.get_ancestor_link(parent)
                    if rel_field:
                        child = parent
                        if child == modelclass:
                            ancestor_pk = kwargs[rel_field.related_field.attname]
                            kwargs[rel_field.attname] = ancestor_pk
                            kwargs[rel_field.related_field.attname] = ancestor_pk
                            bulk_skip.discard(rel_field.attname)
                            bulk_skip.discard(rel_field.related_field.attname)
                            break

            if skip or bulk_skip:
                real_model = deferred_class_factory(real_model, skip, bulk_skip)

            instance = real_model(**kwargs)

            # Main class pk attribute might not have ended with a valid value in
            # multiple inheritance where there may be multiple fields with the
            # same ``id`` attribute (only the first one gets set, popped out of
            # kwargs by ``__init__``, and the following get the default ``None``).
            setattr(instance, cls._meta.pk.attname, kwargs[cls._meta.pk.attname])

        else:
            instance = super(PolymorphicModelBase, cls).__call__(*args, **kwargs)
            if not instance.polymorphic_ctype_id:
                instance.polymorphic_ctype = instance.get_polymorphic_ctype()

        return instance

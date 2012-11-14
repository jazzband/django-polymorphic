# -*- coding: utf-8 -*-
"""
Seamless Polymorphic Inheritance for Django Models

Copyright:
This code and affiliated files are (C) by Bert Constantin and individual contributors.
Please see LICENSE and AUTHORS for more information.
"""
from polymorphic_model import PolymorphicModel
from manager import PolymorphicManager
from query import PolymorphicQuerySet
from query_translate import translate_polymorphic_Q_object
from showfields import ShowFieldContent, ShowFieldType, ShowFieldTypeAndContent
from showfields import ShowFields, ShowFieldTypes, ShowFieldsAndTypes  # import old names for compatibility


VERSION = (1, 0, 0, 'beta')


def get_version():
    version = '%s.%s' % VERSION[0:2]
    if VERSION[2]:
        version += '.%s' % VERSION[2]
    if VERSION[3]:
        version += ' %s' % VERSION[3]
    return version

from django.contrib.contenttypes.models import ContentTypeManager
from django.utils.encoding import smart_unicode


# Monkey-patch Django to allow ContentTypes for proxy models. This is compatible with an
# upcoming change in Django 1.5 and should be removed when we upgrade. There is a test
# in MonkeyPatchTests that checks for this.
# https://code.djangoproject.com/ticket/18399

def get_for_model(self, model, for_concrete_model=True):
    from django.utils.encoding import smart_unicode

    if for_concrete_model:
        model = model._meta.concrete_model
    elif model._deferred:
        model = model._meta.proxy_for_model

    opts = model._meta

    try:
        ct = self._get_from_cache(opts)
    except KeyError:
        ct, created = self.get_or_create(
            app_label = opts.app_label,
            model = opts.object_name.lower(),
            defaults = {'name': smart_unicode(opts.verbose_name_raw)},
        )
        self._add_to_cache(self.db, ct)

    return ct

ContentTypeManager.get_for_model__original = ContentTypeManager.get_for_model
ContentTypeManager.get_for_model = get_for_model


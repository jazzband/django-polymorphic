# -*- coding: utf-8 -*-
"""
Seamless Polymorphic Inheritance for Django Models

Copyright:
This code and affiliated files are (C) by Bert Constantin and individual contributors.
Please see LICENSE and AUTHORS for more information.
"""
# See PEP 440 (https://www.python.org/dev/peps/pep-0440/)
__version__ = "0.9.1"


import sys
from types import ModuleType

# Monkey-patch Django < 1.5 to allow ContentTypes for proxy models.
import django
if django.VERSION[:2] < (1, 5):
    from django.contrib.contenttypes.models import ContentTypeManager
    from django.utils.encoding import smart_text

    def get_for_model(self, model, for_concrete_model=True):
        if for_concrete_model:
            model = model._meta.concrete_model
        elif model._deferred:
            model = model._meta.proxy_for_model

        opts = model._meta

        try:
            ct = self._get_from_cache(opts)
        except KeyError:
            ct, created = self.get_or_create(
                app_label=opts.app_label,
                model=opts.object_name.lower(),
                defaults={'name': smart_text(opts.verbose_name_raw)},
            )
            self._add_to_cache(self.db, ct)

        return ct

    ContentTypeManager.get_for_model__original = ContentTypeManager.get_for_model
    ContentTypeManager.get_for_model = get_for_model


# import mapping to objects in other modules
all_by_module = {
    'polymorphic.manager': ('PolymorphicManager', ),
    'polymorphic.models': ('PolymorphicModel', ),
    'polymorphic.query': ('PolymorphicQuerySet', ),
    'polymorphic.query_translate': ('translate_polymorphic_Q_object', ),
    'polymorphic.showfields': (
        'ShowFieldContent', 'ShowFieldType', 'ShowFieldTypeAndContent',
        # old names for compatibility
        'ShowFields', 'ShowFieldTypes', 'ShowFieldsAndTypes',
    ),
}


object_origins = {}
for module, items in all_by_module.items():
    for item in items:
        object_origins[item] = module


class module(ModuleType):

    def __dir__(self):
        """Just show what we want to show."""
        result = list(new_module.__all__)
        result.extend(('__file__', '__path__', '__doc__', '__all__',
                       '__docformat__', '__name__', '__path__',
                       '__package__', '__version__'))
        return result

    def __getattr__(self, name):
        if name in object_origins:
            module = __import__(object_origins[name], None, None, [name])
            for extra_name in all_by_module[module.__name__]:
                setattr(self, extra_name, getattr(module, extra_name))
            return getattr(module, name)
        return ModuleType.__getattribute__(self, name)


# keep a reference to this module so that it's not garbage collected
old_module = sys.modules[__name__]

# setup the new module and patch it into the dict of loaded modules
new_module = sys.modules[__name__] = module(__name__)
new_module.__dict__.update({
    '__file__':         __file__,
    '__package__':      __package__,
    '__path__':         __path__,
    '__doc__':          __doc__,
    '__version__':      __version__,
    '__all__':          tuple(object_origins),
    '__docformat__':    'restructuredtext en',
})

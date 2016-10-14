# -*- coding: utf-8 -*-
"""
Seamless Polymorphic Inheritance for Django Models

Copyright:
This code and affiliated files are (C) by Bert Constantin and individual contributors.
Please see LICENSE and AUTHORS for more information.
"""
# See PEP 440 (https://www.python.org/dev/peps/pep-0440/)
__version__ = "1.0.2"


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

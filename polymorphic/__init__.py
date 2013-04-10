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


"""
See PEP 386 (https://www.python.org/dev/peps/pep-0386/)

Release logic:
    1. Remove "dev#" from current (this file, now).
    2. git commit
    3. git tag <version>
    4. push to pypi + push --tags to github
    5. bump the version, append ".dev0"
    6. git commit
    7. push to github
"""
__version__ = "0.4.1.dev0"


# Proxied models need to have it's own ContentType


from django.contrib.contenttypes.models import ContentTypeManager
from django.utils.encoding import smart_unicode


def get_for_proxied_model(self, model):
    """
    Returns the ContentType object for a given model, creating the
    ContentType if necessary. Lookups are cached so that subsequent lookups
    for the same model don't hit the database.
    """
    opts = model._meta
    key = (opts.app_label, opts.object_name.lower())
    try:
        ct = self.__class__._cache[self.db][key]
    except KeyError:
        # Load or create the ContentType entry. The smart_unicode() is
        # needed around opts.verbose_name_raw because name_raw might be a
        # django.utils.functional.__proxy__ object.
        ct, created = self.get_or_create(
            app_label=opts.app_label,
            model=opts.object_name.lower(),
            defaults={'name': smart_unicode(opts.verbose_name_raw)},
        )
        self._add_to_cache(self.db, ct)
    return ct
ContentTypeManager.get_for_proxied_model = get_for_proxied_model

# -*- coding: utf-8 -*-
""" PolymorphicManager
    Please see README.rst or DOCS.rst or http://chrisglass.github.com/django_polymorphic/
"""
from __future__ import unicode_literals
import warnings
import django
from django.db import models
from polymorphic.query import PolymorphicQuerySet


class PolymorphicManager(models.Manager):
    """
    Manager for PolymorphicModel

    Usually not explicitly needed, except if a custom manager or
    a custom queryset class is to be used.
    """
    # Tell Django that related fields also need to use this manager:
    use_for_related_fields = True
    queryset_class = PolymorphicQuerySet

    def __init__(self, queryset_class=None, *args, **kwrags):
        # Up till polymorphic 0.4, the queryset class could be specified as parameter to __init__.
        # However, this doesn't work for related managers which instantiate a new version of this class.
        # Hence, for custom managers the new default is using the 'queryset_class' attribute at class level instead.
        if queryset_class:
            warnings.warn("Using PolymorphicManager(queryset_class=..) is deprecated; override the queryset_class attribute instead", DeprecationWarning)
            # For backwards compatibility, still allow the parameter:
            self.queryset_class = queryset_class

        super(PolymorphicManager, self).__init__(*args, **kwrags)

    def get_queryset(self):
        return self.queryset_class(self.model, using=self._db)

    # For Django 1.5
    if django.VERSION < (1, 7):
        get_query_set = get_queryset

    def __unicode__(self):
        return '%s (PolymorphicManager) using %s' % (self.__class__.__name__, self.queryset_class.__name__)

    # Proxied methods
    def non_polymorphic(self):
        return self.all().non_polymorphic()

    def instance_of(self, *args):
        return self.all().instance_of(*args)

    def not_instance_of(self, *args):
        return self.all().not_instance_of(*args)

    def get_real_instances(self, base_result_objects=None):
        return self.all().get_real_instances(base_result_objects=base_result_objects)

    if django.VERSION >= (1, 7):
        @classmethod
        def from_queryset(cls, queryset_class, class_name=None):
            manager = super(PolymorphicManager, cls).from_queryset(queryset_class, class_name=class_name)
            manager.queryset_class = queryset_class  # also set our version, Django uses _queryset_class
            return manager

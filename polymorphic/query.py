# -*- coding: utf-8 -*-
from __future__ import absolute_import

import threading

from django.db.models.query import QuerySet
from django.db.models.fields.related import SingleRelatedObjectDescriptor, ReverseSingleRelatedObjectDescriptor
from django.contrib.contenttypes.models import ContentType

polymorphic = threading.local()


class PolymorphicSingleRelatedObjectDescriptor(SingleRelatedObjectDescriptor):
    def get_queryset(self, **db_hints):
        qs = SingleRelatedObjectDescriptor.get_queryset(self, **db_hints)
        return qs.non_polymorphic()


class PolymorphicReverseSingleRelatedObjectDescriptor(ReverseSingleRelatedObjectDescriptor):
    def get_queryset(self, **db_hints):
        qs = ReverseSingleRelatedObjectDescriptor.get_queryset(self, **db_hints)
        return qs.non_polymorphic()


class PolymorphicQuerySet(QuerySet):
    polymorphic_disabled = False

    def _clone(self, *args, **kwargs):
        "Django's _clone only copies its own variables, so we need to copy ours here"
        new = super(PolymorphicQuerySet, self)._clone(*args, **kwargs)
        new.polymorphic_disabled = self.polymorphic_disabled
        return new

    def iterator(self):
        polymorphic_disabled = getattr(polymorphic, 'disabled', False)
        polymorphic.disabled = self.polymorphic_disabled
        try:
            for obj in super(PolymorphicQuerySet, self).iterator():
                yield obj
        finally:
            polymorphic.disabled = polymorphic_disabled

    def delete(self):
        polymorphic_disabled = getattr(polymorphic, 'disabled', False)
        polymorphic.disabled = True
        try:
            super(PolymorphicQuerySet, self).delete()
        finally:
            polymorphic.disabled = polymorphic_disabled
    delete.alters_data = True

    def non_polymorphic(self):
        """switch off polymorphic behaviour for this query.
        When the queryset is evaluated, only objects of the type of the
        base class used for this query are returned."""
        qs = self._clone()
        qs.polymorphic_disabled = True
        return qs

    def get_real_instances(self):
        qs = self._clone()
        qs.polymorphic_disabled = False
        return qs

    def _instance_of_ctypes(self, *models):
        instances_of = [instance_of() for model in models for instance_of in model._meta.instance_of]
        return [ContentType.objects.get_for_model(instance_of) for instance_of in instances_of if instance_of]

    def instance_of(self, *models):
        clone = self._clone()
        return clone.filter(polymorphic_ctype__in=self._instance_of_ctypes(*models))

    def not_instance_of(self, *models):
        clone = self._clone()
        return clone.exclude(polymorphic_ctype__in=self._instance_of_ctypes(*models))

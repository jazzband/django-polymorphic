# -*- coding: utf-8 -*-
from __future__ import absolute_import

from django.db import models

from .query import PolymorphicQuerySet


class PolymorphicManager(models.Manager):
    use_for_related_fields = True

    queryset_class = PolymorphicQuerySet

    def get_queryset(self):
        return self.queryset_class(self.model, using=self._db)

    def non_polymorphic(self):
        return self.get_query_set().non_polymorphic()

    def get_real_instances(self, objects):
        if isinstance(objects, PolymorphicQuerySet):
            return objects.get_real_instances()
        else:
            return self.get_query_set().filter(pk__in=[o.pk for o in objects])

    def instance_of(self, *models):
        return self.get_query_set().instance_of(*models)

    def not_instance_of(self, *models):
        return self.get_query_set().not_instance_of(*models)

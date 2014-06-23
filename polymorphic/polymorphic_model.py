# -*- coding: utf-8 -*-
from __future__ import absolute_import

from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.utils import six

from .base import PolymorphicModelBase
from .manager import PolymorphicManager
from .query import polymorphic
from .utils import deferred_class_factory, transmogrify


class PolymorphicModel(six.with_metaclass(PolymorphicModelBase, models.Model)):
    # avoid ContentType related field accessor clash (an error emitted by model validation)
    polymorphic_ctype = models.ForeignKey(ContentType, editable=False, related_name='polymorphic_%(app_label)s.%(class)s_set')

    # some applications want to know the name of the fields that are added to its models
    polymorphic_internal_model_fields = ['polymorphic_ctype']

    objects = PolymorphicManager()

    class Meta:
        abstract = True

    def delete(self, using=None):
        polymorphic_disabled = getattr(polymorphic, 'disabled', False)
        polymorphic.disabled = True
        try:
            super(PolymorphicModel, self).delete(using=using)
        finally:
            polymorphic.disabled = polymorphic_disabled
    delete.alters_data = True

    def get_polymorphic_ctype(self):
        if self.polymorphic_ctype_id:
            return ContentType.objects.get_for_id(self.polymorphic_ctype_id)
        else:
            return ContentType.objects.get_for_model(self, for_concrete_model=False)

    def get_real_instance(self):
        """
        Normally not needed.
        If a non-polymorphic manager (like base_objects) has been used to
        retrieve objects, then the complete object with it's real class/type
        and all fields may be retrieved with this method.
        Each method call executes one db query (if necessary).
        """
        real_model = self.get_polymorphic_ctype().model_class()
        if real_model == self._meta.model:
            return self

        attrs = set(f.attname for f in real_model._meta.fields) - set(f.attname for f in self._meta.fields)
        if real_model._meta.pk.attname in attrs:
            attrs.remove(real_model._meta.pk.attname)
        deferred_modelclass = deferred_class_factory(real_model, self._meta.model, set(), attrs)

        return transmogrify(deferred_modelclass, self)

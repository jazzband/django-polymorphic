# -*- coding: utf-8 -*-
"""
Seamless Polymorphic Inheritance for Django Models
==================================================

Please see README.rst and DOCS.rst for further information.

Or on the Web:
http://bserve.webhop.org/wiki/django_polymorphic
http://github.com/bconstantin/django_polymorphic
http://bitbucket.org/bconstantin/django_polymorphic

Copyright:
This code and affiliated files are (C) by Bert Constantin and individual contributors.
Please see LICENSE and AUTHORS for more information. 
"""

from pprint import pprint
import sys
from compatibility_tools import defaultdict

from django.db import models
from django.contrib.contenttypes.models import ContentType
from django import VERSION as django_VERSION

from base import PolymorphicModelBase
from manager import PolymorphicManager
from query import PolymorphicQuerySet
from showfields import ShowFieldTypes

 
###################################################################################
### PolymorphicModel

class PolymorphicModel(ShowFieldTypes, models.Model):
    """
    Abstract base class that provides polymorphic behaviour
    for any model directly or indirectly derived from it.
    
    For usage instructions & examples please see documentation.
    
    PolymorphicModel declares one field for internal use (polymorphic_ctype)
    and provides a polymorphic manager as the default manager
    (and as 'objects').
    
    PolymorphicModel overrides the save() method.
    
    If your derived class overrides save() as well, then you need
    to take care that you correctly call the save() method of
    the superclass, like:
    
        super(YourClass,self).save(*args,**kwargs)
    """
    __metaclass__ = PolymorphicModelBase

    polymorphic_model_marker = True   # for PolymorphicModelBase

    class Meta:
        abstract = True

    # avoid ContentType related field accessor clash (an error emitted by model validation)
    # we really should use both app_label and model name, but this is only possible since Django 1.2 
    if django_VERSION[0] <= 1 and django_VERSION[1] <= 1:
        p_related_name_template = 'polymorphic_%(class)s_set'
    else:
        p_related_name_template = 'polymorphic_%(app_label)s.%(class)s_set'
    polymorphic_ctype = models.ForeignKey(ContentType, null=True, editable=False,
                                related_name=p_related_name_template)
            
    # some applications want to know the name of the fields that are added to its models
    polymorphic_internal_model_fields = [ 'polymorphic_ctype' ]

    objects = PolymorphicManager()
    base_objects = models.Manager()

    def pre_save_polymorphic(self):
        """Normally not needed.
        This function may be called manually in special use-cases. When the object
        is saved for the first time, we store its real class in polymorphic_ctype.
        When the object later is retrieved by PolymorphicQuerySet, it uses this
        field to figure out the real class of this object
        (used by PolymorphicQuerySet._get_real_instances)
        """
        if not self.polymorphic_ctype:
            self.polymorphic_ctype = ContentType.objects.get_for_model(self)

    def save(self, *args, **kwargs):
        """Overridden model save function which supports the polymorphism
        functionality (through pre_save_polymorphic)."""
        self.pre_save_polymorphic()
        return super(PolymorphicModel, self).save(*args, **kwargs)

    def get_real_instance_class(self):
        """Normally not needed.
        If a non-polymorphic manager (like base_objects) has been used to
        retrieve objects, then the real class/type of these objects may be
        determined using this method.""" 
        # the following line would be the easiest way to do this, but it produces sql queries
        #return self.polymorphic_ctype.model_class()
        # so we use the following version, which uses the CopntentType manager cache
        return ContentType.objects.get_for_id(self.polymorphic_ctype_id).model_class()
    
    def get_real_instance(self):
        """Normally not needed.
        If a non-polymorphic manager (like base_objects) has been used to
        retrieve objects, then the complete object with it's real class/type
        and all fields may be retrieved with this method.
        Each method call executes one db query (if necessary).""" 
        real_model = self.get_real_instance_class()
        if real_model == self.__class__: return self
        return real_model.objects.get(pk=self.pk)
    
    # hack: a small patch to Django would be a better solution.
    # For base model back reference fields (like basemodel_ptr),
    # Django definitely must =not= use our polymorphic manager/queryset.
    # For now, we catch objects attribute access here and handle back reference fields manually.
    # This problem is triggered by delete(), like here:
    # django.db.models.base._collect_sub_objects: parent_obj = getattr(self, link.name)
    # TODO: investigate Django how this can be avoided
    def __getattribute__(self, name):
        if not name.startswith('__'):         # do not intercept __class__ etc.

            # for efficiency: create a dict containing all model attribute names we need to intercept
            # (do this only once and store the result into self.__class__.inheritance_relation_fields_dict)
            if not self.__class__.__dict__.get('inheritance_relation_fields_dict', None):

                def add_if_regular_sub_or_super_class(model, as_ptr, result):
                    if ( issubclass(model, models.Model) and model != models.Model
                        and model != self.__class__ and model != PolymorphicModel):
                        name = model.__name__.lower()
                        if as_ptr: name+='_ptr'
                        result[name] = model
                def add_all_base_models(model, result):
                    add_if_regular_sub_or_super_class(model, True, result)
                    for b in model.__bases__:
                        add_all_base_models(b, result)
                def add_sub_models(model, result):
                    for b in model.__subclasses__():
                        add_if_regular_sub_or_super_class(b, False, result)

                result = {}
                add_all_base_models(self.__class__,result)
                add_sub_models(self.__class__,result)
                #print '##',self.__class__.__name__,' - ',result
                self.__class__.inheritance_relation_fields_dict = result

            model = self.__class__.inheritance_relation_fields_dict.get(name, None)
            if model:
                id = super(PolymorphicModel, self).__getattribute__('id')
                attr = model.base_objects.get(id=id)
                #print '---',self.__class__.__name__,name
                return attr
        return super(PolymorphicModel, self).__getattribute__(name)



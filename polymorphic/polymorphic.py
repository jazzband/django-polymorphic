# -*- coding: utf-8 -*-
"""
Fully Polymorphic Django Models
===============================

For an overview, examples, documentation and updates please see here:

    http://bserve.webhop.org/wiki/django_polymorphic

or in the included README.rst and DOCS.rst files.

Copyright:
This code and affiliated files are (C) by Bert Constantin and individual contributors.
Please see LICENSE and AUTHORS for more information. 
"""

from django.db import models
from django.db.models.base import ModelBase
from django.db.models.query import QuerySet
from collections import defaultdict
from pprint import pprint
from django.contrib.contenttypes.models import ContentType
import sys

# chunk-size: maximum number of objects requested per db-request
# by the polymorphic queryset.iterator() implementation
Polymorphic_QuerySet_objects_per_request = 100

 
###################################################################################
### PolymorphicManager

class PolymorphicManager(models.Manager):
    """
    Manager for PolymorphicModel
    
    Usually not explicitly needed, except if a custom manager or
    a custom queryset class is to be used.
    """
    use_for_related_fields = True

    def __init__(self, queryset_class=None, *args, **kwrags):
        if not queryset_class: self.queryset_class = PolymorphicQuerySet
        else: self.queryset_class = queryset_class
        super(PolymorphicManager, self).__init__(*args, **kwrags)
        
    def get_query_set(self):
        return self.queryset_class(self.model)
    
    # Proxy all unknown method calls to the queryset, so that its members are
    # directly accessible as PolymorphicModel.objects.*
    # The advantage is that not yet known member functions of derived querysets will be proxied as well. 
    # We exclude any special functions (__) from this automatic proxying.
    def __getattr__(self, name):
        if name.startswith('__'): return super(PolymorphicManager, self).__getattr__(self, name)
        return getattr(self.get_query_set(), name)
    
    def __unicode__(self):
        return self.__class__.__name__ + ' (PolymorphicManager) using ' + self.queryset_class.__name__


###################################################################################
### PolymorphicQuerySet

# PolymorphicQuerySet Q objects (and filter()) support these additional key words.
# These are forbidden as field names (a descriptive exception is raised) 
POLYMORPHIC_SPECIAL_Q_KWORDS = [ 'instance_of', 'not_instance_of']

class PolymorphicQuerySet(QuerySet):
    """
    QuerySet for PolymorphicModel
    
    Contains the core functionality for PolymorphicModel 
    
    Usually not explicitly needed, except if a custom queryset class
    is to be used.
    """

    def instance_of(self, *args):
        """Filter the queryset to only include the classes in args (and their subclasses).
        Implementation in _translate_polymorphic_filter_defnition."""
        return self.filter(instance_of=args)

    def not_instance_of(self, *args):
        """Filter the queryset to exclude the classes in args (and their subclasses).
        Implementation in _translate_polymorphic_filter_defnition."""
        return self.filter(not_instance_of=args)

    def _filter_or_exclude(self, negate, *args, **kwargs):
        "We override this internal Django functon as it is used for all filter member functions."
        _translate_polymorphic_filter_definitions_in_args(self.model, args) # the Q objects
        additional_args = _translate_polymorphic_filter_definitions_in_kwargs(self.model, kwargs) # filter_field='data'
        return super(PolymorphicQuerySet, self)._filter_or_exclude(negate, *(list(args) + additional_args), **kwargs)

    # these queryset functions are not yet supported
    def defer(self, *args, **kwargs): raise NotImplementedError
    def only(self, *args, **kwargs): raise NotImplementedError
    def aggregate(self, *args, **kwargs): raise NotImplementedError
    def annotate(self, *args, **kwargs): raise NotImplementedError

    def _get_real_instances(self, base_result_objects):
        """
        Polymorphic object loader
        
        Does the same as:
        
            return [ o.get_real_instance() for o in base_result_objects ]
        
        The list base_result_objects contains the objects from the executed
        base class query. The class of all of them is self.model (our base model).
        
        Some, many or all of these objects were not created and stored as
        class self.model, but as a class derived from self.model. We want to re-fetch
        these objects from the db as their original class so we can return them
        just as they were created/saved.
        
        We identify these objects by looking at o.polymorphic_ctype, which specifies
        the real class of these objects (the class at the time they were saved).
        
        First, we sort the result objects in base_result_objects for their
        subclass (from o.polymorphic_ctype), and then we execute one db query per
        subclass of objects. Finally we re-sort the resulting objects into the
        correct order and return them as a list.
        """
        ordered_id_list = []    # list of ids of result-objects in correct order
        results = {}            # polymorphic dict of result-objects, keyed with their id (no order)
        
        # dict contains one entry per unique model type occurring in result,
        # in the format idlist_per_model[modelclass]=[list-of-object-ids]
        idlist_per_model = defaultdict(list)
        
        # - sort base_result_object ids into idlist_per_model lists, depending on their real class;
        # - also record the correct result order in "ordered_id_list"
        # - store objects that already have the correct class into "results"
        self_model_content_type_id = ContentType.objects.get_for_model(self.model).pk
        for base_object in base_result_objects:
            ordered_id_list.append(base_object.id)

            # this object is not a derived object and already the real instance => store it right away
            if (base_object.polymorphic_ctype_id == self_model_content_type_id):
                results[base_object.id] = base_object

            # this object is derived and its real instance needs to be retrieved
            # => store it's id into the bin for this model type
            else:
                idlist_per_model[base_object.get_real_instance_class()].append(base_object.id)
        
        # for each model in "idlist_per_model" request its objects (the full model)
        # from the db and store them in results[]
        for modelclass, idlist in idlist_per_model.items():
            qs = modelclass.base_objects.filter(id__in=idlist)
            # copy select related configuration to new qs
            # TODO: this does not seem to copy the complete sel_rel-config (field names etc.)
            self.dup_select_related(qs) 
            # TODO: defer(), only() and annotate(): support for these would be around here
            for o in qs: results[o.id] = o
        
        # re-create correct order and return result list
        resultlist = [ results[ordered_id] for ordered_id in ordered_id_list if ordered_id in results ]
        return resultlist

    def iterator(self):
        """
        This function is used by Django for all object retrieval.
        By overriding it, we modify the objects that this queryset returns
        when it is evaluated (or its get method or other object-returning methods are called).
        
        Here we do the same as:

            base_result_objects=list(super(PolymorphicQuerySet, self).iterator())
            real_results=self._get_real_instances(base_result_objects)
            for o in real_results: yield o
        
        but it requests the objects in chunks from the database,
        with Polymorphic_QuerySet_objects_per_request per chunk
        """
        base_iter = super(PolymorphicQuerySet, self).iterator()

        while True:
            base_result_objects = []
            reached_end = False
            
            for i in range(Polymorphic_QuerySet_objects_per_request):
                try: base_result_objects.append(base_iter.next())
                except StopIteration:
                    reached_end = True
                    break
            
            real_results = self._get_real_instances(base_result_objects)
            
            for o in real_results:
                yield o
                
            if reached_end: raise StopIteration
            
    def __repr__(self):
        result = [ repr(o) for o in self.all() ]
        return  '[ ' + ',\n  '.join(result) + ' ]' 
        

###################################################################################
### PolymorphicQuerySet support functions

# These functions implement the additional filter- and Q-object functionality.
# They form a kind of small framework for easily adding more
# functionality to filters and Q objects.
# Probably a more general queryset enhancement class could be made out of them.
 
def _translate_polymorphic_filter_definitions_in_kwargs(queryset_model, kwargs):
    """
    Translate the keyword argument list for PolymorphicQuerySet.filter()
    
    Any kwargs with special polymorphic functionality are replaced in the kwargs
    dict with their vanilla django equivalents.
    
    For some kwargs a direct replacement is not possible, as a Q object is needed
    instead to implement the required functionality. In these cases the kwarg is
    deleted from the kwargs dict and a Q object is added to the return list.
    
    Modifies: kwargs dict
    Returns: a list of non-keyword-arguments (Q objects) to be added to the filter() query.
    """ 
    additional_args = []
    for field_path, val in kwargs.items():
        
        new_expr = _translate_polymorphic_filter_defnition(queryset_model, field_path, val)

        if type(new_expr) == tuple:
            # replace kwargs element
            del(kwargs[field_path])
            kwargs[new_expr[0]] = new_expr[1]
        
        elif isinstance(new_expr, models.Q):
            del(kwargs[field_path])
            additional_args.append(new_expr)

    return additional_args
    
def _translate_polymorphic_filter_definitions_in_args(queryset_model, args):
    """
    Translate the non-keyword argument list for PolymorphicQuerySet.filter()
    
    In the args list, we replace all kwargs to Q-objects that contain special
    polymorphic functionality with their vanilla django equivalents.
    We traverse the Q object tree for this (which is simple).
    
    TODO: investigate: we modify the Q-objects ina args in-place. Is this OK?
    
    Modifies: args list
    """

    def tree_node_correct_field_specs(node):
        " process all children of this Q node "
        for i in range(len(node.children)):
            child = node.children[i]
            
            if type(child) == tuple:
                # this Q object child is a tuple => a kwarg like Q( instance_of=ModelB )
                key, val = child
                new_expr = _translate_polymorphic_filter_defnition(queryset_model, key, val)
                if new_expr:
                    node.children[i] = new_expr
            else:
                # this Q object child is another Q object, recursively process this as well
                tree_node_correct_field_specs(child)
                                                
    for q in args:
        if isinstance(q, models.Q):
            tree_node_correct_field_specs(q)

def _translate_polymorphic_filter_defnition(queryset_model, field_path, field_val):
    """
    Translate a keyword argument (field_path=field_val), as used for
    PolymorphicQuerySet.filter()-like functions (and Q objects).
    
    A kwarg with special polymorphic functionality is translated into
    its vanilla django equivalent, which is returned, either as tuple
    (field_path, field_val) or as Q object.
    
    Returns: kwarg tuple or Q object or None (if no change is required)
    """
    
    # handle instance_of expressions or alternatively,
    # if this is a normal Django filter expression, return None
    if field_path == 'instance_of':
        return _create_model_filter_Q(field_val)
    elif field_path == 'not_instance_of':
        return _create_model_filter_Q(field_val, not_instance_of=True)
    elif not '___' in field_path:
        return None #no change

    # filter expression contains '___' (i.e. filter for polymorphic field)
    # => get the model class specified in the filter expression
    newpath = _translate_polymorphic_field_path(queryset_model, field_path)
    return (newpath, field_val)


def _translate_polymorphic_field_path(queryset_model, field_path):
    """
    Translate a field path from a keyword argument, as used for
    PolymorphicQuerySet.filter()-like functions (and Q objects).
    
    E.g.: ModelC___field3 is translated into modela__modelb__modelc__field3
    Returns: translated path
    """
    classname, sep, pure_field_path = field_path.partition('___')
    assert sep == '___'

    if '__' in classname:
        # the user has app label prepended to class name via __ => use Django's get_model function
        appname, sep, classname = classname.partition('__')
        model = models.get_model(appname, classname)
        assert model, 'PolymorphicModel: model %s (in app %s) not found!' % (model.__name__, appname)
        if not issubclass(model, queryset_model):
            e = 'PolymorphicModel: queryset filter error: "' + model.__name__ + '" is not derived from "' + queryset_model.__name__ + '"'
            raise AssertionError(e)
        
    else:
        # the user has only given us the class name via __
        # => select the model from the sub models of the queryset base model

        # function to collect all sub-models, this should be optimized (cached)
        def add_all_sub_models(model, result):
            if issubclass(model, models.Model) and model != models.Model:
                # model name is occurring twice in submodel inheritance tree => Error
                if model.__name__ in result and model != result[model.__name__]:
                    e = 'PolymorphicModel: model name alone is ambiguous: %s.%s and %s.%s!\n'
                    e += 'In this case, please use the syntax: applabel__ModelName___field'
                    assert model, e % (
                        model._meta.app_label, model.__name__,
                        result[model.__name__]._meta.app_label, result[model.__name__].__name__)
            
                result[model.__name__] = model

            for b in model.__subclasses__():
                add_all_sub_models(b, result)
        
        submodels = {}
        add_all_sub_models(queryset_model, submodels)
        model = submodels.get(classname, None)
        assert model, 'PolymorphicModel: model %s not found (not a subclass of %s)!' % (classname, queryset_model.__name__)

    # create new field path for expressions, e.g. for baseclass=ModelA, myclass=ModelC
    # 'modelb__modelc" is returned
    def _create_base_path(baseclass, myclass):
        bases = myclass.__bases__
        for b in bases:
            if b == baseclass:
                return myclass.__name__.lower()
            path = _create_base_path(baseclass, b)
            if path: return path + '__' + myclass.__name__.lower()
        return ''
    
    basepath = _create_base_path(queryset_model, model)
    newpath = basepath + '__' if basepath else ''
    newpath += pure_field_path
    return newpath


def _create_model_filter_Q(modellist, not_instance_of=False):
    """
    Helper function for instance_of / not_instance_of
    Creates and returns a Q object that filters for the models in modellist,
    including all subclasses of these models (as we want to do the same
    as pythons isinstance() ).
    .
    We recursively collect all __subclasses__(), create a Q filter for each,
    and or-combine these Q objects. This could be done much more
    efficiently however (regarding the resulting sql), should an optimization
    be needed.
    """

    if not modellist: return None
    from django.db.models import Q
    
    if type(modellist) != list and type(modellist) != tuple:
        if issubclass(modellist, PolymorphicModel):
            modellist = [modellist]
        else:
            assert False, 'PolymorphicModel: instance_of expects a list of models or a single model'

    def q_class_with_subclasses(model):
        q = Q(polymorphic_ctype=ContentType.objects.get_for_model(model))
        for subclass in model.__subclasses__():
            q = q | q_class_with_subclasses(subclass)
        return q
            
    qlist = [  q_class_with_subclasses(m)  for m in modellist  ]
    
    q_ored = reduce(lambda a, b: a | b, qlist)
    if not_instance_of: q_ored = ~q_ored
    return q_ored


###################################################################################
### PolymorphicModel meta class

class PolymorphicModelBase(ModelBase):
    """
    Manager inheritance is a pretty complex topic which may need
    more thought regarding how this should be handled for polymorphic
    models.
    
    In any case, we probably should propagate 'objects' and 'base_objects'
    from PolymorphicModel to every subclass. We also want to somehow
    inherit/propagate _default_manager as well, as it needs to be polymorphic.
    
    The current implementation below is an experiment to solve this
    problem with a very simplistic approach: We unconditionally
    inherit/propagate any and all managers (using _copy_to_model),
    as long as they are defined on polymorphic models
    (the others are left alone).
    
    Like Django ModelBase, we special-case _default_manager:
    if there are any user-defined managers, it is set to the first of these.

    We also require that _default_manager as well as any user defined
    polymorphic managers produce querysets that are derived from
    PolymorphicQuerySet.
    """
    
    def __new__(self, model_name, bases, attrs):
        #print; print '###', model_name, '- bases:', bases

        # create new model
        new_class = self.call_superclass_new_method(model_name, bases, attrs)

        # check if the model fields are all allowed
        self.validate_model_fields(new_class)

        # create list of all managers to be inherited from the base classes
        inherited_managers = new_class.get_inherited_managers(attrs)
        
        # add the managers to the new model
        for source_name, mgr_name, manager in inherited_managers:
            #print '** add inherited manager from model %s, manager %s, %s' % (source_name, mgr_name, manager.__class__.__name__)
            new_manager = manager._copy_to_model(new_class)
            new_class.add_to_class(mgr_name, new_manager)
        
        # get first user defined manager; if there is one, make it the _default_manager
        user_manager = self.get_first_user_defined_manager(attrs)
        if user_manager:
            def_mgr = user_manager._copy_to_model(new_class)
            #print '## add default manager', type(def_mgr)
            new_class.add_to_class('_default_manager', def_mgr)
            new_class._default_manager._inherited = False   # the default mgr was defined by the user, not inherited

        # validate resulting default manager 
        self.validate_model_manager(new_class._default_manager, model_name, '_default_manager')

        return new_class

    def get_inherited_managers(self, attrs):
        """
        Return list of all managers to be inherited/propagated from the base classes;
        use correct mro, only use managers with _inherited==False,
        skip managers that are overwritten by the user with same-named class attributes (in attrs)
        """
        add_managers = []; add_managers_keys = set()
        for base in self.__mro__[1:]:
            if not issubclass(base, models.Model): continue
            if not getattr(base, 'polymorphic_model_marker', None): continue # leave managers of non-polym. models alone

            for key, manager in base.__dict__.items():
                if type(manager) == models.manager.ManagerDescriptor: manager = manager.manager 
                if not isinstance(manager, models.Manager): continue
                if key in attrs: continue
                if key in add_managers_keys: continue       # manager with that name already added, skip
                if manager._inherited: continue             # inherited managers have no significance, they are just copies
                if isinstance(manager, PolymorphicManager): # validate any inherited polymorphic managers
                    self.validate_model_manager(manager, self.__name__, key)
                add_managers.append((base.__name__, key, manager))
                add_managers_keys.add(key)
        return add_managers

    @classmethod
    def get_first_user_defined_manager(self, attrs):
        mgr_list = []
        for key, val in attrs.items():
            if not isinstance(val, models.Manager): continue
            mgr_list.append((val.creation_counter, val))
        # if there are user defined managers, use first one as _default_manager
        if mgr_list:                        # 
            _, manager = sorted(mgr_list)[0]
            return manager
        return None  

    @classmethod
    def call_superclass_new_method(self, model_name, bases, attrs):
        """call __new__ method of super class and return the newly created class.
        Also work around a limitation in Django's ModelBase."""
        # There seems to be a general limitation in Django's app_label handling
        # regarding abstract models (in ModelBase). See issue 1 on github - TODO: propose patch for Django
        # We run into this problem if polymorphic.py is located in a top-level directory
        # which is directly in the python path. To work around this we temporarily set
        # app_label here for PolymorphicModel. 
        meta = attrs.get('Meta', None)
        model_module_name = attrs['__module__']
        do_app_label_workaround = (meta
                                    and model_module_name == 'polymorphic'
                                    and model_name == 'PolymorphicModel'
                                    and getattr(meta, 'app_label', None) is None )
        
        if do_app_label_workaround: meta.app_label = 'poly_dummy_app_label'
        new_class = super(PolymorphicModelBase, self).__new__(self, model_name, bases, attrs)
        if do_app_label_workaround: del(meta.app_label)
        return new_class

    def validate_model_fields(self):
        "check if all fields names are allowed (i.e. not in POLYMORPHIC_SPECIAL_Q_KWORDS)"
        for f in self._meta.fields:
            if f.name in POLYMORPHIC_SPECIAL_Q_KWORDS:
                e = 'PolymorphicModel: "%s" - field name "%s" is not allowed in polymorphic models'
                raise AssertionError(e % (self.__name__, f.name) )

    @classmethod
    def validate_model_manager(self, manager, model_name, manager_name):
        """check if the manager is derived from PolymorphicManager
        and its querysets from PolymorphicQuerySet - throw AssertionError if not"""
        
        if not issubclass(type(manager), PolymorphicManager):
            e = 'PolymorphicModel: "' + model_name + '.' + manager_name + '" manager is of type "' + type(manager).__name__
            e += '", but must be a subclass of PolymorphicManager'
            raise AssertionError(e)
        if not getattr(manager, 'queryset_class', None) or not issubclass(manager.queryset_class, PolymorphicQuerySet):
            e = 'PolymorphicModel: "' + model_name + '.' + manager_name + '" (PolymorphicManager) has been instantiated with a queryset class which is'
            e += ' not a subclass of PolymorphicQuerySet (which is required)'
            raise AssertionError(e)
        return manager
        

###################################################################################
### PolymorphicModel

class PolymorphicModel(models.Model):
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

    # TODO: %(class)s alone is not really enough, we also need to include app_label - patch for Django needed?
    # see: django/db/models/fields/related.py/RelatedField
    polymorphic_ctype = models.ForeignKey(ContentType,
                            null=True, editable=False, related_name='polymorphic_%(class)s_set')
            
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
        return real_model.objects.get(id=self.id)
    
    # Hack: 
    # For base model back reference fields (like basemodel_ptr),
    # Django definitely must =not= use our polymorphic manager/queryset.
    # For now, we catch objects attribute access here and handle back reference fields manually.
    # This problem is triggered by delete(), like here:
    # django.db.models.base._collect_sub_objects: parent_obj = getattr(self, link.name)
    # TODO: investigate Django how this can be avoided
    def __getattribute__(self, name):
        if name != '__class__':
            #if name.endswith('_ptr_cache'): # unclear if this should be handled as well
            if name.endswith('_ptr'): name = name[:-4]
            model = self.__class__.sub_and_superclass_dict.get(name, None)
            if model: 
                id = super(PolymorphicModel, self).__getattribute__('id')
                attr = model.base_objects.get(id=id)
                return attr
        return super(PolymorphicModel, self).__getattribute__(name)

    # support for __getattribute__ hack: create sub_and_superclass_dict,
    # containing all model attribute names we need to intercept
    # (do this once here instead of in __getattribute__ every time)
    def __init__(self, *args, **kwargs):
        if not getattr(self.__class__, 'sub_and_superclass_dict', None):
            def add_all_base_models(model, result):
                if issubclass(model, models.Model) and model != models.Model:
                    result[model.__name__.lower()] = model
                for b in model.__bases__:
                    add_all_base_models(b, result)
            def add_all_sub_models(model, result):
                if issubclass(model, models.Model) and model != models.Model:
                    result[model.__name__.lower()] = model
                for b in model.__subclasses__():
                    add_all_sub_models(b, result)
                                    
            result = {}
            add_all_base_models(self.__class__, result)
            add_all_sub_models(self.__class__, result)
            self.__class__.sub_and_superclass_dict = result
            
        super(PolymorphicModel, self).__init__(*args, **kwargs)
        
    def __repr__(self):
        out = self.__class__.__name__ + ': id %d, ' % (self.id or - 1); last = self._meta.fields[-1]
        for f in self._meta.fields:
            if f.name in [ 'id' ] + self.polymorphic_internal_model_fields or 'ptr' in f.name: continue
            out += f.name + ' (' + type(f).__name__ + ')'
            if f != last:  out += ', '
        return '<' + out + '>'


class ShowFields(object):
    """ model mixin that shows the object's class, it's fields and field contents """
    def __repr__(self):
        out = 'id %d, ' % (self.id); last = self._meta.fields[-1]
        for f in self._meta.fields:
            if f.name in [ 'id' ] + self.polymorphic_internal_model_fields or 'ptr' in f.name: continue
            out += f.name
            if isinstance(f, (models.ForeignKey)):
                o = getattr(self, f.name)
                out += ': "' + ('None' if o == None else o.__class__.__name__) + '"'
            else:
                out += ': "' + getattr(self, f.name) + '"'
            if f != last:  out += ', '
        return '<' + (self.__class__.__name__ + ': ') + out + '>'


class ShowFieldsAndTypes(object):
    """ model mixin, like ShowFields, but also show field types """
    def __repr__(self):
        out = 'id %d, ' % (self.id); last = self._meta.fields[-1]
        for f in self._meta.fields:
            if f.name in [ 'id' ] + self.polymorphic_internal_model_fields or 'ptr' in f.name: continue
            out += f.name + ' (' + type(f).__name__ + ')'
            if isinstance(f, (models.ForeignKey)):
                o = getattr(self, f.name)
                out += ': "' + ('None' if o == None else o.__class__.__name__) + '"'
            else:
                out += ': "' + getattr(self, f.name) + '"'
            if f != last:  out += ', '
        return '<' + self.__class__.__name__ + ': ' + out + '>'


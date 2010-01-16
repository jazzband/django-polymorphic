# -*- coding: utf-8 -*-
"""
===============================
Fully Polymorphic Django Models
===============================


Overview
========

'polymorphic.py' is an add-on module that adds fully automatic
polymorphism to the Django model inheritance system.

The effect is: For enabled models, objects retrieved from the
database are always delivered just as they were created and saved,
with the same type/class and fields - regardless how they are
retrieved. The resulting querysets are polymorphic, i.e. may deliver
objects of several different types in a single query result.

Please see the concrete examples below as they demonstrate this best.

Please note that this module is very experimental code. See below for
current restrictions, caveats, and performance implications.


Installation / Testing
======================

Requirements
------------

Django 1.1 and Python 2.5+. This code has been tested
on Django 1.1.1 with Python 2.5.4 and 2.6.4 on Linux. 

Testing
-------

The repository (or tar file)  contains a complete Django project
that may be used for testing and experimentation.

To run the included test suite, execute::

    ./manage test poly

'management/commands/polycmd.py' can be used for experiments
- modify this file to your liking, then run::

    ./manage syncdb      # db is created in /tmp/... (settings.py)
    ./manage polycmd
    
Using polymorphic models in your own projects
---------------------------------------------

Copy polymorphic.py (from the 'poly' dir) into a directory from where
you can import it, like your app directory (where your models.py and
views.py files live).


Defining Polymorphic Models
===========================

To make models polymorphic, use PolymorphicModel instead of Django's
models.Model as the superclass of your base model. All models
inheriting from your base class will be polymorphic as well::

    from polymorphic import PolymorphicModel    

    class ModelA(PolymorphicModel):
        field1 = models.CharField(max_length=10)
        
    class ModelB(ModelA):
        field2 = models.CharField(max_length=10)
        
    class ModelC(ModelB):
        field3 = models.CharField(max_length=10)


Using Polymorphic Models
========================

Most of Django's standard ORM functionality is available
and works as expected:

Create some objects
-------------------

    >>> ModelA.objects.create(field1='A1')
    >>> ModelB.objects.create(field1='B1', field2='B2')
    >>> ModelC.objects.create(field1='C1', field2='C2', field3='C3')

Query results are polymorphic
-----------------------------

    >>> ModelA.objects.all()
    .
    [ <ModelA: id 1, field1 (CharField)>,
      <ModelB: id 2, field1 (CharField), field2 (CharField)>,
      <ModelC: id 3, field1 (CharField), field2 (CharField), field3 (CharField)> ]

Filtering for classes (equivalent to python's isinstance() ):
-------------------------------------------------------------

    >>> ModelA.objects.instance_of(ModelB)
    .
    [ <ModelB: id 2, field1 (CharField), field2 (CharField)>,
      <ModelC: id 3, field1 (CharField), field2 (CharField), field3 (CharField)> ]
    
    In general, including or excluding parts of the inheritance tree::
        
        ModelA.objects.instance_of(ModelB [, ModelC ...])
        ModelA.objects.not_instance_of(ModelB [, ModelC ...])

Polymorphic filtering (for fields in derived classes)
-----------------------------------------------------

    For example, cherrypicking objects from multiple derived classes
    anywhere in the inheritance tree, using Q objects (with the
    slightly enhanced syntax: exact model name + three _ + field name):
    
    >>> ModelA.objects.filter(  Q( ModelB___field2 = 'B2' )  |  Q( ModelC___field3 = 'C3' )  )
    .
    [ <ModelB: id 2, field1 (CharField), field2 (CharField)>,
      <ModelC: id 3, field1 (CharField), field2 (CharField), field3 (CharField)> ]

Combining Querysets of different types/models
---------------------------------------------

    Querysets may now be regarded as object containers that allow the
    aggregation of  different object types - very similar to python
    lists (as long as the objects are accessed through the manager of
    a common base class):

    >>> Base.objects.instance_of(ModelX) | Base.objects.instance_of(ModelY)
    .
    [ <ModelX: id 1, field_x (CharField)>,
      <ModelY: id 2, field_y (CharField)> ]

Using Third Party Models (without modifying them)
-------------------------------------------------

    Third party models can be used as polymorphic models without
    restrictions by subclassing them. E.g. using a third party
    model as the root of a polymorphic inheritance tree::
        
        from thirdparty import ThirdPartyModel
        
        class MyThirdPartyModel(PolymorhpicModel, ThirdPartyModel):
            pass    # or add fields
    
    Or instead integrating the third party model anywhere into an
    existing polymorphic inheritance tree::

        class MyModel(SomePolymorphicModel):
            my_field = models.CharField(max_length=10)
        
        class MyModelWithThirdParty(MyModel, ThirdPartyModel):
            pass    # or add fields
  
ManyToManyField, ForeignKey, OneToOneField
------------------------------------------

    Relationship fields referring to polymorphic models work as
    expected: like polymorphic querysets they now always return the
    referred objects with the same type/class these were created and
    saved as.
    
    E.g., if in your model you define::
    
        field1 = OneToOneField(ModelA)
        
    then field1 may now also refer to objects of type ModelB or ModelC.
    
    A ManyToManyField example::

        # The model holding the relation may be any kind of model, polymorphic or not
        class RelatingModel(models.Model):
            many2many = models.ManyToManyField('ModelA')  # ManyToMany relation to a polymorphic model

        >>> o=RelatingModel.objects.create()
        >>> o.many2many.add(ModelA.objects.get(id=1))
        >>> o.many2many.add(ModelB.objects.get(id=2))
        >>> o.many2many.add(ModelC.objects.get(id=3))
        
        >>> o.many2many.all()
        [ <ModelA: id 1, field1 (CharField)>,
          <ModelB: id 2, field1 (CharField), field2 (CharField)>,
          <ModelC: id 3, field1 (CharField), field2 (CharField), field3 (CharField)> ]

Non-Polymorphic Queries
-----------------------
    
    >>> ModelA.base_objects.all()
    .
    [ <ModelA: id 1, field1 (CharField)>,
      <ModelA: id 2, field1 (CharField)>,
      <ModelA: id 3, field1 (CharField)> ]

    Each polymorphic model has 'base_objects' defined as a normal
    Django manager. Of course, arbitrary custom managers may be
    added to the models as well.
    

Custom Managers, Querysets & Inheritance
========================================
    
Using a Custom Manager
----------------------

For creating a custom polymorphic manager class, derive your manager
from PolymorphicManager instead of models.Manager. In your model
class, explicitly add the default manager first, and then your
custom manager::

        class MyOrderedManager(PolymorphicManager):
            def get_query_set(self):
                return super(MyOrderedManager,self).get_query_set().order_by('some_field')
                
        class MyModel(PolymorphicModel):
            objects = PolymorphicManager()    # add the default polymorphic manager first
            ordered_objects = MyOrderedManager()    # then add your own manager

The first manager defined ('objects' in the example) is used by
Django as automatic manager for several purposes, including accessing
related objects. It must not filter objects and it's safest to use
the plain PolymorphicManager here.

Manager Inheritance
-------------------

The current polymorphic models implementation unconditionally
inherits all managers from its base models (but only the
polymorphic base models).

An example (inheriting from MyModel above)::

    class MyModel2(MyModel):
        pass

    # Managers inherited from MyModel, delivering MyModel2 objects (including MyModel2 subclass objects)
    >>> MyModel2.objects.all()
    >>> MyModel2.ordered_objects.all()

Manager inheritance is a somewhat complex topic that needs more
thought and more actual experience with real-world use-cases.

Using a Custom Queryset Class
-----------------------------

The PolymorphicManager class accepts one initialization argument,
which is the queryset class the manager should use. A custom
custom queryset class can be defined and used like this::

        class MyQuerySet(PolymorphicQuerySet):
            def my_queryset_method(...):
                ...
    
        class MyModel(PolymorphicModel):
            my_objects=PolymorphicManager(MyQuerySet)
            ...
    

Performance Considerations
==========================

The current implementation is pretty simple and does not use any
custom sql - it is purely based on the Django ORM. Right now the
query ::

    result_objects = list( ModelA.objects.filter(...) )
    
performs one sql query to retrieve ModelA objects and one additional
query for each unique derived class occurring in result_objects.
The best case for retrieving 100 objects is 1 db query if all are
class ModelA. If 50 objects are ModelA and 50 are ModelB, then two
queries are executed. If result_objects contains only the base model
type (ModelA), the polymorphic models are just as efficient as plain
Django models (in terms of executed queries). The pathological worst
case is 101 db queries if result_objects contains 100 different
object types (with all of them subclasses of ModelA).

Performance ist relative: when Django users create their own
polymorphic ad-hoc solution (without a module like polymorphic.py),
they will tend to use a variation of ::

    result_objects = [ o.get_real_instance() for o in BaseModel.objects.filter(...) ]

which of course has really bad performance. Relative to this, the
performance of the current polymorphic.py is rather good.
It's well possible that the current implementation is already
efficient enough for the majority of use cases.

Chunking: The implementation always requests objects in chunks of
size Polymorphic_QuerySet_objects_per_request. This limits the
complexity/duration for each query, including the pathological cases.


Possible Optimizations
======================

PolymorphicQuerySet can be optimized to require only one sql query
for the queryset evaluation and retrieval of all objects.

Basically, what ist needed is a possibility to pull in the fields
from all relevant sub-models with one sql query. In order to do this
on top of the Django ORM, some kind of enhhancement would be needed.

At first, it looks like a reverse select_related for OneToOne
relations might offer a solution (see http://code.djangoproject.com/ticket/7270)::

    ModelA.objects.filter(...).select_related('modelb','modelb__modelc')

This approach has a number of problems, but nevertheless would
already execute the correct sql query and receive all the model
fields required from the db.

A kind of "select_related for values" might be a better solution::

    ModelA.objects.filter(...).values_related(
        [ base field name list ],  {
            'modelb' : [field name list ],
            'modelb__modelc' : [ field name list ]
        })    

Django's lower level db API in QuerySet.query (see BaseQuery in
django.db.models.sql.query) might still allow other, better or easier
ways to implement the needed functionality.

SQL Complexity 
--------------

Regardless how these queries would be created, their complexity is
the same in any case:

With only one sql query, one sql join for each possible subclass
would be needed (BaseModel.__subclasses__(), recursively).
With two sql queries, the number of joins could be reduced to the
number of actuallly occurring subclasses in the result. A final
implementation might want to use one query only if the number of
possible subclasses (and therefore joins) is not too large, and
two queries otherwise (using the first query to determine the
actually occurring subclasses, reducing the number of joins for
the second).

A relatively large number of joins may be needed in both cases,
which raises concerns regarding the efficiency of these database
queries. It is currently unclear however, how many model classes
will actually be involved in typical use cases - the total number
of classes in the inheritance tree as well as the number of distinct
classes in query results. It may well turn out that the increased
number of joins is no problem for the DBMS in all realistic use
cases. Alternatively, if the sql query execution time is
significantly longer even in common use cases, this may still be
acceptable in exchange for the added functionality.

Let's not forget that all of the above is just about optimizations.
The current simplistic implementation already works well - perhaps
well enough for the majority of applications. 


Restrictions, Caveats, Loose Ends
=================================

Unsupported Queryset Methods
----------------------------

+   aggregate() probably makes only sense in a purely non-OO/relational
    way. So it seems an implementation would just fall back to the
    Django vanilla equivalent.
    
+   annotate(): The current '_get_real_instances' would need minor
    enhancement.

+   defer() and only(): Full support, including slight polymorphism
    enhancements, seems to be straighforward
    (depends on '_get_real_instances'). 

+   extra(): Does not really work with the current implementation of 
    '_get_real_instances'. It's unclear if it should be supported.

+   select_related(): This would probably need Django core support
    for traversing the reverse model inheritance OneToOne relations
    with Django's select_related(), e.g.:
    *select_related('modela__modelb__foreignkeyfield')*.
    Also needs more thought/investigation. 

+   distinct() needs more thought and investigation as well

+   values() & values_list(): Implementation seems to be mostly
    straighforward


Restrictions & Caveats
----------------------

+   Diamond shaped inheritance: There seems to be a general problem 
    with diamond shaped multiple model inheritance with Django models
    (tested with V1.1).
    An example is here: http://code.djangoproject.com/ticket/10808.
    This problem is aggravated when trying to enhance models.Model
    by subclassing it instead of modifying Django core (as we do here
    with PolymorphicModel).
  
+   The name and appname of the leaf model is stored in the base model
    (the base model directly inheriting from PolymorphicModel).
    If a model or an app is renamed, then these fields need to be
    corrected too, if the db content should stay usable after the rename.
    Aside from this, these two fields should probably be combined into
    one field (more db/sql efficiency)

+   For all objects that are not instances of the base class type, but
    instances of a subclass, the base class fields are currently
    transferred twice from the database (an artefact of the current
    implementation's simplicity).

+   __getattribute__ hack: For base model inheritance back relation
    fields (like basemodel_ptr), as well as implicit model inheritance
    forward relation fields, Django internally tries to use our
    polymorphic manager/queryset in some places, which of course it
    should not. Currently this is solved with hackish __getattribute__
    in PolymorphicModel. A minor patch to Django core would probably
    get rid of that.

+   "instance_of" and "not_instance_of" may need some optimization.
 
 
More Investigation Needed
-------------------------

There are a number of subtleties that have not yet been fully evaluated
or resolved, for example (among others) the exact implications of
'use_for_related_fields' in the polymorphic manager.

There may also well be larger issues of conceptual or technical nature
that might basically be showstoppers (but have not yet been found). 


In General
----------   
 
It is important to consider that this code is very experimental
and very insufficiently tested. A number of test cases are included
but they need to be expanded. This implementation is currently more
a tool for exploring the concept of polymorphism within the Django
framework. After careful testing and consideration it may perhaps be
useful for actual projects, but it might be too early for this
right now.


Links
=====

- http://code.djangoproject.com/wiki/ModelInheritance
- http://lazypython.blogspot.com/2009/02/second-look-at-inheritance-and.html
- http://www.djangosnippets.org/snippets/1031/
- http://www.djangosnippets.org/snippets/1034/
- http://groups.google.com/group/django-developers/browse_frm/thread/7d40ad373ebfa912/a20fabc661b7035d?lnk=gst&q=model+inheritance+CORBA#a20fabc661b7035d
- http://groups.google.com/group/django-developers/browse_thread/thread/9bc2aaec0796f4e0/0b92971ffc0aa6f8?lnk=gst&q=inheritance#0b92971ffc0aa6f8
- http://groups.google.com/group/django-developers/browse_thread/thread/3947c594100c4adb/d8c0af3dacad412d?lnk=gst&q=inheritance#d8c0af3dacad412d
- http://groups.google.com/group/django-users/browse_thread/thread/52f72cffebb705e/b76c9d8c89a5574f
- http://peterbraden.co.uk/article/django-inheritance
- http://www.hopelessgeek.com/2009/11/25/a-hack-for-multi-table-inheritance-in-django
- http://stackoverflow.com/questions/929029/how-do-i-access-the-child-classes-of-an-object-in-django-without-knowing-the-name/929982#929982
- http://stackoverflow.com/questions/1581024/django-inheritance-how-to-have-one-method-for-all-subclasses
- http://groups.google.com/group/django-users/browse_thread/thread/cbdaf2273781ccab/e676a537d735d9ef?lnk=gst&q=polymorphic#e676a537d735d9ef
- http://groups.google.com/group/django-users/browse_thread/thread/52f72cffebb705e/bc18c18b2e83881e?lnk=gst&q=model+inheritance#bc18c18b2e83881e
- http://code.djangoproject.com/ticket/10808
- http://code.djangoproject.com/ticket/7270


Copyright
==========

| This code and affiliated files are (C) 2010 Bert Constantin and individual contributors.
| Please see LICENSE for more information. 

"""

from django.db import models
from django.db.models.base import ModelBase
from django.db.models.query import QuerySet
from collections import deque
from pprint import pprint
import copy

# chunk-size: maximum number of objects requested per db-request
# by the polymorphic queryset.iterator() implementation
Polymorphic_QuerySet_objects_per_request = 100

 
###################################################################################
### PolymorphicManager

class PolymorphicManager(models.Manager):
    """
    Manager for PolymorphicModel abstract model.
    
    Usually not explicitly needed, except if a custom manager or
    a custom queryset class is to be used.
    
    For more information, please see module docstring.
    """
    use_for_related_fields = True

    def __init__(self, queryset_class=None, *args, **kwrags):
        if not queryset_class: self.queryset_class = PolymorphicQuerySet
        else: self.queryset_class = queryset_class
        super(PolymorphicManager, self).__init__(*args, **kwrags)
        
    def get_query_set(self):
        return self.queryset_class(self.model)
    
    def __unicode__(self):
        return self.__class__.__name__ + ' (PolymorphicManager) using ' + self.queryset_class.__name__

    # proxies to queryset
    def instance_of(self, *args, **kwargs): return self.get_query_set().instance_of(*args, **kwargs)
    def not_instance_of(self, *args, **kwargs): return self.get_query_set().not_instance_of(*args, **kwargs)


###################################################################################
### PolymorphicQuerySet

class PolymorphicQuerySet(QuerySet):
    """
    QuerySet for PolymorphicModel abstract model
    
    contains the core functionality for PolymorphicModel 
    
    Usually not explicitly needed, except if a custom queryset class
    is to be used (see PolymorphicManager).
    """

    def instance_of(self, *args):
        return self.filter(instance_of=args)

    def not_instance_of(self, *args):
        return self.filter(not_instance_of=args)

    def _filter_or_exclude(self, negate, *args, **kwargs):
        _translate_polymorphic_filter_specs_in_args(self.model, args)
        additional_args = _translate_polymorphic_filter_specs_in_kwargs(self.model, kwargs)
        return super(PolymorphicQuerySet, self)._filter_or_exclude(negate, *(list(args) + additional_args), **kwargs)

    def _get_real_instances(self, base_result_objects):
        """
        Polymorphic object loader
        
        Does the same as:
        
            return [ o.get_real_instance() for o in base_result_objects ]
        
        The list base_result_objects contains the objects from the executed
        base class query. The class of all of them is self.model (our base model).
        
        Some, many or all of these objects were not created and stored as
        class self.model, but as a class derived from self.model. So, these
        objects in base_result_objects have not the class they were created as
        and do not contain all fields of their real class.
        
        We identify them by looking at o.p_classname & o.p_appname, which specify
        the real class of these objects (the class at the time they were saved).
        We replace them by the correct objects, which we fetch from the db.
        
        To do this, we sort the result objects in base_result_objects for their
        subclass first, then execute one db query per subclass of objects,
        and finally re-sort the resulting objects into the correct
        order and return them as a list.
        """
        ordered_id_list = []      # list of ids of result-objects in correct order
        results = {}          # polymorphic dict of result-objects, keyed with their id (no order)

        # dict contains one entry for the different model types occurring in result, keyed by model-name
        # each entry: { 'p_classname': <model name>, 'appname':<model app name>,
        #      'idlist':<list of all result object ids from this model> }
        type_bins = {}
        
        # - sort base_result_objects into bins depending on their real class;
        # - also record the correct result order in ordered_id_list
        for base_object in base_result_objects:
            ordered_id_list.append(base_object.id)

            # this object is not a derived object and already the real instance => store it right away
            if (base_object.p_classname == base_object.__class__.__name__
                and base_object.p_appname == base_object.__class__._meta.app_label):
                results[base_object.id] = base_object

            # this object is derived and its real instance needs to be retrieved
            # => store it's id into the bin for this model type
            else:
                model_key = base_object.p_classname + '-' + base_object.p_appname
                if not model_key in type_bins:
                    type_bins[model_key] = {
                        'classname':base_object.p_classname,
                        'appname':base_object.p_appname,
                        'idlist':[]
                        }
                type_bins[model_key]['idlist'].append(base_object.id)
        
        # for each bin request its objects (the full model) from the db and store them in results[]
        for bin in type_bins.values():
            modelclass = models.get_model(bin['appname'], bin['classname'])
            if modelclass:
                qs = modelclass.base_objects.filter(id__in=bin['idlist'])
                # copy select related configuration to new qs
                # TODO: this does not seem to copy the complete sel_rel-config (field names etc.)
                self.dup_select_related(qs) 
                # TODO: defer(), only() and annotate(): support for these would be around here
                
                for o in qs: results[o.id] = o
        
        resultlist = [ results[ordered_id] for ordered_id in ordered_id_list if ordered_id in results ]
        return resultlist

    def iterator(self):
        """
        This function does the same as:

            base_result_objects=list(super(PolymorphicQuerySet, self).iterator())
            real_results=self._get_get_real_instances(base_result_objects)
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
            
    # these queryset functions are not yet supported
    def defer(self, *args, **kwargs): raise NotImplementedError
    def only(self, *args, **kwargs): raise NotImplementedError
    def aggregate(self, *args, **kwargs): raise NotImplementedError
    def annotate(self, *args, **kwargs): raise NotImplementedError

    def __repr__(self):
        result = [ repr(o) for o in self.all() ]
        return  '[ ' + ',\n  '.join(result) + ' ]' 
        

###################################################################################
### PolymorphicQuerySet support functions

# These functions implement the additional filter- and Q-object functionality.
# They form a kind of small framework for easily adding more
# functionality to filters and Q objects.
# Probably a more general queryset enhancement class could be made out them.
 
def _translate_polymorphic_filter_specs_in_kwargs(queryset_model, kwargs):
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
        # normal filter expression => ignore
        new_expr = _translate_polymorphic_filter_spec(queryset_model, field_path, val)
        if type(new_expr) == tuple:
            # replace kwargs element
            del(kwargs[field_path])
            kwargs[new_expr[0]] = new_expr[1]
        
        elif isinstance(new_expr, models.Q):
            del(kwargs[field_path])
            additional_args.append(new_expr)

    return additional_args
    
def _translate_polymorphic_filter_specs_in_args(queryset_model, args):
    """
    Translate the non-keyword argument list for PolymorphicQuerySet.filter()
    
    In the args list, we replace all kwargs to Q-objects that contain special
    polymorphic functionality with their vanilla django equivalents.
    We traverse the Q object tree for this (which is simple).
    
    Modifies: args list
    """

    def tree_node_correct_field_specs(node):
        " process all children of this Q node "
        for i in range(len(node.children)):
            child = node.children[i]
            
            if type(child) == tuple:
                # this Q object child is a tuple => a kwarg like Q( instance_of=ModelB )
                key, val = child
                new_expr = _translate_polymorphic_filter_spec(queryset_model, key, val)
                if new_expr:
                    node.children[i] = new_expr
            else:
                # this Q object child is another Q object, recursively process this as well
                tree_node_correct_field_specs(child)
                                                
    for q in args:
        if isinstance(q, models.Q):
            tree_node_correct_field_specs(q)

def _translate_polymorphic_filter_spec(queryset_model, field_path, field_val):
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
    classname, sep, pure_field_path = field_path.partition('___')
    if '__' in classname: appname, sep, classname = classname.partition('__')
    else: appname = queryset_model._meta.app_label
    model = models.get_model(appname, classname)
    if not issubclass(model, queryset_model):
        e = 'queryset filter error: "' + model.__name__ + '" is not derived from "' + queryset_model.__name__ + '"'
        raise AssertionError(e)
    
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
    return (newpath, field_val)

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
            assert False, 'instance_of expects a list of models or a single model'

    def q_class_with_subclasses(model):
        q = Q(p_classname=model.__name__) & Q(p_appname=model._meta.app_label)
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
    Manager inheritance is a pretty complex topic which will need
    more thought regarding how this should be handled for polymorphic
    models.
    
    In any case, we probably should propagate 'objects' and 'base_objects'
    from PolymorphicModel to every subclass. We also want to somehow
    inherit _default_manager as well, as it needs to be polymorphic.
    
    The current implementation below is an experiment to solve the
    problem with a very simplistic approach: We unconditionally inherit
    any and all managers (using _copy_to_model), as long as they are
    defined on polymorphic models (the others are left alone).
    
    Like Django ModelBase, we special-case _default_manager:
    if there are any user-defined managers, it is set to the first of these.

    We also require that _default_manager as well as any user defined
    polymorphic managers produce querysets that are derived from
    PolymorphicQuerySet.
    """
    
    def __new__(self, model_name, bases, attrs):
        #print; print '###', model_name, '- bases:', bases
        
        # create new model
        new_class = super(PolymorphicModelBase, self).__new__(self, model_name, bases, attrs)

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
        Return list of all managers to be inherited from the base classes;
        use correct mro, only use managers with _inherited==False,
        skip managers that are overwritten by the user with same-named class attributes (attr)
        """
        add_managers = []; add_managers_keys = set()
        for base in self.__mro__[1:]:
            if not issubclass(base, models.Model): continue
            if not getattr(base,'polymorphic_model_marker',None): continue # leave managers of non-polym. models alone

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
    def validate_model_manager(self, manager, model_name, manager_name):
        """check if the manager is derived from PolymorphicManager
        and its querysets from PolymorphicQuerySet - throw AssertionError if not"""
        
        if not issubclass(type(manager), PolymorphicManager):
            e = '"' + model_name + '.' + manager_name + '" manager is of type "' + type(manager).__name__
            e += '", but must be a subclass of PolymorphicManager'
            raise AssertionError(e)
        if not getattr(manager, 'queryset_class', None) or not issubclass(manager.queryset_class, PolymorphicQuerySet):
            e = '"' + model_name + '.' + manager_name + '" (PolymorphicManager) has been instantiated with a queryset class which is'
            e += ' not a subclass of PolymorphicQuerySet (which is required)'
            raise AssertionError(e)
        return manager
        

###################################################################################
### PolymorphicModel

class PolymorphicModel(models.Model):
    """
    Abstract base class that provides full polymorphism
    to any model directly or indirectly derived from it
    
    For usage instructions & examples please see module docstring.
    
    PolymorphicModel declares two fields for internal use (p_classname
    and p_appname) and provides a polymorphic manager as the
    default manager (and as 'objects').
    
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

    p_classname = models.CharField(max_length=100, default='')
    p_appname = models.CharField(max_length=50, default='')

    # some applications want to know the name of fields that are added to its models
    polymorphic_internal_model_fields = [ 'p_classname', 'p_appname' ]

    objects = PolymorphicManager()
    base_objects = models.Manager()

    def save(self, *args, **kwargs):
        """Overridden model save function which supports the polymorphism
        functionality. If your derived class overrides save() as well, then you
        need to take care that you correctly call the save() method of
        the superclass.
        
        When the object is saved for the first time, we store its real class and app name
        into p_classname and p_appname. When the object later is retrieved by
        PolymorphicQuerySet, it uses these fields to figure out the real type of this object
        (used by PolymorphicQuerySet._get_real_instances)"""
        if not self.p_classname:
            self.p_classname = self.__class__.__name__
            self.p_appname = self.__class__._meta.app_label
        return super(PolymorphicModel, self).save(*args, **kwargs)

    def get_real_instance_class(self):
        """Normally not needed - only if a non-polymorphic manager
        (like base_objects) has been used to retrieve objects.
        Then these objects have the wrong class (the base class).
        This function returns the real/correct class for this object.""" 
        return models.get_model(self.p_appname, self.p_classname)
    
    def get_real_instance(self):
        """Normally not needed - only if a non-polymorphic manager
        (like base_objects) has been used to retrieve objects.
        Then these objects have the wrong class (the base class).
        This function returns the real object with the correct class
        and content. Each method call executes one db query.""" 
        if self.p_classname == self.__class__.__name__ and self.p_appname == self.__class__._meta.app_label:
            return self
        return self.get_real_instance_class().objects.get(id=self.id)

    # Hack: 
    # For base model back reference fields (like basemodel_ptr), Django should =not= use our polymorphic manager/queryset.
    # For now, we catch objects attribute access here and handle back reference fields manually.
    # This problem is triggered by delete(), like here: django.db.models.base._collect_sub_objects: parent_obj = getattr(self, link.name)
    # TODO: investigate Django how this can be avoided
    def __getattribute__(self, name):
        if name != '__class__':
            modelname = name.rstrip('_ptr')
            model = self.__class__.sub_and_superclass_dict.get(modelname, None)
            if model: 
                id = super(PolymorphicModel, self).__getattribute__('id')
                attr = model.base_objects.get(id=id)
                return attr

        return super(PolymorphicModel, self).__getattribute__(name)

    # support for __getattribute__: create sub_and_superclass_dict,
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
        "output object descriptions as seen in module docstring"
        out = self.__class__.__name__ + ': id %d, ' % (self.id or - 1); last = self._meta.fields[-1]
        for f in self._meta.fields:
            if f.name in [ 'id', 'p_classname', 'p_appname' ] or 'ptr' in f.name: continue
            out += f.name + ' (' + type(f).__name__ + ')'
            if f != last:  out += ', '
        return '<' + out + '>'
    

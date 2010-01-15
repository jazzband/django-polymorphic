
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

    Third party models can be used as polymorphic models without any
    restrictions by simply subclassing them. E.g. using a third party
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
inherits all managers from the base models. An example::

    class MyModel2(MyModel):
        pass

    # Managers inherited from MyModel
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


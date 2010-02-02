.. contents:: Table of Contents
    :depth: 1

Installation / Testing
======================

Requirements
------------

Django 1.1 (or later) and Python 2.5 (or later). This code has been tested
on Django 1.1.1 / 1.2 alpha and Python 2.5.4 / 2.6.4 on Linux.

Testing
-------

The repository (or tar file)  contains a complete Django project
that may be used for tests or experiments.

To run the included test suite, execute::

    ./manage test polymorphic

The management command ``pcmd.py`` in the app ``pexp`` (Polymorphic EXPerimenting)
can be used for experiments - modify this file (pexp/management/commands/pcmd.py)
to your liking, then run::

    ./manage syncdb      # db is created in /var/tmp/... (settings.py)
    ./manage pcmd
    
Installation
------------

In the directory "django_polymorphic", execute ``sudo python setup.py install``.

Alternatively you can simply copy the ``polymorphic`` directory
(under "django_polymorphic") into your Django project dir.

If you want to use the management command ``polymorphic_dumpdata``, then
you need to add ``polymorphic`` to your INSTALLED_APPS setting.

In any case, Django's ContentType framework (``django.contrib.contenttypes``)
needs to be listed in INSTALLED_APPS (usually it already is).



Defining Polymorphic Models
===========================

To make models polymorphic, use ``PolymorphicModel`` instead of Django's
``models.Model`` as the superclass of your base model. All models
inheriting from your base class will be polymorphic as well::

    from polymorphic.models import PolymorphicModel    

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
    syntax: ``exact model name + three _ + field name``):
    
    >>> ModelA.objects.filter(  Q(ModelB___field2 = 'B2') | Q(ModelC___field3 = 'C3')  )
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
        
    then field1 may now also refer to objects of type ``ModelB`` or ``ModelC``.
    
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
    
More Queryset Methods
---------------------

+   ``annotate()`` and ``aggregate()`` work just as usual, with the
    addition that the ``ModelX___field`` syntax can be used for the
    keyword arguments (but not for the non-keyword arguments).
    
+   ``order_by()`` now similarly supports the ``ModelX___field`` syntax
    for specifying ordering through a field in a submodel.

+   ``distinct()`` works as expected. It only regards the fields of
    the base class, but this should never make a difference.

+   ``select_related()`` works just as usual, but it can not (yet) be used
    to select relations in derived models
    (like ``ModelA.objects.select_related('ModelC___fieldxy')`` )

+   ``extra()`` by default works exactly like the original version,
    with the resulting queryset not being polymorphic. There is
    experimental support for a polymorphic extra() via the keyword
    argument ``polymorphic=True`` (only the ``where`` and
    ``order_by`` arguments of extra() should be used then).

+   ``values()`` & ``values_list()`` currently do not return polymorphic
    results. This may change in the future however. If you want to use these
    methods now, it's best if you use ``Model.base_objects.values...`` as
    this is guaranteed to not change. 

+   ``defer()`` and ``only()`` are not yet supported (support will be added
    in the future). 

manage.py dumpdata
------------------
    
    Django's standard ``dumpdata`` command requires non-polymorphic
    behaviour from the querysets it uses and produces incomplete
    results with polymorphic models. Django_polymorphic includes
    a slightly modified version, named ``polymorphic_dumpdata``
    that fixes this. Just use this command instead of Django's
    (see "installation/testing").

    Please note that there are problems using ContentType together
    with Django's seralisation or fixtures (and all polymorphic models
    use ContentType). This issue seems to be resolved with Django 1.2
    (changeset 11863): http://code.djangoproject.com/ticket/7052
    

Custom Managers, Querysets & Inheritance
========================================
    
Using a Custom Manager
----------------------

For creating a custom polymorphic manager class, derive your manager
from ``PolymorphicManager`` instead of ``models.Manager``. In your model
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
the plain ``PolymorphicManager`` here.

Manager Inheritance
-------------------

Polymorphic models inherit/propagate all managers from their
base models, as long as these are polymorphic. This means that all
managers defined in polymorphic base models work just the same as if
they were defined in the new model.

An example (inheriting from MyModel above)::

    class MyModel2(MyModel):
        pass

    # Managers inherited from MyModel:
    # the regular 'objects' manager and the custom 'ordered_objects' manager
    >>> MyModel2.objects.all()
    >>> MyModel2.ordered_objects.all()

Using a Custom Queryset Class
-----------------------------

The ``PolymorphicManager`` class accepts one initialization argument,
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
custom SQL - it is purely based on the Django ORM. Right now the
query ::

    result_objects = list( ModelA.objects.filter(...) )
    
performs one SQL query to retrieve ``ModelA`` objects and one additional
query for each unique derived class occurring in result_objects.
The best case for retrieving 100 objects is 1 db query if all are
class ``ModelA``. If 50 objects are ``ModelA`` and 50 are ``ModelB``, then
two queries are executed. If result_objects contains only the base model
type (``ModelA``), the polymorphic models are just as efficient as plain
Django models (in terms of executed queries). The pathological worst
case is 101 db queries if result_objects contains 100 different
object types (with all of them subclasses of ``ModelA``).

Performance ist relative: when Django users create their own
polymorphic ad-hoc solution (without a tool like ``django_polymorphic``),
this usually results in a variation of ::

    result_objects = [ o.get_real_instance() for o in BaseModel.objects.filter(...) ]

which has really bad performance. Relative to this, the
performance of the current ``django_polymorphic`` is pretty good.
It may well be efficient enough for the majority of use cases.

Chunking: The implementation always requests objects in chunks of
size ``Polymorphic_QuerySet_objects_per_request``. This limits the
complexity/duration for each query, including the pathological cases.


Possible Optimizations
======================

``PolymorphicQuerySet`` can be optimized to require only one SQL query
for the queryset evaluation and retrieval of all objects.

Basically, what ist needed is a possibility to pull in the fields
from all relevant sub-models with one SQL query. However, some deeper
digging into the Django database layer will be required in order to
make this happen.

A viable option might be to get the SQL query from the QuerySet
(probably from ``django.db.models.SQL.compiler.SQLCompiler.as_sql``), 
making sure that all necessary joins are done, and then doing a
custom SQL request from there (like in ``SQLCompiler.execute_sql``).

An optimized version could fall back to the current ORM-only
implementation for all non-SQL databases.

SQL Complexity 
--------------

With only one SQL query, one SQL join for each possible subclass
would be needed (``BaseModel.__subclasses__()``, recursively).
With two SQL queries, the number of joins could be reduced to the
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
cases. Alternatively, if the SQL query execution time is
significantly longer even in common use cases, this may still be
acceptable in exchange for the added functionality.

In General 
----------

Let's not forget that all of the above is just about optimization.
The current implementation already works well - and perhaps well
enough for the majority of applications. 

Also, it seems that further optimization (down to one DB request)
would be restricted to a relatively small area of the code, and
be mostly independent from the rest of the module.
So it seems this optimization can be done at any later time
(like when it's needed).


Restrictions & Caveats
======================

*   The queryset methods ``values()``, ``values_list()``, ``select_related()``, 
    ``defer()`` and ``only()`` are not yet fully supported (see above)

*   Django 1.1 only - the names of polymorphic models must be unique
    in the whole project, even if they are in two different apps.
    This results from a restriction in the Django 1.1 "related_name"
    option (fixed in Django 1.2).

*   Django 1.1 only - when ContentType is used in models, Django's
    seralisation or fixtures cannot be used. This issue seems to be
    resolved for Django 1.2 (changeset 11863: Fixed #7052, Added support
    for natural keys in serialization).
  
    + http://code.djangoproject.com/ticket/7052
    + http://stackoverflow.com/questions/853796/problems-with-contenttypes-when-loading-a-fixture-in-django

*   Diamond shaped inheritance: There seems to be a general problem 
    with diamond shaped multiple model inheritance with Django models
    (tested with V1.1).
    An example is here: http://code.djangoproject.com/ticket/10808.
    This problem is aggravated when trying to enhance models.Model
    by subclassing it instead of modifying Django core (as we do here
    with PolymorphicModel).
  
*   A reference (``ContentType``) to the real/leaf model is stored
    in the base model (the base model directly inheriting from
    PolymorphicModel). If a model or an app is renamed, then Django's
    ContentType table needs to be corrected too, if the db content
    should stay usable after the rename.
    
*   For all objects that are not instances of the base class, but
    instances of a subclass, the base class fields are currently
    transferred twice from the database (an artefact of the current
    implementation's simplicity).

*   __getattribute__ hack: For base model inheritance back relation
    fields (like basemodel_ptr), as well as implicit model inheritance
    forward relation fields, Django internally tries to use our
    polymorphic manager/queryset in some places, which of course it
    should not. Currently this is solved with a hacky __getattribute__
    in PolymorphicModel, which causes some overhead. A minor patch to
    Django core would probably get rid of that.

Project Status
--------------   
 
It's important to consider that this code is very new and
to some extent still experimental. Please see the docs for
current restrictions, caveats, and performance implications.

It does seem to work very well for a number of people, but
API changes, code reorganisations or further schema changes
are still a possibility. There may also remain larger bugs
and problems in the code that have not yet been found.


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


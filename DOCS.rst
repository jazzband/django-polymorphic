Polymorphic Models for Django
=============================

.. contents:: Table of Contents
    :depth: 1


Quickstart
===========

Install
-------

After uncompressing (if necessary), in the directory "...django_polymorphic",
execute  (on Unix-like systems)::

    sudo python setup.py install

Make Your Models Polymorphic
----------------------------

Use ``PolymorphicModel`` instead of Django's ``models.Model``, like so::

    from polymorphic import PolymorphicModel

    class Project(PolymorphicModel):
            topic = models.CharField(max_length=30)

    class ArtProject(Project):
            artist = models.CharField(max_length=30)

    class ResearchProject(Project):
            supervisor = models.CharField(max_length=30)

All models inheriting from your polymorphic models will be polymorphic as well.

Create some objects
-------------------

>>> Project.objects.create(topic="Department Party")
>>> ArtProject.objects.create(topic="Painting with Tim", artist="T. Turner")
>>> ResearchProject.objects.create(topic="Swallow Aerodynamics", supervisor="Dr. Winter")

Get polymorphic query results
-----------------------------

>>> Project.objects.all()
[ <Project:         id 1, topic "Department Party">,
  <ArtProject:      id 2, topic "Painting with Tim", artist "T. Turner">,
  <ResearchProject: id 3, topic "Swallow Aerodynamics", supervisor "Dr. Winter"> ]

use ``instance_of`` or ``not_instance_of`` for narrowing the result to specific subtypes:

>>> Project.objects.instance_of(ArtProject)
[ <ArtProject:      id 2, topic "Painting with Tim", artist "T. Turner"> ]

>>> Project.objects.instance_of(ArtProject) | Project.objects.instance_of(ResearchProject)
[ <ArtProject:      id 2, topic "Painting with Tim", artist "T. Turner">,
  <ResearchProject: id 3, topic "Swallow Aerodynamics", supervisor "Dr. Winter"> ]

Polymorphic filtering: Get all projects where Mr. Turner is involved as an artist
or supervisor (note the three underscores):

>>> Project.objects.filter(  Q(ArtProject___artist = 'T. Turner') | Q(ResearchProject___supervisor = 'T. Turner')  )
[ <ArtProject:      id 2, topic "Painting with Tim", artist "T. Turner">,
  <ResearchProject: id 4, topic "Color Use in Late Cubism", supervisor "T. Turner"> ]

This is basically all you need to know, as django_polymorphic mostly
works fully automatic and just delivers the expected ("pythonic") results.

Note: In all example output, above and below, for a nicer and more informative
output the ``ShowFieldType`` mixin has been used (documented below).


List of Features
================

*   Fully automatic - generally makes sure that the same objects are
    returned from the database that were stored there, regardless how
    they are retrieved
*   Only on models that request polymorphic behaviour (and the
    models inheriting from them)
*   Full support for ForeignKeys, ManyToManyFields and OneToToneFields
*   Filtering for classes, equivalent to python's isinstance():
    ``instance_of(...)`` and ``not_instance_of(...)``
*   Polymorphic filtering/ordering etc., allowing the use of fields of
    derived models ("ArtProject___artist")
*   Support for user-defined custom managers
*   Automatic inheritance of custom managers
*   Support for user-defined custom queryset classes
*   Non-polymorphic queries if needed, with no other change in
    features/behaviour
*   Combining querysets of different types/models ("qs3 = qs1 | qs2")
*   Nice/informative display of polymorphic queryset results


More about Installation / Testing
=================================

Requirements
------------

Django 1.1 (or later) and Python 2.4 or later. This code has been tested
on Django 1.1 / 1.2 / 1.3 and Python 2.4.6 / 2.5.4 / 2.6.4 on Linux.

Included Test Suite
-------------------

The repository (or tar file) contains a complete Django project
that may be used for tests or experiments, without any installation needed.

To run the included test suite, in the directory "...django_polymorphic" execute::

    ./manage test polymorphic

The management command ``pcmd.py`` in the app ``pexp`` can be used
for quick tests or experiments - modify this file (pexp/management/commands/pcmd.py)
to your liking, then run::

    ./manage syncdb      # db is created in /var/tmp/... (settings.py)
    ./manage pcmd

Installation
------------

In the directory "...django_polymorphic", execute ``sudo python setup.py install``.

Alternatively you can simply copy the ``polymorphic`` subdirectory
(under "django_polymorphic") into your Django project dir
(e.g. if you want to distribute your project with more 'batteries included').

If you want to run the test cases in `polymorphic/tests.py`, you need to add
``polymorphic`` to your INSTALLED_APPS setting.

Django's ContentType framework (``django.contrib.contenttypes``)
needs to be listed in INSTALLED_APPS (usually it already is).


More Polymorphic Functionality
==============================

In the examples below, these models are being used::

    from polymorphic import PolymorphicModel

    class ModelA(PolymorphicModel):
        field1 = models.CharField(max_length=10)

    class ModelB(ModelA):
        field2 = models.CharField(max_length=10)

    class ModelC(ModelB):
        field3 = models.CharField(max_length=10)


Filtering for classes (equivalent to python's isinstance() ):
-------------------------------------------------------------

>>> ModelA.objects.instance_of(ModelB)
.
[ <ModelB: id 2, field1 (CharField), field2 (CharField)>,
  <ModelC: id 3, field1 (CharField), field2 (CharField), field3 (CharField)> ]

In general, including or excluding parts of the inheritance tree::

    ModelA.objects.instance_of(ModelB [, ModelC ...])
    ModelA.objects.not_instance_of(ModelB [, ModelC ...])

You can also use this feature in Q-objects (with the same result as above):

>>> ModelA.objects.filter( Q(instance_of=ModelB) )


Polymorphic filtering (for fields in derived classes)
-----------------------------------------------------

For example, cherrypicking objects from multiple derived classes
anywhere in the inheritance tree, using Q objects (with the
syntax: ``exact model name + three _ + field name``):

>>> ModelA.objects.filter(  Q(ModelB___field2 = 'B2') | Q(ModelC___field3 = 'C3')  )
.
[ <ModelB: id 2, field1 (CharField), field2 (CharField)>,
  <ModelC: id 3, field1 (CharField), field2 (CharField), field3 (CharField)> ]


Combining Querysets
-------------------

Querysets could now be regarded as object containers that allow the
aggregation of different object types, very similar to python
lists - as long as the objects are accessed through the manager of
a common base class:

>>> Base.objects.instance_of(ModelX) | Base.objects.instance_of(ModelY)
.
[ <ModelX: id 1, field_x (CharField)>,
  <ModelY: id 2, field_y (CharField)> ]


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


Using Third Party Models (without modifying them)
-------------------------------------------------

Third party models can be used as polymorphic models without
restrictions by subclassing them. E.g. using a third party
model as the root of a polymorphic inheritance tree::

    from thirdparty import ThirdPartyModel

    class MyThirdPartyBaseModel(PolymorhpicModel, ThirdPartyModel):
        pass    # or add fields

Or instead integrating the third party model anywhere into an
existing polymorphic inheritance tree::

    class MyBaseModel(SomePolymorphicModel):
        my_field = models.CharField(max_length=10)

    class MyModelWithThirdParty(MyBaseModel, ThirdPartyModel):
        pass    # or add fields


Non-Polymorphic Queries
-----------------------

If you insert ``.non_polymorphic()`` anywhere into the query chain, then
django_polymorphic will simply leave out the final step of retrieving the
real objects, and the manager/queryset will return objects of the type of
the base class you used for the query, like vanilla Django would
(``ModelA`` in this example). 

>>> qs=ModelA.objects.non_polymorphic().all()
>>> qs
[ <ModelA: id 1, field1 (CharField)>,
  <ModelA: id 2, field1 (CharField)>,
  <ModelA: id 3, field1 (CharField)> ]

There are no other changes in the behaviour of the queryset. For example,
enhancements for ``filter()`` or ``instance_of()`` etc. still work as expected.
If you do the final step yourself, you get the usual polymorphic result:

>>> ModelA.objects.get_real_instances(qs)
[ <ModelA: id 1, field1 (CharField)>,
  <ModelB: id 2, field1 (CharField), field2 (CharField)>,
  <ModelC: id 3, field1 (CharField), field2 (CharField), field3 (CharField)> ]


About Queryset Methods
----------------------

*   ``annotate()`` and ``aggregate()`` work just as usual, with the
    addition that the ``ModelX___field`` syntax can be used for the
    keyword arguments (but not for the non-keyword arguments).

*   ``order_by()`` now similarly supports the ``ModelX___field`` syntax
    for specifying ordering through a field in a submodel.

*   ``distinct()`` works as expected. It only regards the fields of
    the base class, but this should never make a difference.

*   ``select_related()`` works just as usual, but it can not (yet) be used
    to select relations in derived models
    (like ``ModelA.objects.select_related('ModelC___fieldxy')`` )

*   ``extra()`` works as expected (it returns polymorphic results) but
    currently has one restriction: The resulting objects are required to have
    a unique primary key within the result set - otherwise an error is thrown
    (this case could be made to work, however it may be mostly unneeded)..
    The keyword-argument "polymorphic" is no longer supported.
    You can get back the old non-polymorphic behaviour (before V1.0)
    by using ``ModelA.objects.non_polymorphic().extra(...)``.

*   ``get_real_instances()`` allows you to turn a
    queryset or list  of base model objects efficiently into the real objects.
    For example, you could do ``base_objects_queryset=ModelA.extra(...).non_polymorphic()``
    and then call ``real_objects=base_objects_queryset.get_real_instances()``.Or alternatively
    .``real_objects=ModelA.objects..get_real_instances(base_objects_queryset_or_object_list)``

*   ``values()`` & ``values_list()`` currently do not return polymorphic
    results. This may change in the future however. If you want to use these
    methods now, it's best if you use ``Model.base_objects.values...`` as
    this is guaranteed to not change. 

*   ``defer()`` and ``only()`` are not yet supported (support will be added
    in the future). 


Using enhanced Q-objects in any Places
--------------------------------------

The queryset enhancements (e.g. ``instance_of``) only work as arguments
to the member functions of a polymorphic queryset.  Occationally it may
be useful to be able to use Q objects with these enhancements in other places.
As Django doesn't understand these enhanced Q objects, you need to
transform them manually into normal Q objects before you can feed them
to a Django queryset or function::

    normal_q_object = ModelA.translate_polymorphic_Q_object( Q(instance_of=Model2B) )

This function cannot be used at model creation time however (in models.py),
as it may need to access the ContentTypes database table.


Nicely Displaying Polymorphic Querysets
---------------------------------------

In order to get the output as seen in all examples here, you need to use the
ShowFieldType class mixin::

    from polymorphic import PolymorphicModel, ShowFieldType

    class ModelA(ShowFieldType, PolymorphicModel):
        field1 = models.CharField(max_length=10)

You may also use ShowFieldContent or ShowFieldTypeAndContent to display
additional information when printing querysets (or converting them to text).

When showing field contents, they will be truncated to 20 characters. You can
modify this behaviour by setting a class variable in your model like this::

    class ModelA(ShowFieldType, PolymorphicModel):
        polymorphic_showfield_max_field_width = 20
        ...

Similarly, pre-V1.0 output formatting can be re-estated by using
``polymorphic_showfield_old_format = True``.

Custom Managers, Querysets & Manager Inheritance
================================================
    
Using a Custom Manager
----------------------

A nice feature of Django is the possibility to define one's own custom object managers.
This is fully supported with django_polymorphic: For creating a custom polymorphic
manager class, just derive your manager from ``PolymorphicManager`` instead of
``models.Manager``. As with vanilla Django, in your model class, you should
explicitly add the default manager first, and then your custom manager::

    from polymorphic import PolymorphicModel, PolymorphicManager

   class TimeOrderedManager(PolymorphicManager):
        def get_query_set(self):
            qs = super(TimeOrderedManager,self).get_query_set()
            return qs.order_by('-start_date')        # order the queryset

        def most_recent(self):
            qs = self.get_query_set()                # get my ordered queryset
            return qs[:10]                           # limit => get ten most recent entries

    class Project(PolymorphicModel):
        objects = PolymorphicManager()               # add the default polymorphic manager first
        objects_ordered = TimeOrderedManager()       # then add your own manager
        start_date = DateTimeField()                 # project start is this date/time

The first manager defined ('objects' in the example) is used by
Django as automatic manager for several purposes, including accessing
related objects. It must not filter objects and it's safest to use
the plain ``PolymorphicManager`` here.

Manager Inheritance
-------------------

Polymorphic models inherit/propagate all managers from their
base models, as long as these are polymorphic. This means that all
managers defined in polymorphic base models continue to work as
expected in models inheriting from this base model::

   from polymorphic import PolymorphicModel, PolymorphicManager

   class TimeOrderedManager(PolymorphicManager):
        def get_query_set(self):
            qs = super(TimeOrderedManager,self).get_query_set()
            return qs.order_by('-start_date')        # order the queryset

        def most_recent(self):
            qs = self.get_query_set()                # get my ordered queryset
            return qs[:10]                           # limit => get ten most recent entries

    class Project(PolymorphicModel):
        objects = PolymorphicManager()               # add the default polymorphic manager first
        objects_ordered = TimeOrderedManager()       # then add your own manager
        start_date = DateTimeField()                 # project start is this date/time

    class ArtProject(Project):                       # inherit from Project, inheriting its fields and managers
        artist = models.CharField(max_length=30)

ArtProject inherited the managers ``objects`` and ``objects_ordered`` from Project.

``ArtProject.objects_ordered.all()`` will return all art projects ordered
regarding their start time and ``ArtProject.objects_ordered.most_recent()``
will return the ten most recent art projects.
.

Using a Custom Queryset Class
-----------------------------

The ``PolymorphicManager`` class accepts one initialization argument,
which is the queryset class the manager should use. Just as with vanilla Django,
you may define your own custom queryset classes. Just use PolymorphicQuerySet
instead of Django's QuerySet as the base class::

        from polymorphic import PolymorphicModel, PolymorphicManager, PolymorphicQuerySet

        class MyQuerySet(PolymorphicQuerySet):
            def my_queryset_method(...):
                ...
    
        class MyModel(PolymorphicModel):
            my_objects=PolymorphicManager(MyQuerySet)
            ...


Performance Considerations
==========================

The current implementation is rather simple and does not use any
custom SQL or Django DB layer internals - it is purely based on the
standard Django ORM.

Specifically, the query::

    result_objects = list( ModelA.objects.filter(...) )

performs one SQL query to retrieve ``ModelA`` objects and one additional
query for each unique derived class occurring in result_objects.
The best case for retrieving 100 objects is 1 SQL query if all are
class ``ModelA``. If 50 objects are ``ModelA`` and 50 are ``ModelB``, then
two queries are executed. The pathological worst case is 101 db queries if
result_objects contains 100 different object types (with all of them
subclasses of ``ModelA``).

Usually, when Django users create their own polymorphic ad-hoc solution
without a tool like django_polymorphic, this usually results in a variation of ::

    result_objects = [ o.get_real_instance() for o in BaseModel.objects.filter(...) ]

which has very bad performance, as it introduces one additional
SQL query for every object in the result which is not of class ``BaseModel``.

Compared to these solutions, django_polymorphic has the advantage
that it only needs one sql request per *object type*, and not *per object*.

.. _performance:

Performance Problems with PostgreSQL, MySQL and SQLite3
-------------------------------------------------------

Current relational DBM systems seem to have general problems with
the SQL queries produced by object relational mappers like the Django
ORM, if these use multi-table inheritance like Django's ORM does.
The "inner joins" in these queries can perform very badly.
This is independent of django_polymorphic and affects all uses of
multi table Model inheritance.

Concrete benchmark results are forthcoming (please see discussion forum).

Please also see this `post (and comments) from Jacob Kaplan-Moss`_.

.. _post (and comments) from Jacob Kaplan-Moss: http://www.jacobian.org/writing/concrete-inheritance/


.. _restrictions:

Restrictions & Caveats
======================

*   Database Performance regarding concrete Model inheritance in general.
    Please see "Performance Problems" above.

*   Queryset methods ``values()``, ``values_list()``, ``select_related()``,
    ``defer()`` and ``only()`` are not yet fully supported (see above).
    ``extra()`` has one restriction: the resulting objects are required to have
    a unique primary key within the result set.

*   Django Admin Integration: There currently is no specific admin integration,
    but it would most likely make sense to have one.

*   Diamond shaped inheritance: There seems to be a general problem 
    with diamond shaped multiple model inheritance with Django models
    (tested with V1.1 - V1.3).
    An example is here: http://code.djangoproject.com/ticket/10808.
    This problem is aggravated when trying to enhance models.Model
    by subclassing it instead of modifying Django core (as we do here
    with PolymorphicModel).

*   The enhanced filter-definitions/Q-objects only work as arguments
    for the methods of the polymorphic querysets. Please see above
    for ``translate_polymorphic_Q_object``.

*   A reference (``ContentType``) to the real/leaf model is stored
    in the base model (the base model directly inheriting from
    PolymorphicModel). You need to be aware of this when using the
    ``dumpdata`` management command or any other low-level
    database operations. E.g. if you rename models or apps or copy
    objects from one database to another, then Django's ContentType
    table needs to be corrected/copied too. This is of course generally
    the case for any models using Django's ContentType.

*   Django 1.1 only - the names of polymorphic models must be unique
    in the whole project, even if they are in two different apps.
    This results from a restriction in the Django 1.1 "related_name"
    option (fixed in Django 1.2).

*   Django 1.1 only - when ContentType is used in models, Django's
    seralisation or fixtures cannot be used (all polymorphic models
    use ContentType). This issue seems to be resolved for Django 1.2
    (changeset 11863: Fixed #7052, Added support for natural keys in serialization).

    + http://code.djangoproject.com/ticket/7052
    + http://stackoverflow.com/questions/853796/problems-with-contenttypes-when-loading-a-fixture-in-django


Project Status
==============   
 
Django_polymorphic works well for a considerable number of users now,
and no major problems have shown up for many months.
The API can be considered stable beginning with the V1.0 release.


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


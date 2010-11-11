Polymorphic Models for Django
=============================


Quick Start, Docs, Contributing
-------------------------------

* `What is django_polymorphic good for?`_
* `Quickstart`_, or the complete `Installation and Usage Docs`_
* `Release Notes, News and Discussion`_ (Google Group) or Changelog_
* Download from GitHub_ or Bitbucket_, or as TGZ_ or ZIP_
* Improve django_polymorphic, report issues, discuss, patch or fork (GitHub_, Bitbucket_, Group_, Mail_)

.. _What is django_polymorphic good for?: #good-for
.. _release notes, news and discussion: http://groups.google.de/group/django-polymorphic/topics
.. _Group: http://groups.google.de/group/django-polymorphic/topics
.. _Mail: http://github.com/bconstantin/django_polymorphic/tree/master/setup.py
.. _Installation and Usage Docs: http://bserve.webhop.org/django_polymorphic/DOCS.html
.. _Quickstart: http://bserve.webhop.org/django_polymorphic/DOCS.html#quickstart
.. _GitHub: http://github.com/bconstantin/django_polymorphic
.. _Bitbucket: http://bitbucket.org/bconstantin/django_polymorphic
.. _TGZ: http://github.com/bconstantin/django_polymorphic/tarball/master
.. _ZIP: http://github.com/bconstantin/django_polymorphic/zipball/master
.. _Overview: http://bserve.webhop.org/django_polymorphic
.. _Changelog: http://bserve.webhop.org/django_polymorphic/CHANGES.html

.. _good-for:

What is django_polymorphic good for?
------------------------------------

Let's assume the models ``ArtProject`` and ``ResearchProject`` are derived
from the model ``Project``, and let's store one of each into the database:

>>> Project.objects.create(topic="Department Party")
>>> ArtProject.objects.create(topic="Painting with Tim", artist="T. Turner")
>>> ResearchProject.objects.create(topic="Swallow Aerodynamics", supervisor="Dr. Winter")

If we want to retrieve all our projects, we do:

>>> Project.objects.all()

Using django_polymorphic, we simply get what we stored::

    [ <Project:         id 1, topic "Department Party">,
      <ArtProject:      id 2, topic "Painting with Tim", artist "T. Turner">,
      <ResearchProject: id 3, topic "Swallow Aerodynamics", supervisor "Dr. Winter"> ]

Using vanilla Django, we get incomplete objects, which is probably not what we wanted::

    [ <Project: id 1, topic "Department Party">,
      <Project: id 2, topic "Painting with Tim">,
      <Project: id 3, topic "Swallow Aerodynamics"> ]

It's very similar for ForeignKeys, ManyToManyFields or OneToOneFields.

In general, the effect of django_polymorphic is twofold:

On one hand it makes sure that model inheritance just works as you
expect, by simply ensuring that you always get back exactly the same
objects from the database you stored there - regardless how you access
them, making model inheritance much more "pythonic".
This can save you a lot of unpleasant workarounds that tend to
make your code messy, error-prone, and slow.

On the other hand, together with some small API additions to the Django
ORM, django_polymorphic enables a much more expressive and intuitive
programming style and also very advanced object oriented designs
that are not possible with vanilla Django.

Fortunately, most of the heavy duty machinery that is needed for this
functionality is already present in the original Django database layer.
Django_polymorphic adds a rather thin layer above that in order
to make real OO fully automatic and very easy to use.

There is a catch however, which applies to concrete model inheritance
in general: Current DBM systems like PostgreSQL or MySQL are not very
good at processing the required sql queries and can be rather slow in
many cases. Concrete benchmarks are forthcoming (please see
discussion forum).

For more information, please look at `Quickstart`_ or at the complete
`Installation and Usage Docs`_ and also see the `restrictions and caveats`_.

.. _restrictions and caveats: http://bserve.webhop.org/django_polymorphic/DOCS.html#restrictions


This is a V1.0 Beta/Testing Release
-----------------------------------

The release contains a considerable amount of changes in some of the more
critical parts of the software. It's intended for testing and development
environments and not for production environments. For these, it's best to
wait a few weeks for the proper V1.0 release, to allow some time for any
potential problems to turn up (if they exist).

If you encounter any problems or have suggestions regarding the API or the
changes in this beta, please post them in the `discussion group`_
or open an issue on GitHub_ or BitBucket_ (or send me an email).

.. _discussion group: http://groups.google.de/group/django-polymorphic/topics


License
=======

Django_polymorphic uses the same license as Django (BSD-like).


API Changes & Additions
=======================


November 11 2010, V1.0 API Changes
-------------------------------------------------------------------

extra() queryset method
+++++++++++++++++++++++

``.extra()`` has been re-implemented. Now it's polymorphic by
default and works (nearly) without restrictions (please see docs). This is a (very)
incompatible API change regarding previous versions of django_polymorphic.
Support for the ``polymorphic`` keyword parameter has been removed.
You can get back the non-polymorphic behaviour by using
``ModelA.objects.non_polymorphic().extra()``.

No Pretty-Printing of Querysets by default
++++++++++++++++++++++++++++++++++++++++++

In order to improve compatibility with vanilla Django, printing quersets
(__repr__ and __unicode__) does not use django_polymorphic's pretty printing
by default anymore. To get the old behaviour when printing querysets,
you need to replace your model definition:

>>> class Project(PolymorphicModel):

by:

>>> class Project(PolymorphicModel, ShowFieldType):

The mixin classes for pretty output have been renamed:

    ``ShowFieldTypes, ShowFields, ShowFieldsAndTypes``

are now:

    ``ShowFieldType, ShowFieldContent and ShowFieldTypeAndContent``

(the old ones still exist for compatibility)

Pretty-Printing Output Format Changed
+++++++++++++++++++++++++++++++++++++

``ShowFieldContent`` and ``ShowFieldTypeAndContent`` now
use a slightly different output format. If this causes too much trouble for
your test cases, you can get the old behaviour back (mostly) by adding
``polymorphic_showfield_old_format = True`` to your model definitions.
``ShowField...`` now also produces more informative output for custom
primary keys.

polymorphic_dumpdata
++++++++++++++++++++

The ``polymorphic_dumpdata`` management command is not needed anymore
and has been disabled, as the regular Django dumpdata command now automatically
works correctly with polymorphic models (for all supported versions of Django).

Running the Test suite with Django 1.3
++++++++++++++++++++++++++++++++++++++

Django 1.3 requires ``python manage.py test polymorphic`` instead of
just ``python manage.py test``.


November 01 2010, V1.0 API Additions
-------------------------------------------------------------------

*   ``.non_polymorphic()`` queryset member function added. This is preferable to
    using ``.base_objects...``, as it just makes the resulting queryset non-polymorphic
    and does not change anything else in the behaviour of the manager used (while
    ``.base_objects`` is just a different manager).

*   ``.get_real_instances()`` has been elevated to an official part of the API.
    It allows you to turn a queryset or list of base objects into a list of the real instances.
    This is useful if e.g. you use ``ModelA.objects.non_polymorphic().extra(...)`` and then want to
    transform the result to its polymorphic equivalent:

    >>> qs = ModelA.objects.all().non_polymorphic()
    >>> real_objects = qs.get_real_instances()

    is equivalent to:

    >>> real_objects = ModelA.objects.all()

    Instead of ``qs.get_real_instances()``, ``ModelA.objects.get_real_instances(qs)`` may be used
    as well. In the latter case, ``qs`` may be any list of objects of type ModelA.

*   ``translate_polymorphic_Q_object``  (see DOCS)


February 22 2010, Installation Note
-------------------------------------------------------------------

The django_polymorphic source code has been restructured
and as a result needs to be installed like a normal Django App
- either via copying the "polymorphic" directory into your
Django project or by running setup.py. Adding 'polymorphic'
to INSTALLED_APPS in settings.py is still optional, however.

The file `polymorphic.py` cannot be used as a standalone
extension module anymore (as is has been split into a number
of smaller files).

Importing works slightly different now: All relevant symbols are
imported directly from 'polymorphic' instead from
'polymorphic.models'::

    # new way
    from polymorphic import PolymorphicModel, ...

    # old way, doesn't work anymore
    from polymorphic.models import PolymorphicModel, ...


January 26 2010: Database Schema Change
-------------------------------------------------------------------

The update from January 26 changed the database schema (more info in the commit-log_).
Sorry for any inconvenience. But this should be the final DB schema now.

.. _commit-log: http://github.com/bconstantin/django_polymorphic/commit/c2b420aea06637966a208329ef7ec853889fa4c7

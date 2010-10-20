Polymorphic Models for Django
=============================

.

Quick Start, Docs, Contributing
-------------------------------

* `What is django_polymorphic good for?`_
* `Quickstart`_, or the complete `Installation and Usage Docs`_
* `Release Notes, News and Discussion`_ (Google Group) or Changelog_
* Download from GitHub_ or Bitbucket_, or as TGZ_ or ZIP_
* Improve django_polymorphic, report issues, participate, discuss, patch or fork (GitHub_, Bitbucket_, Group_, Mail_)

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

If you work with Django's model inheritance, django_polymorphic might
save you from implementing unpleasant workarounds that make your code
messy, error-prone, and slow. Model inheritance becomes much more "pythonic"
and now just works as you as a Python programmer expect.

It's best to Look at an Example
-------------------------------

Let's assume the models ``ArtProject`` and ``ResearchProject`` are derived
from the model ``Project``, and let's store one of each into the database:

>>> Project.objects.create(topic="John's Gathering")
>>> ArtProject.objects.create(topic="Sculpting with Tim", artist="T. Turner")
>>> ResearchProject.objects.create(topic="Swallow Aerodynamics", supervisor="Dr. Winter")

If we want to retrieve all our projects, we do:

>>> Project.objects.all()

Using django_polymorphic, we simply get what we stored::

    [ <Project:         id 1, topic: "John's Gathering">,
      <ArtProject:      id 2, topic: "Sculpting with Tim", artist: "T. Turner">,
      <ResearchProject: id 3, topic: "Swallow Aerodynamics", supervisor: "Dr. Winter"> ]

Using vanilla Django, we get incomplete objects, which is probably not what we wanted::

    [ <Project: id 1, topic: "John's Gathering">,
      <Project: id 2, topic: "Sculpting with Tim">,
      <Project: id 3, topic: "Swallow Aerodynamics"> ]

It's very similar for ForeignKeys, ManyToManyFields or OneToOneFields.

In general, the effect of django_polymorphic is twofold:

On one hand it makes sure that model inheritance just works
as you expect, by simply ensuring that you always get back exactly the same
objects from the database you stored there - regardless how you access them.
This can save you a lot of unpleasant workarounds.

On the other hand, together with only few small API additions to the Django ORM,
django_polymorphic enables a much more expressive and intuitive
programming style and also very advanced object oriented
designs that are not possible with vanilla Django.

Fortunately, most of the heavy duty machinery that is needed for this
functionality is already present in the original Django database layer.
Django_polymorphic merely adds a rather thin layer above that, which is
all that is required to make real OO fully automatic and very easy to use,
with only minimal additions to Django's API.

For more information, please look at `Quickstart`_ or the complete
`Installation and Usage Docs`_. Please also see the `restrictions and caveats`_.

.. _restrictions and caveats: http://bserve.webhop.org/django_polymorphic/DOCS.html#restrictions


This is a V1.0 Beta/Testing Release
-----------------------------------

This release is mostly a cleanup and maintenance release that also
improves a number of minor things and fixes one (non-critical) bug.

Some pending API changes and corrections have been folded into this release
in order to make the upcoming V1.0 API as stable as possible.

This release is also about getting feedback from you in case you don't
approve of any of these changes or would like to get additional
API fixes into V1.0.

The release contains a considerable amount of changes in some of the more
critical parts of the software. It's intended for testing and development
environments and not for production environments. For these, it's best to
wait a few weeks for the proper V1.0 release, to allow some time for any
potential problems to turn up (if they exist).

If you encounter any problems please post them in the `discussion group`_
or open an issue on GitHub_ or BitBucket_ (or send me an email).

.. _discussion group: http://groups.google.de/group/django-polymorphic/topics


License
=======

Django_polymorphic uses the same license as Django (BSD-like).


API Changes
===========

October 18 2010
-------------------------------------------------------------------

polymorphic_dumpdata
++++++++++++++++++++

The polymorphic_dumpdata management command is not needed anymore
and has been removed, as the regular Django dumpdata command now automatically
works correctly with polymorphic models (for all supported versions of Django).

Output of Queryset or Object Printing
+++++++++++++++++++++++++++++++++++++

In order to improve compatibility with vanilla Django, printing quersets does not use
django_polymorphic's pretty printing by default anymore.
To get the old behaviour when printing querysets, you need to replace your model definition:

>>> class Project(PolymorphicModel):

by:

>>> class Project(PolymorphicModel, ShowFieldType):

The mixin classes for pretty output have been renamed:

    ``ShowFieldTypes, ShowFields, ShowFieldsAndTypes``

are now:

    ``ShowFieldType, ShowFieldContent and ShowFieldTypeAndContent``

(the old ones still exist for compatibility)

Running the Test suite with Django 1.3
++++++++++++++++++++++++++++++++++++++

Django 1.3 requires ``python manage.py test polymorphic`` instead of
just ``python manage.py test``.


February 22 2010, Installation Note
-----------------------------------

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
-----------------------------------------

| The update from January 26 changed the database schema (more info in the commit-log_).
| Sorry for any inconvenience. But this should be the final DB schema now.

.. _commit-log: http://github.com/bconstantin/django_polymorphic/commit/c2b420aea06637966a208329ef7ec853889fa4c7

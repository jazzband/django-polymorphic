Release Notes, Usage, Code
--------------------------

* Please see `here for release notes, news and discussion`_ (Google Group)
* `Many Examples`_, or full `Installation and Usage Docs`_ (or the short `Overview`_)   
* Download from GitHub_ or Bitbucket_, or as TGZ_ or ZIP_
* Improve django_polymorphic: Report issues, discuss, post patch, or fork the code (GitHub_, Bitbucket_, Newsgroup_, Mail_) 

.. _here for release notes, news and discussion: http://groups.google.de/group/django-polymorphic/topics
.. _Newsgroup: http://groups.google.de/group/django-polymorphic/topics
.. _Mail: http://github.com/bconstantin/django_polymorphic/tree/master/setup.py
.. _Installation and Usage Docs: http://bserve.webhop.org/wiki/django_polymorphic/doc
.. _Many Examples: http://bserve.webhop.org/wiki/django_polymorphic/doc#defining-polymorphic-models
.. _GitHub: http://github.com/bconstantin/django_polymorphic
.. _Bitbucket: http://bitbucket.org/bconstantin/django_polymorphic
.. _TGZ: http://github.com/bconstantin/django_polymorphic/tarball/master
.. _ZIP: http://github.com/bconstantin/django_polymorphic/zipball/master
.. _Overview: http://bserve.webhop.org/wiki/django_polymorphic


What is django_polymorphic good for?
------------------------------------

**Example**: If we define the model ``Project`` as the base class for
our models ``ArtProject`` and ``ResearchProject``, and we store one of
each into the database, then we can do::

	>>> Project.objects.all()
	.
	[ <Project:         id 1, topic: "John's Gathering">,
	  <ArtProject:      id 2, topic: "Sculpting with Tim", artist: "T. Turner">,
	  <ResearchProject: id 3, topic: "Swallow Aerodynamics", supervisor: "Dr. Winter"> ]

In general: django_polymorphic implements seamless polymorphic inheritance for Django models.

The effect: objects are always returned back from the database just
as you created them, with the same type/class and fields.

It doesn't matter how these objects are retrieved: be it through the
model's own managers/querysets, ForeignKeys, ManyToManyFields
or OneToOneFields.

As seen in this example, the resulting querysets are polymorphic,
and will typically deliver objects of several different types in
a single query result.

django_polymorphic does this only for models that explicitely enable it
(and for their submodels).

Please see the `Documentation and Examples`_ for more information
or directly look at `more Examples`_. 

.. _Documentation and Examples: http://bserve.webhop.org/wiki/django_polymorphic/doc
.. _more Examples: http://bserve.webhop.org/wiki/django_polymorphic/doc#defining-polymorphic-models

Status
------

It's important to consider that this code is very new and
to some extent still experimental. Please see the docs for
current restrictions, caveats, and performance implications.

It does seem to work very well for a number of people, but
API changes, code reorganisations or further schema changes
are still a possibility. There may also remain larger bugs
and problems in the code that have not yet been found.


License
-------

django_polymorphic uses the same license as Django (BSD-like).


Database Schema Change on January 26
------------------------------------

| The update from January 26 changed the database schema (more info in the commit-log_).
| Sorry for any inconvenience. But this should be the final DB schema now.

.. _commit-log: http://github.com/bconstantin/django_polymorphic/commit/c2b420aea06637966a208329ef7ec853889fa4c7

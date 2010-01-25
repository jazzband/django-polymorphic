===============================
Fully Polymorphic Django Models
===============================

News
----

* 	2010-1-26: IMPORTANT - database schema change (more info in change log).
	I hope I got this change in early enough before anyone started to use
	polymorphic.py in earnest. Sorry for any inconvenience.
	This should be the final DB schema now!


What is django_polymorphic good for?
------------------------------------

If ``ArtProject`` and ``ResearchProject`` inherit from the model ``Project``::

    >>> Project.objects.all()
	.
	[ <Project:         id 1, topic: "John's Gathering">,
	  <ArtProject:      id 2, topic: "Sculpting with Tim", artist: "T. Turner">,
	  <ResearchProject: id 3, topic: "Swallow Aerodynamics", supervisor: "Dr. Winter"> ]

In general, objects retrieved from the database are always delivered just as
they were created and saved, with the same type/class and fields. It doesn't
matter how you access these objects: be it through the model's own
managers/querysets, ForeignKey, ManyToMany or OneToOne fields.

The resulting querysets are polymorphic, and may deliver
objects of several different types in a single query result.

``django_polymorphic`` consists of just one add-on module, ``polymorphic.py``,
that adds this kind of automatic polymorphism to Django's model
inheritance system (for models that request this behaviour).

Please see additional examples and the documentation here:

	http://bserve.webhop.org/wiki/django_polymorphic

or in the DOCS.rst file in this repository.

Status
------

This module is still very experimental. Please see the docs for current restrictions,
caveats, and performance implications.

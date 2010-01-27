**2010-1-26**
	IMPORTANT - database schema change (more info in change log).
	I hope I got this change in early enough before anyone started to use
	polymorphic.py in earnest. Sorry for any inconvenience.
	This should be the final DB schema now.


Usage, Examples, Installation & Documentation, Links
----------------------------------------------------

* Documentation_ and Overview_  
* `Discussion, Questions, Suggestions`_
* GitHub_ - Bitbucket_ - `Download as TGZ`_ or ZIP_ 

.. _Documentation: http://bserve.webhop.org/wiki/django_polymorphic/doc 
.. _Discussion, Questions, Suggestions: http://django-polymorphic.blogspot.com/2010/01/messages.html
.. _GitHub: http://github.com/bconstantin/django_polymorphic
.. _Bitbucket: http://bitbucket.org/bconstantin/django_polymorphic
.. _Download as TGZ: http://github.com/bconstantin/django_polymorphic/tarball/master
.. _ZIP: http://github.com/bconstantin/django_polymorphic/zipball/master
.. _Overview: http://bserve.webhop.org/wiki/django_polymorphic


What is django_polymorphic good for?
------------------------------------

If ``ArtProject`` and ``ResearchProject`` inherit from the model ``Project``:

>>> Project.objects.all()
.
[ <Project:         id 1, topic: "John's Gathering">,
  <ArtProject:      id 2, topic: "Sculpting with Tim", artist: "T. Turner">,
  <ResearchProject: id 3, topic: "Swallow Aerodynamics", supervisor: "Dr. Winter"> ]

In general, objects retrieved from the database are always returned back 
with the same type/class and fields they were created and saved with.
It doesn't matter how these objects are retrieved: be it through the
model's own managers/querysets, ForeignKeys, ManyToManyFields
or OneToOneFields.

The resulting querysets are polymorphic, i.e they may deliver
objects of several different types in a single query result.

``django_polymorphic`` consists of just one add-on module, ``polymorphic.py``,
that adds this functionality to Django's model inheritance system
(for models that request this behaviour).


Status
------

This module is still very experimental. Please see the docs for current restrictions,
caveats, and performance implications.



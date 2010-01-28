**2010-1-26**
	IMPORTANT - database schema change (more info in change log).
	I hope I got this change in early enough before anyone started to use
	polymorphic.py in earnest. Sorry for any inconvenience.
	This should be the final DB schema now.


Usage, Examples, Installation & Documentation, Links
----------------------------------------------------

* Please see the `Documentation and Examples`_ (or the short `Overview`_)  
* If you have comments or suggestions: `Discussion, Comments, Suggestions`_
* The code can be found on GitHub_ and Bitbucket_, or downloaded as TGZ_ or ZIP_ 

.. _Documentation and Examples: http://bserve.webhop.org/wiki/django_polymorphic/doc 
.. _Discussion, Questions, Suggestions: http://django-polymorphic.blogspot.com/2010/01/messages.html
.. _GitHub: http://github.com/bconstantin/django_polymorphic
.. _Bitbucket: http://bitbucket.org/bconstantin/django_polymorphic
.. _TGZ: http://github.com/bconstantin/django_polymorphic/tarball/master
.. _ZIP: http://github.com/bconstantin/django_polymorphic/zipball/master
.. _Overview: http://bserve.webhop.org/wiki/django_polymorphic


What is django_polymorphic good for?
------------------------------------

It causes objects being retrieved from the database to always be returned back 
with the same type/class and fields they were created and saved with.

Example:
If ``ArtProject`` and ``ResearchProject`` inherit from the model ``Project``,
and we have saved one of each into the database::

	>>> Project.objects.all()
	.
	[ <Project:         id 1, topic: "John's Gathering">,
	  <ArtProject:      id 2, topic: "Sculpting with Tim", artist: "T. Turner">,
	  <ResearchProject: id 3, topic: "Swallow Aerodynamics", supervisor: "Dr. Winter"> ]
	
It doesn't matter how these objects are retrieved: be it through the
model's own managers/querysets, ForeignKeys, ManyToManyFields
or OneToOneFields.

``django_polymorphic`` does this only for models that explicitly request this behaviour.

The resulting querysets are polymorphic, i.e they may deliver
objects of several different types in a single query result.


Status
------

It's important to consider that this code is still very new and
experimental. Please see the docs for current restrictions, caveats,
and performance implications.

Right now it's suitable only for the more enterprising early adopters.

It does seem to work well for a number of people (including me), but
it's still very early and API changes, code reorganisations or further
schema changes are still a possibility.


News
----

**2010-1-29:**

	Restructured django_polymorphic into a regular Django add-on
	application. This is needed for the management commands, and
	also seems to be a generally good idea for future enhancements
	as well (and it makes sure the tests are always included).

	The ``poly`` app - until now being used for test purposes only
	- has been renamed to ``polymorphic``. See DOCS.rst
	("installation/testing") for more info. 

**2010-1-26:**

	IMPORTANT - database schema change (more info in change log).
	I hope I got this change in early enough before anyone started to use
	polymorphic.py in earnest. Sorry for any inconvenience.
	This should be the final DB schema now.

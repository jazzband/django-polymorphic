Welcome to django-polymorphic's documentation!
==============================================

Django-polymorphic builds on top of the standard Django model inheritance.
It makes using inherited models easier. When a query is made at the base model,
the inherited model classes are returned.

When we store models that inherit from a ``Project`` model...

.. code-block:: python

    >>> Project.objects.create(topic="Department Party")
    >>> ArtProject.objects.create(topic="Painting with Tim", artist="T. Turner")
    >>> ResearchProject.objects.create(topic="Swallow Aerodynamics", supervisor="Dr. Winter")

...and want to retrieve all our projects, the subclassed models are returned!

.. code-block:: python

    >>> Project.objects.all()
    [ <Project:         id 1, topic "Department Party">,
      <ArtProject:      id 2, topic "Painting with Tim", artist "T. Turner">,
      <ResearchProject: id 3, topic "Swallow Aerodynamics", supervisor "Dr. Winter"> ]

Using vanilla Django, we get the base class objects, which is rarely what we wanted:

.. code-block:: python

    >>> Project.objects.all()
    [ <Project: id 1, topic "Department Party">,
      <Project: id 2, topic "Painting with Tim">,
      <Project: id 3, topic "Swallow Aerodynamics"> ]

Features
--------

* Full admin integration.
* ORM integration:

 * Support for ForeignKey, ManyToManyField, OneToOneField descriptors.
 * Support for proxy models.
 * Filtering/ordering of inherited models (``ArtProject___artist``).
 * Filtering model types: ``instance_of(...)`` and ``not_instance_of(...)``
 * Combining querysets of different models (``qs3 = qs1 | qs2``)
 * Support for custom user-defined managers.

* Formset support.
* Uses the minimum amount of queries needed to fetch the inherited models.
* Disabling polymorphic behavior when needed.


Getting started
---------------

.. toctree::
   :maxdepth: 2

   quickstart
   admin
   performance
   third-party

Advanced topics
---------------

.. toctree::
   :maxdepth: 2

   formsets
   migrating
   managers
   advanced
   changelog
   contributing
   api/index


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`


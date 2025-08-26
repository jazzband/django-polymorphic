django-polymorphic
==================

.. image:: https://img.shields.io/badge/License-BSD-blue.svg
   :target: https://opensource.org/license/bsd-3-clause
   :alt: License: BSD

.. image:: https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json
   :target: https://github.com/astral-sh/ruff
   :alt: Ruff

.. image:: https://badge.fury.io/py/django-polymorphic.svg
   :target: https://pypi.python.org/pypi/django-polymorphic/
   :alt: PyPI version

.. image:: https://img.shields.io/pypi/pyversions/django-polymorphic.svg
   :target: https://pypi.python.org/pypi/django-polymorphic/
   :alt: PyPI pyversions

.. image:: https://img.shields.io/pypi/djversions/django-polymorphic.svg
   :target: https://pypi.org/project/django-polymorphic/
   :alt: PyPI Django versions

.. image:: https://img.shields.io/pypi/status/django-polymorphic.svg
   :target: https://pypi.python.org/pypi/django-polymorphic
   :alt: PyPI status

.. image:: https://readthedocs.org/projects/django-polymorphic/badge/?version=latest
   :target: http://django-polymorphic.readthedocs.io/?badge=latest/
   :alt: Documentation Status

.. image:: https://img.shields.io/codecov/c/github/jazzband/django-polymorphic/master.svg
   :target: https://codecov.io/github/jazzband/django-polymorphic?branch=master
   :alt: Code Coverage

.. image:: https://github.com/jazzband/django-polymorphic/actions/workflows/test.yml/badge.svg?branch=master
   :target: https://github.com/jazzband/django-polymorphic/actions/workflows/test.yml?query=branch:master
   :alt: Test Status

.. image:: https://github.com/jazzband/django-polymorphic/actions/workflows/lint.yml/badge.svg?branch=master
   :target: https://github.com/jazzband/django-polymorphic/actions/workflows/lint.yml?query=branch:master
   :alt: Lint Status

.. image:: https://img.shields.io/badge/Published%20on-Django%20Packages-0c3c26
   :target: https://djangopackages.org/packages/p/django-polymorphic/
   :alt: Published on Django Packages

.. image:: https://jazzband.co/static/img/badge.svg
   :target: https://jazzband.co/
   :alt: Jazzband


:pypi:`django-polymorphic` builds on top of the standard Django model inheritance.
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

  - Support for ForeignKey, ManyToManyField, OneToOneField descriptors.
  - Support for proxy models.
  - Filtering/ordering of inherited models (``ArtProject___artist``).
  - Filtering model types: :meth:`~polymorphic.managers.PolymorphicQuerySet.instance_of` and
    :meth:`~polymorphic.managers.PolymorphicQuerySet.not_instance_of`
  - Combining querysets of different models (``qs3 = qs1 | qs2``)
  - Support for custom user-defined managers.

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
   integrations

Advanced topics
---------------

.. toctree::
   :maxdepth: 2

   formsets
   migrating
   managers
   advanced
   changelog
   api/index


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

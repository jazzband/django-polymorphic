Quickstart
===========

Install the project using::

    pip install django-polymorphic

Update the settings file:

.. code-block:: python

    INSTALLED_APPS += (
        'polymorphic',
        'django.contrib.contenttypes',
    )

The current release of :pypi:`django-polymorphic` supports:

.. image:: https://badge.fury.io/py/django-polymorphic.svg
   :target: https://pypi.python.org/pypi/django-polymorphic/
   :alt: PyPI version

.. image:: https://img.shields.io/pypi/pyversions/django-polymorphic.svg
   :target: https://pypi.python.org/pypi/django-polymorphic/
   :alt: Supported Pythons

.. image:: https://img.shields.io/pypi/djversions/django-polymorphic.svg
   :target: https://pypi.org/project/django-polymorphic/
   :alt: Supported Django


Making Your Models Polymorphic
------------------------------

Use :class:`~polymorphic.models.PolymorphicModel` instead of Django's
:class:`~django.db.models.Model`, like so:

.. code-block:: python

    from polymorphic.models import PolymorphicModel

    class Project(PolymorphicModel):
        topic = models.CharField(max_length=30)

    class ArtProject(Project):
        artist = models.CharField(max_length=30)

    class ResearchProject(Project):
        supervisor = models.CharField(max_length=30)

All models inheriting from your polymorphic models will be polymorphic as well.

Using Polymorphic Models
------------------------

Create some objects:

.. code-block:: python

    >>> Project.objects.create(topic="Department Party")
    >>> ArtProject.objects.create(topic="Painting with Tim", artist="T. Turner")
    >>> ResearchProject.objects.create(topic="Swallow Aerodynamics", supervisor="Dr. Winter")

Get polymorphic query results:

.. code-block:: python

    >>> Project.objects.all()
    [ <Project:         id 1, topic "Department Party">,
      <ArtProject:      id 2, topic "Painting with Tim", artist "T. Turner">,
      <ResearchProject: id 3, topic "Swallow Aerodynamics", supervisor "Dr. Winter"> ]

Use :meth:`~polymorphic.managers.PolymorphicQuerySet.instance_of` and
:meth:`~polymorphic.managers.PolymorphicQuerySet.not_instance_of` for narrowing the result to
specific subtypes:

.. code-block:: python

    >>> Project.objects.instance_of(ArtProject)
    [ <ArtProject:      id 2, topic "Painting with Tim", artist "T. Turner"> ]

.. code-block:: python

    >>> Project.objects.instance_of(ArtProject) | Project.objects.instance_of(ResearchProject)
    [ <ArtProject:      id 2, topic "Painting with Tim", artist "T. Turner">,
      <ResearchProject: id 3, topic "Swallow Aerodynamics", supervisor "Dr. Winter"> ]

Polymorphic filtering: Get all projects where Mr. Turner is involved as an artist
or supervisor (note the three underscores):

.. code-block:: python

    >>> Project.objects.filter(Q(ArtProject___artist='T. Turner') | Q(ResearchProject___supervisor='T. Turner'))
    [ <ArtProject:      id 2, topic "Painting with Tim", artist "T. Turner">,
      <ResearchProject: id 4, topic "Color Use in Late Cubism", supervisor "T. Turner"> ]

This is basically all you need to know, as *django-polymorphic* mostly
works fully automatic and just delivers the expected results.

.. note::
    While :pypi:`django-polymorphic` makes subclassed models easy to use in Django,
    we still encourage to use them with caution. Each subclassed model will require
    Django to perform an ``INNER JOIN`` to fetch the model fields from the database.
    While taking this in mind, there are valid reasons for using subclassed models.
    That's what this library is designed for!

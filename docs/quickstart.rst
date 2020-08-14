Quickstart
===========

Install the project using::

    pip install django-polymorphic

Update the settings file::

    INSTALLED_APPS += (
        'polymorphic',
        'django.contrib.contenttypes',
    )

The current release of *django-polymorphic* supports Django 1.11, 2.0, 2.1, 2.2 and Python 2.7 and 3.5+ is supported.
For older Django versions, use *django-polymorphic==1.3*.

Making Your Models Polymorphic
------------------------------

Use ``PolymorphicModel`` instead of Django's ``models.Model``, like so::

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

>>> Project.objects.create(topic="Department Party")
>>> ArtProject.objects.create(topic="Painting with Tim", artist="T. Turner")
>>> ResearchProject.objects.create(topic="Swallow Aerodynamics", supervisor="Dr. Winter")

Get polymorphic query results:

>>> Project.objects.all()
[ <Project:         id 1, topic "Department Party">,
  <ArtProject:      id 2, topic "Painting with Tim", artist "T. Turner">,
  <ResearchProject: id 3, topic "Swallow Aerodynamics", supervisor "Dr. Winter"> ]

Use ``instance_of`` or ``not_instance_of`` for narrowing the result to specific subtypes:

>>> Project.objects.instance_of(ArtProject)
[ <ArtProject:      id 2, topic "Painting with Tim", artist "T. Turner"> ]

>>> Project.objects.instance_of(ArtProject) | Project.objects.instance_of(ResearchProject)
[ <ArtProject:      id 2, topic "Painting with Tim", artist "T. Turner">,
  <ResearchProject: id 3, topic "Swallow Aerodynamics", supervisor "Dr. Winter"> ]

Polymorphic filtering: Get all projects where Mr. Turner is involved as an artist
or supervisor (note the three underscores):

>>> Project.objects.filter(Q(ArtProject___artist='T. Turner') | Q(ResearchProject___supervisor='T. Turner'))
[ <ArtProject:      id 2, topic "Painting with Tim", artist "T. Turner">,
  <ResearchProject: id 4, topic "Color Use in Late Cubism", supervisor "T. Turner"> ]

This is basically all you need to know, as *django-polymorphic* mostly
works fully automatic and just delivers the expected results.

Note: When using the ``dumpdata`` management command on polymorphic tables
(or any table that has a reference to :class:`~django.contrib.contenttypes.models.ContentType`),
include the ``--natural`` flag in the arguments. This makes sure the
:class:`~django.contrib.contenttypes.models.ContentType` models will be referenced by name
instead of their primary key as that changes between Django instances.


.. note::
    While *django-polymorphic* makes subclassed models easy to use in Django,
    we still encourage to use them with caution. Each subclassed model will require
    Django to perform an ``INNER JOIN`` to fetch the model fields from the database.
    While taking this in mind, there are valid reasons for using subclassed models.
    That's what this library is designed for!

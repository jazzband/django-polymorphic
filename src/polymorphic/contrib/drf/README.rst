.. image:: https://travis-ci.org/apirobot/django-rest-polymorphic.svg?branch=master
    :target: https://travis-ci.org/apirobot/django-rest-polymorphic

.. image:: https://codecov.io/gh/apirobot/django-rest-polymorphic/branch/master/graph/badge.svg
    :target: https://codecov.io/gh/apirobot/django-rest-polymorphic

.. image:: https://badge.fury.io/py/django-rest-polymorphic.svg
    :target: https://badge.fury.io/py/django-rest-polymorphic


=======================
Django REST Polymorphic
=======================

Polymorphic serializers for Django REST Framework.


Overview
--------

``django-rest-polymorphic`` allows you to easily define serializers for your inherited models that you have created using ``django-polymorphic`` library.


Installation
------------

Install using ``pip``:

.. code-block:: bash

    $ pip install django-rest-polymorphic


Usage
-----

Define your polymorphic models:

.. code-block:: python

    # models.py
    from django.db import models
    from polymorphic.models import PolymorphicModel


    class Project(PolymorphicModel):
        topic = models.CharField(max_length=30)


    class ArtProject(Project):
        artist = models.CharField(max_length=30)


    class ResearchProject(Project):
        supervisor = models.CharField(max_length=30)

Define serializers for each polymorphic model the way you did it when you used ``django-rest-framework``:

.. code-block:: python

    # serializers.py
    from rest_framework import serializers
    from .models import Project, ArtProject, ResearchProject


    class ProjectSerializer(serializers.ModelSerializer):
        class Meta:
            model = Project
            fields = ('topic', )


    class ArtProjectSerializer(serializers.ModelSerializer):
        class Meta:
            model = ArtProject
            fields = ('topic', 'artist')


    class ResearchProjectSerializer(serializers.ModelSerializer):
        class Meta:
            model = ResearchProject
            fields = ('topic', 'supervisor')

Then you have to create a polymorphic serializer that serves as a mapper between models and serializers which you have defined above:

.. code-block:: python

    # serializers.py
    from rest_polymorphic.serializers import PolymorphicSerializer


    class ProjectPolymorphicSerializer(PolymorphicSerializer):
        model_serializer_mapping = {
            Project: ProjectSerializer,
            ArtProject: ArtProjectSerializer,
            ResearchProject: ResearchProjectSerializer
        }

Create viewset with serializer_class equals to your polymorphic serializer:

.. code-block:: python

    # views.py
    from rest_framework import viewsets
    from .models import Project
    from .serializers import ProjectPolymorphicSerializer


    class ProjectViewSet(viewsets.ModelViewSet):
        queryset = Project.objects.all()
        serializer_class = ProjectPolymorphicSerializer

Test it:

.. code-block:: bash

    $ http GET "http://localhost:8000/projects/"

.. code-block:: http

    HTTP/1.0 200 OK
    Content-Length: 227
    Content-Type: application/json

    [
        {
            "resourcetype": "Project",
            "topic": "John's gathering"
        },
        {
            "artist": "T. Turner",
            "resourcetype": "ArtProject",
            "topic": "Sculpting with Tim"
        },
        {
            "resourcetype": "ResearchProject",
            "supervisor": "Dr. Winter",
            "topic": "Swallow Aerodynamics"
        }
    ]

.. code-block:: bash

    $ http POST "http://localhost:8000/projects/" resourcetype="ArtProject" topic="Guernica" artist="Picasso"

.. code-block:: http

    HTTP/1.0 201 Created
    Content-Length: 67
    Content-Type: application/json

    {
        "artist": "Picasso",
        "resourcetype": "ArtProject",
        "topic": "Guernica"
    }

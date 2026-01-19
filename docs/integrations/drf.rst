.. _django-rest-framework-support:

===================
djangorestframework
===================

Polymorphic serializers for `Django REST Framework <https://www.django-rest-framework.org/>`_.

The :pypi:`django-rest-polymorphic` package has been incorporated into :pypi:`django-polymorphic`.
This contrib package allows you to easily define serializers for your inherited models that you have
created using ``django-polymorphic`` library. To migrate from :pypi:`django-rest-polymorphic`, you
need to change your import paths from ``rest_polymorphic.serializers`` to
``polymorphic.contrib.drf.serializers``.

Usage
-----

Define your polymorphic models:

.. literalinclude:: ../../src/polymorphic/tests/examples/integrations/drf/models/example_models.py
    :language: python
    :linenos:


Define serializers for each polymorphic model the way you did it when you used
:pypi:`djangorestframework`:

.. literalinclude:: ../../src/polymorphic/tests/examples/integrations/drf/example_serializers.py
    :language: python
    :linenos:
    :lines: 1-26


Note that if you extend `HyperlinkedModelSerializer
<https://www.django-rest-framework.org/api-guide/serializers/#hyperlinkedmodelserializer>`_ instead
of `ModelSerializer <https://www.django-rest-framework.org/api-guide/serializers/#modelserializer>`_
you need to define `extra_kwargs
<https://www.django-rest-framework.org/community/3.0-announcement/#the-extra_kwargs-option>`_ to
direct the URL to the appropriate view for your polymorphic serializer.

Then you have to create a polymorphic serializer that serves as a mapper between models and
serializers which you have defined above:

.. literalinclude:: ../../src/polymorphic/tests/examples/integrations/drf/example_serializers.py
    :language: python
    :lines: 29-

Create viewset with serializer_class equals to your polymorphic serializer:

.. literalinclude:: ../../src/polymorphic/tests/examples/integrations/drf/views.py
    :language: python
    :linenos:

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
            "topic": "Sculpting with Tim",
            "url": "http://localhost:8000/projects/2/"
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
        "topic": "Guernica",
        "url": "http://localhost:8000/projects/4/"
    }


Customize resource type
-----------------------

As you can see from the example above, in order to specify the type of your polymorphic model, you need to send a request with resource type field. The value of resource type should be the name of the model.

If you want to change the resource type field name from ``resourcetype`` to something else, you should override ``resource_type_field_name`` attribute:

.. code-block:: python

    class ProjectPolymorphicSerializer(PolymorphicSerializer):
        resource_type_field_name = 'projecttype'
        ...

If you want to change the behavior of resource type, you should override ``to_resource_type`` method:

.. code-block:: python

    class ProjectPolymorphicSerializer(PolymorphicSerializer):
        ...

        def to_resource_type(self, model_or_instance):
            return model_or_instance._meta.object_name.lower()

Now, the request for creating new object will look like this:

.. code-block:: bash

    $ http POST "http://localhost:8000/projects/" projecttype="artproject" topic="Guernica" artist="Picasso"

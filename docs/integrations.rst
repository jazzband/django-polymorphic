.. _integrations:

Integrations
============

When integrating polymorphic models into third party apps you have three primary options:

0. Hope it just works (it might!).
1. Ensure the querysets the third party apps see are
   :meth:`not polymorphic <polymorphic.query.PolymorphicQuerySet.non_polymorphic>`.
2. Override or extend relevant third party app code to work with polymorphic querysets.

If it does not just work, option 1 is usually the easiest. We provide some integrations in
:mod:`polymorphic.contrib` for popular third party apps and provide guidance for others below.

This page does not exhaustively cover all integrations. If you feel your integration need is
very common you may consider opening a PR to either provide support in code or documentation here.

This page covers supported and tested integration advice. For all other integration advice please
refer to `our integrations discussion page
<https://github.com/jazzband/django-polymorphic/discussions/categories/integrations>`_.

For the integration examples on this page, we use the following polymorphic model hierarchy:

.. literalinclude:: ../src/polymorphic/tests/examples/integrations/models.py
    :language: python
    :linenos:

.. _django-django-guardian-support:

django-guardian
---------------

.. versionadded:: 1.0.2

You can configure :pypi:`django-guardian` to use the base model for object level permissions.
Add this option to your settings:

.. code-block:: python

    GUARDIAN_GET_CONTENT_TYPE = \
        'polymorphic.contrib.guardian.get_polymorphic_base_content_type'

This option requires :pypi:`django-guardian` >= 1.4.6. Details about how this option works are
available in the `django-guardian documentation
<https://django-guardian.readthedocs.io/en/stable/configuration>`_.


.. _django-rest-framework-support:

djangorestframework
-------------------

The :pypi:`django-rest-polymorphic` package provides polymorphic serializers that help you integrate
your polymorphic models with :pypi:`djangorestframework`.


Example
~~~~~~~

Define serializers:

.. code-block:: python

    from rest_framework import serializers
    from rest_polymorphic.serializers import PolymorphicSerializer
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


    class ProjectPolymorphicSerializer(PolymorphicSerializer):
        model_serializer_mapping = {
            Project: ProjectSerializer,
            ArtProject: ArtProjectSerializer,
            ResearchProject: ResearchProjectSerializer
        }

Create viewset with serializer_class equals to your polymorphic serializer:

.. code-block:: python

    from rest_framework import viewsets
    from .models import Project
    from .serializers import ProjectPolymorphicSerializer


    class ProjectViewSet(viewsets.ModelViewSet):
        queryset = Project.objects.all()
        serializer_class = ProjectPolymorphicSerializer


.. _django-extra-views-support:

django-extra-views
------------------

.. versionadded:: 1.1

The :mod:`polymorphic.contrib.extra_views` package provides classes to display polymorphic formsets
using the classes from :pypi:`django-extra-views`. See the documentation of:

* :class:`~polymorphic.contrib.extra_views.PolymorphicFormSetView`
* :class:`~polymorphic.contrib.extra_views.PolymorphicInlineFormSetView`
* :class:`~polymorphic.contrib.extra_views.PolymorphicInlineFormSet`

.. tip::

    The complete working code for this example can be found `in the extra_views integration test
    <https://github.com/jazzband/django-polymorphic/tree/HEAD/src/polymorphic/tests/examples/integrations/extra_views>`_.


Example View
~~~~~~~~~~~~

Here's how to create a view using :class:`~polymorphic.contrib.extra_views.PolymorphicFormSetView`
to handle polymorphic formsets:

.. literalinclude:: ../src/polymorphic/tests/examples/integrations/extra_views/views.py
    :language: python
    :linenos:


URL Configuration
~~~~~~~~~~~~~~~~~

Configure the URL patterns to route to your formset view:

.. literalinclude:: ../src/polymorphic/tests/examples/integrations/extra_views/urls.py
    :language: python
    :linenos:


Template
~~~~~~~~

The template for rendering the formset:

.. literalinclude:: ../src/polymorphic/tests/examples/integrations/extra_views/templates/extra_views/article_formset.html
    :language: html+django

``model_name`` is a template tag implemented like so:

.. literalinclude:: ../src/polymorphic/tests/examples/integrations/extra_views/templatetags/extra_views_tags.py
    :language: python
    :lines: 6-

.. _django-reversion-support:

django-reversion
----------------

Support for :pypi:`django-reversion` works as expected with polymorphic models. We just need to
do two things:

1. Inherit our admin classes from both :class:`~polymorphic.admin.PolymorphicParentModelAdmin` /
   :class:`~polymorphic.admin.PolymorphicChildModelAdmin` and
   :ref:`VersionAdmin <django-reversion:versionadmin>`.
2. Override the ``admin/polymorphic/object_history.html`` template.

.. tip::

    The complete working code for this example can be found `in the reversion integration test
    <https://github.com/jazzband/django-polymorphic/tree/HEAD/src/polymorphic/tests/examples/integrations/reversion>`_.


Admin Configuration
~~~~~~~~~~~~~~~~~~~

The admin configuration combines :class:`~polymorphic.admin.PolymorphicParentModelAdmin` and
:class:`~polymorphic.admin.PolymorphicChildModelAdmin` with
:ref:`VersionAdmin <django-reversion:versionadmin>`:

.. literalinclude:: ../src/polymorphic/tests/examples/integrations/reversion/admin.py
    :language: python
    :linenos:


Custom Template
~~~~~~~~~~~~~~~

Since both :class:`~polymorphic.admin.PolymorphicParentModelAdmin` and
:ref:`VersionAdmin <django-reversion:versionadmin>`. define ``object_history.html`` template, you
need to create a custom template that combines both:

.. literalinclude:: ../src/polymorphic/tests/examples/integrations/reversion/templates/admin/polymorphic/object_history.html
    :language: html+django

This makes sure both the reversion template is used, and the breadcrumb is corrected for the
polymorphic model using the :templatetag:`breadcrumb_scope`
tag.

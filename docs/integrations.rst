.. _integrations:

Integrations
============

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


.. _django-mptt-support:

django-mptt
-----------

Combining polymorphic with :pypi:`django-mptt` is certainly possible, but not straightforward.
It involves combining both managers, querysets, models, meta-classes and admin classes
using multiple inheritance.

The :pypi:`django-polymorphic-tree` package provides this out of the box.


.. _django-reversion-support:

django-reversion
----------------

Support for :pypi:`django-reversion` works as expected with polymorphic models.
However, they require more setup than standard models. That's become:

* Manually register the child models with :pypi:`django-reversion`, so their ``follow`` parameter
  can be set.
* Polymorphic models use :ref:`django:multi-table-inheritance`.
  See the :doc:`django-reversion:api` for how to deal with this by adding a ``follow`` field for the
  primary key.
* Both admin classes redefine ``object_history_template``.


Example
~~~~~~~

The admin :ref:`admin example <admin-example>` becomes:

.. code-block:: python

    from django.contrib import admin
    from polymorphic.admin import PolymorphicParentModelAdmin, PolymorphicChildModelAdmin
    from reversion.admin import VersionAdmin
    from reversion import revisions
    from .models import ModelA, ModelB, ModelC


    class ModelAChildAdmin(PolymorphicChildModelAdmin, VersionAdmin):
        base_model = ModelA  # optional, explicitly set here.
        base_form = ...
        base_fieldsets = (
            ...
        )

    class ModelBAdmin(ModelAChildAdmin, VersionAdmin):
        # define custom features here

    class ModelCAdmin(ModelBAdmin):
        # define custom features here


    class ModelAParentAdmin(VersionAdmin, PolymorphicParentModelAdmin):
        base_model = ModelA  # optional, explicitly set here.
        child_models = (
            (ModelB, ModelBAdmin),
            (ModelC, ModelCAdmin),
        )

    revisions.register(ModelB, follow=['modela_ptr'])
    revisions.register(ModelC, follow=['modelb_ptr'])
    admin.site.register(ModelA, ModelAParentAdmin)

Redefine a :file:`admin/polymorphic/object_history.html` template, so it combines both worlds:

.. code-block:: html+django

    {% extends 'reversion/object_history.html' %}
    {% load polymorphic_admin_tags %}

    {% block breadcrumbs %}
        {% breadcrumb_scope base_opts %}{{ block.super }}{% endbreadcrumb_scope %}
    {% endblock %}

This makes sure both the reversion template is used, and the breadcrumb is corrected for the
polymorphic model.

.. _django-reversion-compare-support:

django-reversion-compare
------------------------

The :pypi:`django-reversion-compare` views work as expected, the admin requires a little tweak.
In your parent admin, include the following method:

.. code-block:: python

    def compare_view(self, request, object_id, extra_context=None):
        """Redirect the reversion-compare view to the child admin."""
        real_admin = self._get_real_admin(object_id)
        return real_admin.compare_view(request, object_id, extra_context=extra_context)

As the compare view resolves the the parent admin, it uses it's base model to find revisions.
This doesn't work, since it needs to look for revisions of the child model. Using this tweak,
the view of the actual child model is used, similar to the way the regular change and delete views
are redirected.

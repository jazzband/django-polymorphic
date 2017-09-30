Third-party applications support
================================


django-guardian support
-----------------------

.. versionadded:: 1.0.2

You can configure django-guardian_ to use the base model for object level permissions.
Add this option to your settings:

.. code-block:: python

    GUARDIAN_GET_CONTENT_TYPE = 'polymorphic.contrib.guardian.get_polymorphic_base_content_type'

This option requires django-guardian_ >= 1.4.6. Details about how this option works are available in the
`django-guardian documentation <https://django-guardian.readthedocs.io/en/latest/configuration.html#guardian-get-content-type>`_.


django-extra-views
------------------

.. versionadded:: 1.1

The :mod:`polymorphic.contrib.extra_views` package provides classes to display polymorphic formsets
using the classes from django-extra-views_. See the documentation of:

* :class:`~polymorphic.contrib.extra_views.PolymorphicFormSetView`
* :class:`~polymorphic.contrib.extra_views.PolymorphicInlineFormSetView`
* :class:`~polymorphic.contrib.extra_views.PolymorphicInlineFormSet`


django-mptt support
-------------------

Combining polymorphic with django-mptt_ is certainly possible, but not straightforward.
It involves combining both managers, querysets, models, meta-classes and admin classes
using multiple inheritance.

The django-polymorphic-tree_ package provides this out of the box.


django-reversion support
------------------------

Support for django-reversion_ works as expected with polymorphic models.
However, they require more setup than standard models. That's become:

* Manually register the child models with django-reversion_, so their ``follow`` parameter can be set.
* Polymorphic models use `multi-table inheritance <https://docs.djangoproject.com/en/dev/topics/db/models/#multi-table-inheritance>`_.
  See the `reversion documentation <https://django-reversion.readthedocs.io/en/latest/api.html#multi-table-inheritance>`_
  how to deal with this by adding a ``follow`` field for the primary key.
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

This makes sure both the reversion template is used, and the breadcrumb is corrected for the polymorphic model.

.. _django-reversion-compare-support:

django-reversion-compare support
--------------------------------

The django-reversion-compare_ views work as expected, the admin requires a little tweak.
In your parent admin, include the following method:

.. code-block:: python

    def compare_view(self, request, object_id, extra_context=None):
        """Redirect the reversion-compare view to the child admin."""
        real_admin = self._get_real_admin(object_id)
        return real_admin.compare_view(request, object_id, extra_context=extra_context)

As the compare view resolves the the parent admin, it uses it's base model to find revisions.
This doesn't work, since it needs to look for revisions of the child model. Using this tweak,
the view of the actual child model is used, similar to the way the regular change and delete views are redirected.


.. _django-extra-views: https://github.com/AndrewIngram/django-extra-views
.. _django-guardian: https://github.com/django-guardian/django-guardian
.. _django-mptt: https://github.com/django-mptt/django-mptt
.. _django-polymorphic-tree: https://github.com/django-polymorphic/django-polymorphic-tree
.. _django-reversion-compare: https://github.com/jedie/django-reversion-compare
.. _django-reversion: https://github.com/etianen/django-reversion

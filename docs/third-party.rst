.. _third-party:

Third-party applications support
================================

Django-reversion
----------------

`Django-reversion <https://github.com/etianen/django-reversion>`_ works as
expected with polymorphic models.  However, they require more setup than
standard models.  We have to face these problems:

* The children models are not registered in the admin site.
  You will therefore need to manually register them to django-reversion.
* Polymorphic models use
  `multi-table inheritance <https://docs.djangoproject.com/en/dev/topics/db/models/#multi-table-inheritance>`_.
  The django-reversion wiki explains
  `how to deal with this <https://github.com/etianen/django-reversion/wiki/Low-level-API#multi-table-inheritance>`_.

.. warning::
   ``'polymorphic',`` must be before ``'reversion',`` in your
   ``INSTALLED_APPS`` setting, so that the django-reversion templates
   overridden by django-polymorphic will load first.


Example
.......

The :ref:`admin example <admin-example>` becomes:

.. code-block:: python

    from django.contrib import admin
    from polymorphic.admin import PolymorphicParentModelAdmin, PolymorphicChildModelAdmin
    import reversion
    from reversion import VersionAdmin
    from .models import ModelA, ModelB, ModelC


    class ModelAChildAdmin(PolymorphicChildModelAdmin):
        base_model = ModelA
        base_form = ...
        base_fieldsets = (
            ...
        )

    class ModelBAdmin(VersionAdmin, ModelAChildAdmin):
        # define custom features here

    class ModelCAdmin(ModelBAdmin):
        # define custom features here


    class ModelAParentAdmin(VersionAdmin, PolymorphicParentModelAdmin):
        base_model = ModelA
        child_models = (
            (ModelB, ModelBAdmin),
            (ModelC, ModelCAdmin),
        )

    reversion.register(ModelB, follow=['modela_ptr'])
    reversion.register(ModelC, follow=['modelb_ptr'])
    admin.site.register(ModelA, ModelAParentAdmin)

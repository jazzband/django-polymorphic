Django admin integration
========================

Off course, it's possible to register individual polymorphic models in the Django admin interface.
However, to use these models in a single cohesive interface, some extra base classes are available.

The polymorphic admin interface works in a simple way:

* The add screen gains an additional step where the desired child model is selected.
* The edit screen displays the admin interface of the child model.
* The list screen still displays all objects of the base class.

The polymorphic admin is implemented via a parent admin that forwards
the *edit* and *delete* views to the ``ModelAdmin`` of the derived child model.
The *list* page is still implemented by the parent model admin.


The parent model
----------------

The parent model admin needs to inherit ``PolymorphicParentModelAdmin``,
and implement the following:

* ``base_model`` should be set
* ``child_models`` or ``get_child_models()`` should return a list with Model tuple.

The exact implementation can depend on the way your module is structured.
For simple inheritance situations, ``child_models`` is the best solution.
For more complex cases, use ``get_child_models()``.


By default, the non_polymorphic() method will be called on the queryset, so
only the Parent model will be provided to the list template.  This is to avoid
the performance hit of retrieving child models.

This can be controlled by setting the ``polymorphic_list`` property on the
parent admin.  Setting it to True will provide child models to the list template.

The child models
----------------

The admin interface of the derived models should inherit from ``PolymorphicChildModelAdmin``.
Again, ``base_model`` should be set in this class as well.
This class implements the following features:

* It corrects the breadcrumbs in the admin pages.
* It extends the template lookup paths, to look for both the parent model and child model in the ``admin/app/model/change_form.html`` path.


PolymorphicChildModelFilter
---------------------------

This filter can be used to only display objects from the selected child model.
To do so, add it to ``list_filter``, as shown in the example below.


.. _admin-example:

Example
-------

The models are taken from :ref:`advanced-features`.

If you use other applications such as django-reversion, please check
:ref:`third-party`.

.. code-block:: python

    from django.contrib import admin
    from polymorphic.admin import (
        PolymorphicParentModelAdmin, PolymorphicChildModelAdmin,
        PolymorphicChildModelFilter)
    from .models import ModelA, ModelB, ModelC


    class ModelAAdmin(PolymorphicParentModelAdmin):
        """ The parent model admin """
        base_model = ModelA
        child_models = (ModelB, ModelC)
        list_filter = (PolymorphicChildModelFilter,)  # This is optional.
        # define features for the changelist here


    class ModelAChildAdmin(PolymorphicChildModelAdmin):
        """ Base admin class for all child models """
        base_model = ModelA
        # define common features between the child model admins here


    class ModelBAdmin(ModelAChildAdmin):
        # define custom features here


    class ModelCAdmin(ModelBAdmin):
        # define custom features here


    admin.site.register(ModelA, ModelAAdmin)
    admin.site.register(ModelB, ModelBAdmin)
    admin.site.register(ModelC, ModelCAdmin)

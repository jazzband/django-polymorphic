Django admin integration
========================

Off course, it's possible to register individual polymorphic models in the Django admin interface.
However, to use these models in a single cohesive interface, some extra base classes are available.

The polymorphic admin interface works in a simple way:

* The add screen gains an additional step where the desired child model is selected.
* The edit screen displays the admin interface of the child model.
* The list screen still displays all objects of the base class.

The polymorphic admin is implemented via a parent admin that forwards the *edit* and *delete* views
to the ``ModelAdmin`` of the derived child model. The *list* page is still implemented by the parent model admin.

Both the parent model and child model need to have a ``ModelAdmin`` class.
Only the ``ModelAdmin`` class of the parent/base model has to be registered in the Django admin site.

The parent model
----------------

The parent model needs to inherit ``PolymorphicParentModelAdmin``, and implement the following:

* ``base_model`` should be set
* ``child_models`` or ``get_child_models()`` should return a list with (Model, ModelAdmin) tuple.

The exact implementation can depend on the way your module is structured.
For simple inheritance situations, ``child_models`` is the best solution.
For large applications, ``get_child_models()`` can be used to query a plugin registration system.

The child models
----------------

The admin interface of the derived models should inherit from ``PolymorphicChildModelAdmin``.
Again, ``base_model`` should be set in this class as well.
This class implements the following features:

* It corrects the breadcrumbs in the admin pages.
* It extends the template lookup paths, to look for both the parent model and child model in the ``admin/app/model/change_form.html`` path.
* It allows to set ``base_form`` so the derived class will automatically include other fields in the form.
* It allows to set ``base_fieldsets`` so the derived class will automatically display any extra fields.

The standard ``ModelAdmin`` attributes ``form`` and ``fieldsets`` should rather be avoided at the base class,
because it will hide any additional fields which are defined in the derived model. Instead,
use the ``base_form`` and ``base_fieldsets`` instead. The ``PolymorphicChildModelAdmin`` will
automatically detect the additional fields that the child model has, display those in a separate fieldset.

PolymorphicChildModelFilter
---------------------------

This filter can be used to only display objects from the selected child model.
To do so, add it to ``list_filter``, as shown in the example below.


PolymorphicCompatibleBaseModelAdmin
-----------------------------------

If one of your model (let's say ``MyModel``) has a related field (ForeignKey,
ManyToManyField, OneToOneField or GenericForeignKey) to a polymorphic child
model, the ModelAdmin that has the related field must inherit
``PolymorphicCompatibleBaseModelAdmin``.

Like this:

.. code-block:: python

    from polymorphic.admin import PolymorphicCompatibleBaseModelAdmin

    class MyModelAdmin(PolymorphicCompatibleBaseModelAdmin, ModelAdmin):
        # …


.. _admin-example:

Example
-------

The models are taken from :ref:`advanced-features`.

.. code-block:: python

    from django.contrib import admin
    from polymorphic.admin import PolymorphicParentModelAdmin, PolymorphicChildModelAdmin
    from .models import ModelA, ModelB, ModelC


    class ModelAChildAdmin(PolymorphicChildModelAdmin):
        """ Base admin class for all child models """
        base_model = ModelA

        # By using these `base_...` attributes instead of the regular ModelAdmin `form` and `fieldsets`,
        # the additional fields of the child models are automatically added to the admin form.
        base_form = ...
        base_fieldsets = (
            ...
        )

    class ModelBAdmin(ModelAChildAdmin):
        # define custom features here

    class ModelCAdmin(ModelBAdmin):
        # define custom features here


    class ModelAParentAdmin(PolymorphicParentModelAdmin):
        """ The parent model admin """
        base_model = ModelA
        child_models = (
            (ModelB, ModelBAdmin),
            (ModelC, ModelCAdmin),
        )

    # Only the parent needs to be registered:
    admin.site.register(ModelA, ModelAParentAdmin)

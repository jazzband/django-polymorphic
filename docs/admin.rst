Django admin integration
========================

Of course, it's possible to register individual polymorphic models in the Django admin interface.
However, to use these models in a single cohesive interface, some extra base classes are available.

Setup
-----

Both the parent model and child model need to have a ``ModelAdmin`` class.

The shared base model should use the :class:`~polymorphic.admin.PolymorphicParentModelAdmin` as base class.

 * :attr:`~polymorphic.admin.PolymorphicParentModelAdmin.base_model` should be set
 * :attr:`~polymorphic.admin.PolymorphicParentModelAdmin.child_models` or
   :meth:`~polymorphic.admin.PolymorphicParentModelAdmin.get_child_models` should return an iterable of Model classes.

The admin class for every child model should inherit from :class:`~polymorphic.admin.PolymorphicChildModelAdmin`

 * :attr:`~polymorphic.admin.PolymorphicChildModelAdmin.base_model` should be set.

Although the child models are registered too, they won't be shown in the admin index page.
This only happens when :attr:`~polymorphic.admin.PolymorphicChildModelAdmin.show_in_index` is set to ``True``.

Fieldset configuration
~~~~~~~~~~~~~~~~~~~~~~

The parent admin is only used for the list display of models,
and for the edit/delete view of non-subclassed models.

All other model types are redirected to the edit/delete/history view of the child model admin.
Hence, the fieldset configuration should be placed on the child admin.

.. tip::
    When the child admin is used as base class for various derived classes, avoid using
    the standard ``ModelAdmin`` attributes ``form`` and ``fieldsets``.
    Instead, use the ``base_form`` and ``base_fieldsets`` attributes.
    This allows the :class:`~polymorphic.admin.PolymorphicChildModelAdmin` class
    to detect any additional fields in case the child model is overwritten.

.. versionchanged:: 1.0
    It's now needed to register the child model classes too.

    In *django-polymorphic* 0.9 and below, the ``child_models`` was a tuple of a ``(Model, ChildModelAdmin)``.
    The admin classes were registered in an internal class, and kept away from the main admin site.
    This caused various subtle problems with the ``ManyToManyField`` and related field wrappers,
    which are fixed by registering the child admin classes too. Note that they are hidden from
    the main view, unless :attr:`~polymorphic.admin.PolymorphicChildModelAdmin.show_in_index` is set.

.. _admin-example:

Example
-------

The models are taken from :ref:`advanced-features`.

.. code-block:: python

    from django.contrib import admin
    from polymorphic.admin import PolymorphicParentModelAdmin, PolymorphicChildModelAdmin, PolymorphicChildModelFilter
    from .models import ModelA, ModelB, ModelC, StandardModel


    class ModelAChildAdmin(PolymorphicChildModelAdmin):
        """ Base admin class for all child models """
        base_model = ModelA  # Optional, explicitly set here.

        # By using these `base_...` attributes instead of the regular ModelAdmin `form` and `fieldsets`,
        # the additional fields of the child models are automatically added to the admin form.
        base_form = ...
        base_fieldsets = (
            ...
        )


    @admin.register(ModelB)
    class ModelBAdmin(ModelAChildAdmin):
        base_model = ModelB  # Explicitly set here!
        # define custom features here


    @admin.register(ModelC)
    class ModelCAdmin(ModelBAdmin):
        base_model = ModelC  # Explicitly set here!
        show_in_index = True  # makes child model admin visible in main admin site
        # define custom features here


    @admin.register(ModelA)
    class ModelAParentAdmin(PolymorphicParentModelAdmin):
        """ The parent model admin """
        base_model = ModelA  # Optional, explicitly set here.
        child_models = (ModelB, ModelC)
        list_filter = (PolymorphicChildModelFilter,)  # This is optional.



Filtering child types
---------------------

Child model types can be filtered by adding a :class:`~polymorphic.admin.PolymorphicChildModelFilter`
to the ``list_filter`` attribute. See the example above.


Inline models
-------------

.. versionadded:: 1.0

Inline models are handled via a special :class:`~polymorphic.admin.StackedPolymorphicInline` class.

For models with a generic foreign key, there is a :class:`~polymorphic.admin.GenericStackedPolymorphicInline` class available.

When the inline is included to a normal :class:`~django.contrib.admin.ModelAdmin`,
make sure the :class:`~polymorphic.admin.PolymorphicInlineSupportMixin` is included.
This is not needed when the admin inherits from the
:class:`~polymorphic.admin.PolymorphicParentModelAdmin` /
:class:`~polymorphic.admin.PolymorphicChildModelAdmin` classes.

In the following example, the ``PaymentInline`` supports several types.
These are defined as separate inline classes.
The child classes can be nested for clarity, but this is not a requirement.

.. code-block:: python

    from django.contrib import admin

    from polymorphic.admin import PolymorphicInlineSupportMixin, StackedPolymorphicInline
    from .models import Order, Payment, CreditCardPayment, BankPayment, SepaPayment


    class PaymentInline(StackedPolymorphicInline):
        """
        An inline for a polymorphic model.
        The actual form appearance of each row is determined by
        the child inline that corresponds with the actual model type.
        """
        class CreditCardPaymentInline(StackedPolymorphicInline.Child):
            model = CreditCardPayment

        class BankPaymentInline(StackedPolymorphicInline.Child):
            model = BankPayment

        class SepaPaymentInline(StackedPolymorphicInline.Child):
            model = SepaPayment

        model = Payment
        child_inlines = (
            CreditCardPaymentInline,
            BankPaymentInline,
            SepaPaymentInline,
        )


    @admin.register(Order)
    class OrderAdmin(PolymorphicInlineSupportMixin, admin.ModelAdmin):
        """
        Admin for orders.
        The inline is polymorphic.
        To make sure the inlines are properly handled,
        the ``PolymorphicInlineSupportMixin`` is needed to
        """
        inlines = (PaymentInline,)




Using polymorphic models in standard inlines
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

To add a polymorphic child model as an Inline for another model, add a field to the inline's ``readonly_fields`` list
formed by the lowercased name of the polymorphic parent model with the string ``_ptr`` appended to it.
Otherwise, trying to save that model in the admin will raise an AttributeError with the message "can't set attribute".

.. code-block:: python

    from django.contrib import admin
    from .models import StandardModel


    class ModelBInline(admin.StackedInline):
        model = ModelB
        fk_name = 'modelb'
        readonly_fields = ['modela_ptr']


    @admin.register(StandardModel)
    class StandardModelAdmin(admin.ModelAdmin):
        inlines = [ModelBInline]



Internal details
----------------

The polymorphic admin interface works in a simple way:

* The add screen gains an additional step where the desired child model is selected.
* The edit screen displays the admin interface of the child model.
* The list screen still displays all objects of the base class.

The polymorphic admin is implemented via a parent admin that redirects the *edit* and *delete* views
to the ``ModelAdmin`` of the derived child model. The *list* page is still implemented by the parent model admin.

The parent model
~~~~~~~~~~~~~~~~

The parent model needs to inherit :class:`~polymorphic.admin.PolymorphicParentModelAdmin`, and implement the following:

 * :attr:`~polymorphic.admin.PolymorphicParentModelAdmin.base_model` should be set
 * :attr:`~polymorphic.admin.PolymorphicParentModelAdmin.child_models` or
   :meth:`~polymorphic.admin.PolymorphicParentModelAdmin.get_child_models` should return an iterable of Model classes.

The exact implementation can depend on the way your module is structured.
For simple inheritance situations, ``child_models`` is the best solution.
For large applications, ``get_child_models()`` can be used to query a plugin registration system.

By default, the non_polymorphic() method will be called on the queryset, so
only the Parent model will be provided to the list template.  This is to avoid
the performance hit of retrieving child models.

This can be controlled by setting the ``polymorphic_list`` property on the
parent admin.  Setting it to True will provide child models to the list template.

If you use other applications such as django-reversion_ or django-mptt_, please check +:ref:`third-party`.

Note: If you are using non-integer primary keys in your model, you have to edit ``pk_regex``,
for example ``pk_regex = '([\w-]+)'`` if you use UUIDs. Otherwise you cannot change model entries.

The child models
~~~~~~~~~~~~~~~~

The admin interface of the derived models should inherit from :class:`~polymorphic.admin.PolymorphicChildModelAdmin`.
Again, :attr:`~polymorphic.admin.PolymorphicChildModelAdmin.base_model` should be set in this class as well.
This class implements the following features:

* It corrects the breadcrumbs in the admin pages.
* It extends the template lookup paths, to look for both the parent model and child model in the ``admin/app/model/change_form.html`` path.
* It allows to set :attr:`~polymorphic.admin.PolymorphicChildModelAdmin.base_form` so the derived class will automatically include other fields in the form.
* It allows to set :attr:`~polymorphic.admin.PolymorphicChildModelAdmin.base_fieldsets` so the derived class will automatically display any extra fields.
* Although it must be registered with admin site, by default it's hidden from admin site index page.
  This can be overriden by adding :attr:`~polymorphic.admin.PolymorphicChildModelAdmin.show_in_index` = ``True`` in admin class.


.. _django-reversion: https://github.com/etianen/django-reversion
.. _django-mptt: https://github.com/django-mptt/django-mptt

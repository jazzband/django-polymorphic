"""
The ``extra_views.formsets`` provides a simple way to handle formsets.
The ``extra_views.advanced`` provides a method to combine that with a create/update form.

This package provides classes that support both options for polymorphic formsets.
"""
from __future__ import absolute_import
from django.core.exceptions import ImproperlyConfigured
import extra_views
from polymorphic.formsets import polymorphic_child_forms_factory, BasePolymorphicModelFormSet, BasePolymorphicInlineFormSet


__all__ = (
    'PolymorphicFormSetView',
    'PolymorphicInlineFormSetView',
    'PolymorphicInlineFormSet',
)


class PolymorphicFormSetMixin(object):
    """
    Internal Mixin, that provides polymorphic integration with the ``extra_views`` package.
    """

    formset_class = BasePolymorphicModelFormSet

    #: Default 0 extra forms
    extra = 0

    #: Define the children
    # :type: list[PolymorphicFormSetChild]
    formset_children = None

    def get_formset_children(self):
        """
        :rtype: list[PolymorphicFormSetChild]
        """
        if not self.formset_children:
            raise ImproperlyConfigured("Define 'formset_children' as list of `PolymorphicFormSetChild`")
        return self.formset_children

    def get_formset_child_kwargs(self):
        return {}

    def get_formset(self):
        """
        Returns the formset class from the inline formset factory
        """
        # Implementation detail:
        # Since `polymorphic_modelformset_factory` and `polymorphic_inlineformset_factory` mainly
        # reuse the standard factories, and then add `child_forms`, the same can be done here.
        # This makes sure the base class construction is completely honored.
        FormSet = super(PolymorphicFormSetMixin, self).get_formset()
        FormSet.child_forms = polymorphic_child_forms_factory(self.get_formset_children(), **self.get_formset_child_kwargs())
        return FormSet


class PolymorphicFormSetView(PolymorphicFormSetMixin, extra_views.ModelFormSetView):
    """
    A view that displays a single polymorphic formset.

    .. code-block:: python

        from polymorphic.formsets import PolymorphicFormSetChild


        class ItemsView(PolymorphicFormSetView):
            model = Item
            formset_children = [
                PolymorphicFormSetChild(ItemSubclass1),
                PolymorphicFormSetChild(ItemSubclass2),
            ]

    """
    formset_class = BasePolymorphicModelFormSet


class PolymorphicInlineFormSetView(PolymorphicFormSetMixin, extra_views.InlineFormSetView):
    """
    A view that displays a single polymorphic formset - with one parent object.
    This is a variation of the :mod:`extra_views` package classes for django-polymorphic.

    .. code-block:: python

        from polymorphic.formsets import PolymorphicFormSetChild


        class OrderItemsView(PolymorphicInlineFormSetView):
            model = Order
            inline_model = Item
            formset_children = [
                PolymorphicFormSetChild(ItemSubclass1),
                PolymorphicFormSetChild(ItemSubclass2),
            ]
    """
    formset_class = BasePolymorphicInlineFormSet


class PolymorphicInlineFormSet(PolymorphicFormSetMixin, extra_views.InlineFormSet):
    """
    An inline to add to the ``inlines`` of
    the :class:`~extra_views.advanced.CreateWithInlinesView`
    and :class:`~extra_views.advanced.UpdateWithInlinesView` class.

    .. code-block:: python

        from polymorphic.formsets import PolymorphicFormSetChild


        class ItemsInline(PolymorphicInlineFormSet):
            model = Item
            formset_children = [
                PolymorphicFormSetChild(ItemSubclass1),
                PolymorphicFormSetChild(ItemSubclass2),
            ]


        class OrderCreateView(CreateWithInlinesView):
            model = Order
            inlines = [ItemsInline]

            def get_success_url(self):
                return self.object.get_absolute_url()

    """
    formset_class = BasePolymorphicInlineFormSet

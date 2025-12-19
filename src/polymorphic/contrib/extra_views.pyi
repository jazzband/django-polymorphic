import extra_views
from _typeshed import Incomplete
from polymorphic.formsets import BasePolymorphicInlineFormSet, BasePolymorphicModelFormSet

__all__ = ['PolymorphicFormSetView', 'PolymorphicInlineFormSetView', 'PolymorphicInlineFormSet']

class PolymorphicFormSetMixin:
    formset_class = BasePolymorphicModelFormSet
    factory_kwargs: Incomplete
    formset_children: Incomplete
    def get_formset_children(self): ...
    def get_formset_child_kwargs(self): ...
    def get_formset(self): ...

class PolymorphicFormSetView(PolymorphicFormSetMixin, extra_views.ModelFormSetView):
    formset_class = BasePolymorphicModelFormSet

class PolymorphicInlineFormSetView(PolymorphicFormSetMixin, extra_views.InlineFormSetView):
    formset_class = BasePolymorphicInlineFormSet

class PolymorphicInlineFormSet(PolymorphicFormSetMixin, extra_views.InlineFormSetFactory):
    formset_class = BasePolymorphicInlineFormSet

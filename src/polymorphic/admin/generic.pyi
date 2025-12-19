from .inlines import PolymorphicInlineModelAdmin as PolymorphicInlineModelAdmin
from django.contrib.contenttypes.admin import GenericInlineModelAdmin
from django.utils.functional import cached_property as cached_property
from polymorphic.formsets import BaseGenericPolymorphicInlineFormSet as BaseGenericPolymorphicInlineFormSet, GenericPolymorphicFormSetChild as GenericPolymorphicFormSetChild, polymorphic_child_forms_factory as polymorphic_child_forms_factory

class GenericPolymorphicInlineModelAdmin(PolymorphicInlineModelAdmin, GenericInlineModelAdmin):
    formset = BaseGenericPolymorphicInlineFormSet
    def get_formset(self, request, obj=None, **kwargs): ...
    class Child(PolymorphicInlineModelAdmin.Child):
        formset_child = GenericPolymorphicFormSetChild
        ct_field: str
        ct_fk_field: str
        @cached_property
        def content_type(self): ...
        def get_formset_child(self, request, obj=None, **kwargs): ...

class GenericStackedPolymorphicInline(GenericPolymorphicInlineModelAdmin):
    template: str

from typing import Any

from django.contrib.contenttypes.admin import GenericInlineModelAdmin
from django.contrib.contenttypes.models import ContentType
from django.forms.models import BaseInlineFormSet
from django.utils.functional import cached_property as cached_property
from django_stubs_ext.http import HttpRequest

from polymorphic.formsets import (
    BaseGenericPolymorphicInlineFormSet as BaseGenericPolymorphicInlineFormSet,
)
from polymorphic.formsets import GenericPolymorphicFormSetChild as GenericPolymorphicFormSetChild
from polymorphic.formsets import polymorphic_child_forms_factory as polymorphic_child_forms_factory

from .inlines import PolymorphicInlineModelAdmin as PolymorphicInlineModelAdmin

class GenericPolymorphicInlineModelAdmin(PolymorphicInlineModelAdmin, GenericInlineModelAdmin):
    formset = BaseGenericPolymorphicInlineFormSet
    def get_formset(
        self, request: HttpRequest, obj: Any = None, **kwargs: Any
    ) -> type[BaseInlineFormSet]: ...
    class Child(PolymorphicInlineModelAdmin.Child):
        formset_child = GenericPolymorphicFormSetChild
        ct_field: str
        ct_fk_field: str
        @cached_property
        def content_type(self) -> ContentType: ...
        def get_formset_child(
            self, request: HttpRequest, obj: Any = None, **kwargs: Any
        ) -> GenericPolymorphicFormSetChild: ...

class GenericStackedPolymorphicInline(GenericPolymorphicInlineModelAdmin):
    template: str

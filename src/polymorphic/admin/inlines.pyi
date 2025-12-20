from typing import Any, Sequence

from django_stubs.contrib.admin.options import InlineModelAdmin
from django_stubs.db import models
from django_stubs.forms import Media
from django_stubs.forms.models import BaseInlineFormSet
from django_stubs.http import HttpRequest

from polymorphic.formsets import BasePolymorphicInlineFormSet as BasePolymorphicInlineFormSet
from polymorphic.formsets import PolymorphicFormSetChild as PolymorphicFormSetChild
from polymorphic.formsets import UnsupportedChildType as UnsupportedChildType
from polymorphic.formsets import polymorphic_child_forms_factory as polymorphic_child_forms_factory
from polymorphic.formsets.utils import add_media as add_media

from .helpers import PolymorphicInlineSupportMixin as PolymorphicInlineSupportMixin

class PolymorphicInlineModelAdmin(InlineModelAdmin[Any, Any]):
    formset: type[BaseInlineFormSet[Any, Any, Any]]
    polymorphic_media: Media
    extra: int
    child_inlines: Sequence[type[PolymorphicInlineModelAdmin.Child]]
    child_inline_instances: list[PolymorphicInlineModelAdmin.Child]
    def __init__(self, parent_model: type[models.Model], admin_site: Any) -> None: ...
    def get_child_inlines(self) -> Sequence[type[PolymorphicInlineModelAdmin.Child]]: ...
    def get_child_inline_instances(self) -> list[PolymorphicInlineModelAdmin.Child]: ...
    def get_child_inline_instance(
        self, model: type[models.Model]
    ) -> PolymorphicInlineModelAdmin.Child: ...
    def get_formset(
        self, request: HttpRequest, obj: Any = None, **kwargs: Any
    ) -> type[BaseInlineFormSet[Any, Any, Any]]: ...
    def get_formset_children(
        self, request: HttpRequest, obj: Any = None
    ) -> list[PolymorphicFormSetChild]: ...
    def get_fieldsets(self, request: HttpRequest, obj: Any = None) -> list[Any]: ...
    def get_fields(self, request: HttpRequest, obj: Any = None) -> Any: ...
    @property
    def media(self) -> Media: ...
    class Child(InlineModelAdmin[Any, Any]):
        formset_child = PolymorphicFormSetChild
        extra: int
        parent_inline: PolymorphicInlineModelAdmin
        def __init__(self, parent_inline: PolymorphicInlineModelAdmin) -> None: ...
        def get_formset(self, request: HttpRequest, obj: Any = None, **kwargs: Any) -> Any: ...
        def get_fields(self, request: HttpRequest, obj: Any = None) -> Any: ...
        def get_formset_child(
            self, request: HttpRequest, obj: Any = None, **kwargs: Any
        ) -> PolymorphicFormSetChild: ...

class StackedPolymorphicInline(PolymorphicInlineModelAdmin):
    template: str

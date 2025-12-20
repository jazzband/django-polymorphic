from _typeshed import Incomplete
from django_stubs.admin import ModelAdmin
from django_stubs.query import QuerySet
from django_stubs.http import HttpRequest
from typing import Any, ClassVar
from polymorphic.admin import (
    PolymorphicChildModelAdmin as PolymorphicChildModelAdmin,
    PolymorphicChildModelFilter as PolymorphicChildModelFilter,
    PolymorphicInlineSupportMixin as PolymorphicInlineSupportMixin,
    PolymorphicParentModelAdmin as PolymorphicParentModelAdmin,
    StackedPolymorphicInline as StackedPolymorphicInline,
)
from polymorphic.tests.models import (
    InlineModelA as InlineModelA,
    InlineModelB as InlineModelB,
    InlineParent as InlineParent,
    Model2A as Model2A,
    Model2B as Model2B,
    Model2C as Model2C,
    Model2D as Model2D,
    NoChildren as NoChildren,
    PlainA as PlainA,
)

class Model2Admin(PolymorphicParentModelAdmin):
    list_filter: ClassVar[Any]
    child_models: Any

class Model2DAdmin(PolymorphicChildModelAdmin):
    exclude: ClassVar[Any]

class PlainAAdmin(ModelAdmin):
    search_fields: Incomplete
    def get_queryset(self, request: HttpRequest) -> QuerySet: ...

class Inline(StackedPolymorphicInline):
    model = InlineModelA
    def get_child_inlines(self): ...
    class InlineModelAChild(StackedPolymorphicInline.Child):
        model = InlineModelA

    class InlineModelBChild(StackedPolymorphicInline.Child):
        model = InlineModelB
        autocomplete_fields: ClassVar[Any]

class InlineParentAdmin(PolymorphicInlineSupportMixin, ModelAdmin):
    inlines: ClassVar[Any]
    extra: int

class NoChildrenAdmin(PolymorphicParentModelAdmin):
    child_models: Incomplete

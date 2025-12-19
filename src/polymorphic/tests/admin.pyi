from _typeshed import Incomplete
from django.contrib.admin import ModelAdmin
from django.db.models.query import QuerySet
from django.http import HttpRequest
from polymorphic.admin import PolymorphicChildModelAdmin as PolymorphicChildModelAdmin, PolymorphicChildModelFilter as PolymorphicChildModelFilter, PolymorphicInlineSupportMixin as PolymorphicInlineSupportMixin, PolymorphicParentModelAdmin as PolymorphicParentModelAdmin, StackedPolymorphicInline as StackedPolymorphicInline
from polymorphic.tests.models import InlineModelA as InlineModelA, InlineModelB as InlineModelB, InlineParent as InlineParent, Model2A as Model2A, Model2B as Model2B, Model2C as Model2C, Model2D as Model2D, NoChildren as NoChildren, PlainA as PlainA

class Model2Admin(PolymorphicParentModelAdmin):
    list_filter: Incomplete
    child_models: Incomplete

class Model2DAdmin(PolymorphicChildModelAdmin):
    exclude: Incomplete

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
        autocomplete_fields: Incomplete

class InlineParentAdmin(PolymorphicInlineSupportMixin, ModelAdmin):
    inlines: Incomplete
    extra: int

class NoChildrenAdmin(PolymorphicParentModelAdmin):
    child_models: Incomplete

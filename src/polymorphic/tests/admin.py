from inspect import isclass
from django.contrib.admin import register, ModelAdmin, site as admin_site
from django.db.models.query import QuerySet
from django.http import HttpRequest
from polymorphic.admin import (
    StackedPolymorphicInline,
    PolymorphicInlineSupportMixin,
    PolymorphicChildModelAdmin,
    PolymorphicChildModelFilter,
    PolymorphicParentModelAdmin,
)

from polymorphic.tests.models import (
    PlainA,
    Model2A,
    Model2B,
    Model2C,
    Model2D,
    InlineModelA,
    InlineModelB,
    InlineParent,
    NoChildren,
)


@register(Model2A)
class Model2Admin(PolymorphicParentModelAdmin):
    list_filter = (PolymorphicChildModelFilter,)
    child_models = (Model2B, Model2C, Model2D)


admin_site.register(Model2B, PolymorphicChildModelAdmin)
admin_site.register(Model2C, PolymorphicChildModelAdmin)
admin_site.register(Model2D, PolymorphicChildModelAdmin)


@register(PlainA)
class PlainAAdmin(ModelAdmin):
    search_fields = ["field1"]

    def get_queryset(self, request: HttpRequest) -> QuerySet:
        return super().get_queryset(request).order_by("pk")


class Inline(StackedPolymorphicInline):
    model = InlineModelA

    def get_child_inlines(self):
        return [
            child
            for child in self.__class__.__dict__.values()
            if isclass(child) and issubclass(child, StackedPolymorphicInline.Child)
        ]

    class InlineModelAChild(StackedPolymorphicInline.Child):
        model = InlineModelA

    class InlineModelBChild(StackedPolymorphicInline.Child):
        model = InlineModelB
        autocomplete_fields = ["plain_a"]


@register(InlineParent)
class InlineParentAdmin(PolymorphicInlineSupportMixin, ModelAdmin):
    inlines = (Inline,)
    extra = 1


@register(NoChildren)
class NoChildrenAdmin(PolymorphicParentModelAdmin):
    child_models = ()

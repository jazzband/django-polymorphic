from django.contrib.admin import register, ModelAdmin, site as admin_site
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


class InlineModelAChild(StackedPolymorphicInline.Child):
    model = InlineModelA


class InlineModelBChild(StackedPolymorphicInline.Child):
    model = InlineModelB
    autocomplete_fields = ["plain_a"]


class Inline(StackedPolymorphicInline):
    model = InlineModelA
    child_inlines = (InlineModelAChild, InlineModelBChild)


@register(InlineParent)
class InlineParentAdmin(PolymorphicInlineSupportMixin, ModelAdmin):
    inlines = (Inline,)

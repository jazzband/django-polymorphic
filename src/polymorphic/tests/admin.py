from django.contrib.admin import register, ModelAdmin
from polymorphic.admin import StackedPolymorphicInline, PolymorphicInlineSupportMixin
from polymorphic.tests.models import PlainA, InlineModelA, InlineModelB, InlineParent


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

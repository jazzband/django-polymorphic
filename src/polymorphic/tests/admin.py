from inspect import isclass
from django.contrib.admin import register, ModelAdmin, TabularInline, site as admin_site
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
    ModelWithPolyFK,
    M2MAdminTest,
    M2MAdminTestChildA,
    M2MAdminTestChildB,
    M2MAdminTestChildC,
    M2MThroughBase,
    M2MThroughProject,
    M2MThroughPerson,
    M2MThroughMembership,
    M2MThroughMembershipWithPerson,
    M2MThroughMembershipWithSpecialPerson,
    M2MThroughProjectWithTeam,
    M2MThroughSpecialPerson,
    DirectM2MContainer,
)


@register(Model2A)
class Model2Admin(PolymorphicParentModelAdmin):
    list_filter = (PolymorphicChildModelFilter,)
    child_models = (Model2A, Model2B, Model2C, Model2D)


admin_site.register(Model2B, PolymorphicChildModelAdmin)
admin_site.register(Model2C, PolymorphicChildModelAdmin)


@register(Model2D)
class Model2DAdmin(PolymorphicChildModelAdmin):
    exclude = ("field3",)


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
    child_models = (NoChildren,)


@register(ModelWithPolyFK)
class ModelWithPolyFKAdmin(ModelAdmin):
    fields = ["name", "poly_fk"]


@register(M2MAdminTest)
class M2MAdminTestAdmin(PolymorphicParentModelAdmin):
    list_filter = (PolymorphicChildModelFilter,)
    child_models = (M2MAdminTestChildA, M2MAdminTestChildB, M2MAdminTestChildC)


@register(M2MAdminTestChildA)
class M2MAdminTestChildA(PolymorphicChildModelAdmin):
    raw_id_fields = ("child_bs",)


@register(M2MAdminTestChildB)
class M2MAdminTestChildB(PolymorphicChildModelAdmin):
    raw_id_fields = ("child_as",)


@register(M2MAdminTestChildC)
class M2MAdminTestChildC(PolymorphicChildModelAdmin):
    raw_id_fields = ("child_as",)


# Issue #182: M2M field in model admin
# Register models to test M2M field to polymorphic model
@register(M2MThroughBase)
class M2MThroughBaseAdmin(PolymorphicParentModelAdmin):
    """Base admin for polymorphic M2M test models."""

    child_models = (
        M2MThroughProject,
        M2MThroughPerson,
        M2MThroughProjectWithTeam,
        M2MThroughSpecialPerson,
    )


@register(M2MThroughProject)
class M2MThroughProjectAdmin(PolymorphicChildModelAdmin):
    """Admin for M2MThroughProject polymorphic child."""

    pass


@register(M2MThroughPerson)
class M2MThroughPersonAdmin(PolymorphicChildModelAdmin):
    """Admin for M2MThroughPerson polymorphic child."""

    pass


@register(M2MThroughSpecialPerson)
class M2MThroughSpecialPersonAdmin(PolymorphicChildModelAdmin):
    """Admin for M2MThroughSpecialPerson polymorphic child."""

    pass


@register(DirectM2MContainer)
class DirectM2MContainerAdmin(ModelAdmin):
    """
    Test case for Issue #182: M2M field in model admin.
    DirectM2MContainer has a direct M2M field to polymorphic M2MThroughBase model.
    This should work without AttributeError: 'int' object has no attribute 'pk'.
    """

    filter_horizontal = ("items",)


# Issue #375: Admin with M2M through table on polymorphic model
class M2MThroughMembershipInline(StackedPolymorphicInline):
    """
    Polymorphic inline for Issue #375: M2M through table with polymorphic membership types.
    This tests creating different membership types inline based on person type.
    """

    model = M2MThroughMembership
    extra = 1

    class MembershipWithPersonChild(StackedPolymorphicInline.Child):
        """Inline for regular Person membership."""

        model = M2MThroughMembershipWithPerson

    class MembershipWithSpecialPersonChild(StackedPolymorphicInline.Child):
        """Inline for SpecialPerson membership with special notes."""

        model = M2MThroughMembershipWithSpecialPerson

    child_inlines = (
        MembershipWithPersonChild,
        MembershipWithSpecialPersonChild,
    )


@register(M2MThroughProjectWithTeam)
class M2MThroughProjectWithTeamAdmin(PolymorphicInlineSupportMixin, PolymorphicChildModelAdmin):
    """
    Test case for Issue #375: Admin with M2M through table on polymorphic model.
    M2MThroughProjectWithTeam (polymorphic) has M2M to M2MThroughPerson (polymorphic)
    with custom through model M2MThroughMembership (now polymorphic).
    Uses polymorphic inlines to support different membership types.
    """

    inlines = (M2MThroughMembershipInline,)

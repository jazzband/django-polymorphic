from django.contrib import admin
from django.core.exceptions import PermissionDenied
from django.utils.translation import gettext_lazy as _


class PolymorphicChildModelFilter(admin.SimpleListFilter):
    """
    An admin list filter for the PolymorphicParentModelAdmin which enables
    filtering by its child models.

    This can be used in the parent admin:

    .. code-block:: python

        list_filter = (PolymorphicChildModelFilter,)
    """

    title = _("Type")
    parameter_name = "polymorphic_ctype"

    def lookups(self, request, model_admin):
        return model_admin.get_child_type_choices(request, "change")

    def queryset(self, request, queryset):
        try:
            value = int(self.value())
        except TypeError:
            value = None
        if value:
            # ensure the content type is allowed
            for choice_value, _ in self.lookup_choices:
                if choice_value == value:
                    return queryset.filter(polymorphic_ctype_id=choice_value)
            raise PermissionDenied(
                'Invalid ContentType "{}". It must be registered as child model.'.format(value)
            )
        return queryset

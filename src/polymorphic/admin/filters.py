from __future__ import annotations

from collections.abc import Iterable
from typing import Any, cast

from django.contrib import admin
from django.core.exceptions import PermissionDenied
from django.db.models import QuerySet
from django.http import HttpRequest
from django.utils.translation import gettext_lazy as _

from .parentadmin import PolymorphicParentModelAdmin


class PolymorphicChildModelFilter(admin.SimpleListFilter):
    """
    An admin list filter for the PolymorphicParentModelAdmin which enables
    filtering by its child models.

    This can be used in the parent admin:

    .. code-block:: python

        list_filter = (PolymorphicChildModelFilter,)
    """

    title: str = _("Type")  # type: ignore[assignment]
    parameter_name: str = "polymorphic_ctype"

    def lookups(  # type: ignore[override]
        self, request: HttpRequest, model_admin: PolymorphicParentModelAdmin
    ) -> Iterable[tuple[str, str]]:
        return cast(
            Iterable[tuple[str, str]], model_admin.get_child_type_choices(request, "change")
        )

    def queryset(self, request: HttpRequest, queryset: QuerySet[Any]) -> QuerySet[Any]:
        raw_value = self.value()
        if not raw_value:
            return queryset
        try:
            value = int(raw_value)
        except TypeError:
            value = None
        if value:
            # ensure the content type is allowed
            for choice_value, _ in self.lookup_choices:  # noqa: F402
                if int(choice_value) == value:
                    return queryset.filter(polymorphic_ctype_id=choice_value)
            raise PermissionDenied(
                f'Invalid ContentType "{value}". It must be registered as child model.'
            )
        return queryset

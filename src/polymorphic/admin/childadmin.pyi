from typing import Any, ClassVar, Sequence

from django.contrib import admin
from django_stubs.db import models
from django_stubs.forms import ModelForm
from django_stubs.http import HttpRequest, HttpResponse

from polymorphic.utils import get_base_polymorphic_model as get_base_polymorphic_model

from ..admin import PolymorphicParentModelAdmin as PolymorphicParentModelAdmin

class ParentAdminNotRegistered(RuntimeError): ...

class PolymorphicChildModelAdmin(admin.ModelAdmin[Any]):
    base_model: type[models.Model] | None
    base_form: type[ModelForm[Any]] | None
    base_fieldsets: list[tuple[str | None, dict[str, Any]]] | None
    extra_fieldset_title: str
    show_in_index: bool
    def __init__(
        self, model: type[models.Model], admin_site: Any, *args: Any, **kwargs: Any
    ) -> None: ...
    def get_form(
        self, request: HttpRequest, obj: Any = None, change: bool = False, **kwargs: Any
    ) -> type[ModelForm[Any]]: ...
    def get_model_perms(self, request: HttpRequest) -> dict[str, bool]: ...
    change_form_template: ClassVar[str]
    delete_confirmation_template: ClassVar[str]
    object_history_template: ClassVar[str]
    def response_post_save_add(self, request: HttpRequest, obj: Any) -> HttpResponse: ...
    def response_post_save_change(self, request: HttpRequest, obj: Any) -> HttpResponse: ...
    def render_change_form(
        self,
        request: HttpRequest,
        context: Any,
        add: bool = False,
        change: bool = False,
        form_url: str = "",
        obj: Any = None,
    ) -> HttpResponse: ...
    def delete_view(
        self, request: HttpRequest, object_id: str, context: Any = None
    ) -> HttpResponse: ...
    def history_view(
        self, request: HttpRequest, object_id: str, extra_context: Any = None
    ) -> HttpResponse: ...
    def get_base_fieldsets(
        self, request: HttpRequest, obj: Any = None
    ) -> list[tuple[str | None, dict[str, Any]]]: ...
    def get_fieldsets(self, request: HttpRequest, obj: Any = None) -> list[Any]: ...
    def get_subclass_fields(
        self, request: HttpRequest, obj: Any = None
    ) -> Sequence[str] | list[str]: ...

from typing import Any, ClassVar, Sequence

from django_stubs.contrib import admin
from django_stubs.db.models import Model
from django_stubs.db.models.query import QuerySet
from django_stubs.forms import ModelForm
from django_stubs.http import HttpRequest, HttpResponse

from polymorphic.utils import get_base_polymorphic_model as get_base_polymorphic_model

from .forms import PolymorphicModelChoiceForm as PolymorphicModelChoiceForm

class RegistrationClosed(RuntimeError): ...
class ChildAdminNotRegistered(RuntimeError): ...

class PolymorphicParentModelAdmin(admin.ModelAdmin[Any]):
    base_model: type[Model] | None
    child_models: Sequence[type[Model]] | None
    polymorphic_list: bool
    add_type_template: str | None
    add_type_form: type[ModelForm[Any]]
    pk_regex: str
    def __init__(self, model: type[Model], admin_site: Any, *args: Any, **kwargs: Any) -> None: ...
    def register_child(
        self, model: type[Model], model_admin: type[admin.ModelAdmin[Any]]
    ) -> None: ...
    def get_child_models(self) -> Sequence[type[Model]]: ...
    def get_child_type_choices(
        self, request: HttpRequest, action: str
    ) -> list[tuple[str, str]]: ...
    def get_queryset(self, request: HttpRequest) -> QuerySet[Any]: ...
    def add_view(
        self, request: HttpRequest, form_url: str = "", extra_context: Any = None
    ) -> HttpResponse: ...
    def change_view(
        self, request: HttpRequest, object_id: str, *args: Any, **kwargs: Any
    ) -> HttpResponse: ...
    def changeform_view(
        self,
        request: HttpRequest,
        object_id: str | None = None,
        *args: Any,
        **kwargs: Any,
    ) -> HttpResponse: ...
    def history_view(
        self, request: HttpRequest, object_id: str, extra_context: Any = None
    ) -> HttpResponse: ...
    def delete_view(
        self, request: HttpRequest, object_id: str, extra_context: Any = None
    ) -> HttpResponse: ...
    def get_preserved_filters(self, request: HttpRequest) -> str: ...
    def get_urls(self) -> list[Any]: ...
    def subclass_view(self, request: HttpRequest, path: str) -> HttpResponse: ...
    def add_type_view(self, request: HttpRequest, form_url: str = "") -> HttpResponse: ...
    def render_add_type_form(
        self, request: HttpRequest, context: Any, form_url: str = ""
    ) -> HttpResponse: ...
    change_list_template: ClassVar[str]

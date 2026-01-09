from typing import Any

from django.contrib import admin
from django_stubs.db.models.query import QuerySet
from django_stubs.http import HttpRequest

class PolymorphicChildModelFilter(admin.SimpleListFilter):
    title: str
    parameter_name: str
    def lookups(self, request: HttpRequest, model_admin): ...
    def queryset(self, request: HttpRequest, queryset: QuerySet[Any]): ...

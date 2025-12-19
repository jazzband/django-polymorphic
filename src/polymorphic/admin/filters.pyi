from _typeshed import Incomplete
from django.contrib import admin

class PolymorphicChildModelFilter(admin.SimpleListFilter):
    title: Incomplete
    parameter_name: str
    def lookups(self, request, model_admin): ...
    def queryset(self, request, queryset): ...

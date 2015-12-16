from django.contrib import admin
from polymorphic.admin import PolymorphicParentModelAdmin, PolymorphicChildModelAdmin, PolymorphicChildModelFilter
from pexp.models import *


class ProjectChildAdmin(PolymorphicChildModelAdmin):
    base_model = Project

    # On purpose, only have the shared fields here.
    # The fields of the derived model should still be displayed.
    base_fieldsets = (
        ("Base fields", {
            'fields': ('topic',)
        }),
    )

class ProjectAdmin(PolymorphicParentModelAdmin):
    base_model = Project
    list_filter = (PolymorphicChildModelFilter,)
    child_models = (
        (Project, ProjectChildAdmin),
        (ArtProject, ProjectChildAdmin),
        (ResearchProject, ProjectChildAdmin),
    )

admin.site.register(Project, ProjectAdmin)



class ModelAChildAdmin(PolymorphicChildModelAdmin):
    base_model = ModelA

class ModelAAdmin(PolymorphicParentModelAdmin):
    base_model = ModelA
    list_filter = (PolymorphicChildModelFilter,)
    child_models = (
        (ModelA, ModelAChildAdmin),
        (ModelB, ModelAChildAdmin),
        (ModelC, ModelAChildAdmin),
    )

admin.site.register(ModelA, ModelAAdmin)


class Model2AChildAdmin(PolymorphicChildModelAdmin):
    base_model = Model2A

class Model2AAdmin(PolymorphicParentModelAdmin):
    base_model = Model2A
    list_filter = (PolymorphicChildModelFilter,)
    child_models = (
        (Model2A, Model2AChildAdmin),
        (Model2B, Model2AChildAdmin),
        (Model2C, Model2AChildAdmin),
    )

admin.site.register(Model2A, Model2AAdmin)


class UUIDModelAChildAdmin(PolymorphicChildModelAdmin):
    base_model = UUIDModelA

class UUIDModelAAdmin(PolymorphicParentModelAdmin):
    base_model = UUIDModelA
    list_filter = (PolymorphicChildModelFilter,)
    child_models = (
        (UUIDModelA, UUIDModelAChildAdmin),
        (UUIDModelB, UUIDModelAChildAdmin),
        (UUIDModelC, UUIDModelAChildAdmin),
    )

admin.site.register(UUIDModelA, UUIDModelAAdmin)


class ProxyChildAdmin(PolymorphicChildModelAdmin):
    base_model = ProxyBase

class ProxyAdmin(PolymorphicParentModelAdmin):
    base_model = ProxyBase
    list_filter = (PolymorphicChildModelFilter,)
    child_models = (
        (ProxyA, ProxyChildAdmin),
        (ProxyB, ProxyChildAdmin),
    )

admin.site.register(ProxyBase, ProxyAdmin)

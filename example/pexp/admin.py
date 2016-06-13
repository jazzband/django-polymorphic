from django.contrib import admin
from polymorphic.admin import PolymorphicParentModelAdmin, PolymorphicChildModelAdmin, PolymorphicChildModelFilter
from pexp.models import *


class ProjectAdmin(PolymorphicParentModelAdmin):
    base_model = Project
    list_filter = (PolymorphicChildModelFilter,)
    child_models = (Project, ArtProject, ResearchProject)


class ProjectChildAdmin(PolymorphicChildModelAdmin):
    base_model = Project

    # On purpose, only have the shared fields here.
    # The fields of the derived model should still be displayed.
    base_fieldsets = (
        ("Base fields", {
            'fields': ('topic',)
        }),
    )


admin.site.register(Project, ProjectAdmin)
admin.site.register(ArtProject, ProjectChildAdmin)
admin.site.register(ResearchProject, ProjectChildAdmin)


class ModelAAdmin(PolymorphicParentModelAdmin):
    base_model = ModelA
    list_filter = (PolymorphicChildModelFilter,)
    child_models = (ModelA, ModelB, ModelC)


class ModelAChildAdmin(PolymorphicChildModelAdmin):
    base_model = ModelA


admin.site.register(ModelA, ModelAAdmin)
admin.site.register(ModelB, ModelAChildAdmin)
admin.site.register(ModelC, ModelAChildAdmin)


class Model2AAdmin(PolymorphicParentModelAdmin):
    base_model = Model2A
    list_filter = (PolymorphicChildModelFilter,)
    child_models = (Model2A, Model2B, Model2C)


class Model2AChildAdmin(PolymorphicChildModelAdmin):
    base_model = Model2A


admin.site.register(Model2A, Model2AAdmin)
admin.site.register(Model2B, Model2AChildAdmin)
admin.site.register(Model2C, Model2AChildAdmin)


class UUIDModelAAdmin(PolymorphicParentModelAdmin):
    base_model = UUIDModelA
    list_filter = (PolymorphicChildModelFilter,)
    child_models = (UUIDModelA, UUIDModelB)


class UUIDModelAChildAdmin(PolymorphicChildModelAdmin):
    base_model = UUIDModelA


admin.site.register(UUIDModelA, UUIDModelAAdmin)
admin.site.register(UUIDModelB, UUIDModelAChildAdmin)
admin.site.register(UUIDModelC, UUIDModelAChildAdmin)


class ProxyAdmin(PolymorphicParentModelAdmin):
    base_model = ProxyBase
    list_filter = (PolymorphicChildModelFilter,)
    child_models = (ProxyA, ProxyB)


class ProxyChildAdmin(PolymorphicChildModelAdmin):
    base_model = ProxyBase


admin.site.register(ProxyBase, ProxyAdmin)
admin.site.register(ProxyA, ProxyChildAdmin)
admin.site.register(ProxyB, ProxyChildAdmin)

from django.contrib import admin
from polymorphic.admin import PolymorphicParentModelAdmin, \
    PolymorphicChildModelAdmin, PolymorphicChildModelFilter
from pexp import models


class ProjectChildAdmin(PolymorphicChildModelAdmin):
    base_model = models.Project

    # On purpose, only have the shared fields here.
    # The fields of the derived model should still be displayed.
    base_fieldsets = (
        ("Base fields", {
            'fields': ('topic',)
        }),
    )


class ProjectAdmin(PolymorphicParentModelAdmin):
    base_model = models.Project
    list_filter = (PolymorphicChildModelFilter,)
    child_models = (
        (models.Project, ProjectChildAdmin),
        (models.ArtProject, ProjectChildAdmin),
        (models.ResearchProject, ProjectChildAdmin),
    )

admin.site.register(models.Project, ProjectAdmin)


class ModelAChildAdmin(PolymorphicChildModelAdmin):
    base_model = models.ModelA


class ModelAAdmin(PolymorphicParentModelAdmin):
    base_model = models.ModelA
    list_filter = (PolymorphicChildModelFilter,)
    child_models = (
        (models.ModelA, ModelAChildAdmin),
        (models.ModelB, ModelAChildAdmin),
        (models.ModelC, ModelAChildAdmin),
    )

admin.site.register(models.ModelA, ModelAAdmin)


class Model2AChildAdmin(PolymorphicChildModelAdmin):
    base_model = models.Model2A


class Model2AAdmin(PolymorphicParentModelAdmin):
    base_model = models.Model2A
    list_filter = (PolymorphicChildModelFilter,)
    child_models = (
        (models.Model2A, Model2AChildAdmin),
        (models.Model2B, Model2AChildAdmin),
        (models.Model2C, Model2AChildAdmin),
    )

admin.site.register(models.Model2A, Model2AAdmin)


class UUIDModelAChildAdmin(PolymorphicChildModelAdmin):
    base_model = models.UUIDModelA


class UUIDModelAAdmin(PolymorphicParentModelAdmin):
    base_model = models.UUIDModelA
    list_filter = (PolymorphicChildModelFilter,)
    child_models = (
        (models.UUIDModelA, UUIDModelAChildAdmin),
        (models.UUIDModelB, UUIDModelAChildAdmin),
        (models.UUIDModelC, UUIDModelAChildAdmin),
    )

admin.site.register(models.UUIDModelA, UUIDModelAAdmin)


class ProxyChildAdmin(PolymorphicChildModelAdmin):
    base_model = models.ProxyBase


class ProxyAdmin(PolymorphicParentModelAdmin):
    base_model = models.ProxyBase
    list_filter = (PolymorphicChildModelFilter,)
    child_models = (
        (models.ProxyA, ProxyChildAdmin),
        (models.ProxyB, ProxyChildAdmin),
    )

admin.site.register(models.ProxyBase, ProxyAdmin)

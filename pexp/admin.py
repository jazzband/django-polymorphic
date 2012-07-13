from django.contrib import admin
from polymorphic.admin import PolymorphicParentModelAdmin, PolymorphicChildModelAdmin
from pexp.models import *


class ProjectChildAdmin(PolymorphicChildModelAdmin):
    base_model = Project

class ProjectAdmin(PolymorphicParentModelAdmin):
    base_model = Project
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
    child_models = (
        (ModelA, ModelAChildAdmin),
        (ModelB, ModelAChildAdmin),
        (ModelC, ModelAChildAdmin),
    )

admin.site.register(ModelA, ModelAAdmin)


if 'Model2A' in globals():
    class Model2AChildAdmin(PolymorphicChildModelAdmin):
        base_model = Model2A

    class Model2AAdmin(PolymorphicParentModelAdmin):
        base_model = Model2A
        child_models = (
            (Model2A, Model2AChildAdmin),
            (Model2B, Model2AChildAdmin),
            (Model2C, Model2AChildAdmin),
        )

    admin.site.register(Model2A, Model2AAdmin)


if 'UUIDModelA' in globals():
    class UUIDModelAChildAdmin(PolymorphicChildModelAdmin):
        base_model = UUIDModelA

    class UUIDModelAAdmin(PolymorphicParentModelAdmin):
        base_model = UUIDModelA
        child_models = (
            (UUIDModelA, UUIDModelAChildAdmin),
            (UUIDModelB, UUIDModelAChildAdmin),
            (UUIDModelC, UUIDModelAChildAdmin),
        )

    admin.site.register(UUIDModelA, UUIDModelAAdmin)


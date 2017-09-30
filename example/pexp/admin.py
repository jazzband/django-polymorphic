from django.contrib import admin
from polymorphic.admin import PolymorphicParentModelAdmin, PolymorphicChildModelAdmin, PolymorphicChildModelFilter
from pexp.models import *


class ProjectAdmin(PolymorphicParentModelAdmin):
    base_model = Project  # Can be set explicitly.
    list_filter = (PolymorphicChildModelFilter,)
    child_models = (Project, ArtProject, ResearchProject)


class ProjectChildAdmin(PolymorphicChildModelAdmin):
    base_model = Project  # Can be set explicitly.

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


class UUIDModelAAdmin(PolymorphicParentModelAdmin):
    list_filter = (PolymorphicChildModelFilter,)
    child_models = (UUIDModelA, UUIDModelB)


class UUIDModelAChildAdmin(PolymorphicChildModelAdmin):
    pass


admin.site.register(UUIDModelA, UUIDModelAAdmin)
admin.site.register(UUIDModelB, UUIDModelAChildAdmin)
admin.site.register(UUIDModelC, UUIDModelAChildAdmin)


class ProxyAdmin(PolymorphicParentModelAdmin):
    list_filter = (PolymorphicChildModelFilter,)
    child_models = (ProxyA, ProxyB)


class ProxyChildAdmin(PolymorphicChildModelAdmin):
    pass


admin.site.register(ProxyBase, ProxyAdmin)
admin.site.register(ProxyA, ProxyChildAdmin)
admin.site.register(ProxyB, ProxyChildAdmin)

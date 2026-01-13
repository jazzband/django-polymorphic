from django.apps import AppConfig, apps
from django.core.checks import Error, Tags, Warning, register


@register(Tags.models)
def check_reserved_field_names(app_configs, **kwargs):
    """
    System check that ensures models don't use reserved field names.
    """
    from .models import PolymorphicModel

    findings = []

    for app_config in app_configs or apps.get_app_configs():
        for model in app_config.get_models():
            if issubclass(model, PolymorphicModel):
                findings.extend(_check_model_reserved_field_names(model))
                findings.extend(_check_polymorphic_managers(model))

    return findings


def _check_polymorphic_managers(model):
    from polymorphic.managers import PolymorphicManager
    from polymorphic.query import PolymorphicQuerySet

    findings = []

    # First manager declared with use_in_migrations=True wins.
    for mgr in model._meta.managers:
        if getattr(mgr, "use_in_migrations", True):
            if isinstance(mgr, PolymorphicManager):
                findings.append(
                    Error(
                        f"The migration manager '{model._meta.label}.{mgr.name}' is polymorphic.",
                        obj=mgr,
                        hint="Set use_in_migrations = False on the manager.",
                        id="polymorphic.E002",
                    )
                )
            break

    for manager in ["base", "default"]:
        mgr = getattr(model._meta, f"{manager}_manager")
        if not isinstance(mgr, PolymorphicManager):
            findings.append(
                Warning(
                    f"The {manager} manager {model._meta.label}.{mgr.name}' is not polymorphic.",
                    obj=mgr,
                    id="polymorphic.W001",
                )
            )
        if not isinstance(mgr.get_queryset(), PolymorphicQuerySet):
            findings.append(
                Warning(
                    f"The {manager} manager {model._meta.label}.{mgr.name}' is not "
                    "using a PolymorphicQuerySet.",
                    obj=mgr,
                    id="polymorphic.W002",
                )
            )

    return findings


def _check_model_reserved_field_names(model):
    from polymorphic.base import POLYMORPHIC_SPECIAL_Q_KWORDS

    errors = []

    for field in model._meta.get_fields():
        if field.name in POLYMORPHIC_SPECIAL_Q_KWORDS:
            errors.append(
                Error(
                    f"Field '{field.name}' on model '{model.__name__}' is a reserved name.",
                    obj=field,
                    id="polymorphic.E001",
                )
            )

    return errors


class PolymorphicConfig(AppConfig):
    name = "polymorphic"
    verbose_name = "Django Polymorphic"

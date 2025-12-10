from django.apps import AppConfig, apps
from django.core.checks import Error, Tags, register


@register(Tags.models)
def check_reserved_field_names(app_configs, **kwargs):
    """
    System check that ensures models don't use reserved field names.
    """
    errors = []

    # If app_configs is None, check all installed apps
    if app_configs is None:
        app_configs = apps.get_app_configs()

    for app_config in app_configs:
        for model in app_config.get_models():
            errors.extend(_check_model_reserved_field_names(model))

    return errors


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

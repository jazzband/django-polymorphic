from typing import Any

from django_stubs.apps import AppConfig

def check_reserved_field_names(
    app_configs: list[type[AppConfig]] | None, **kwargs
) -> list[Any]: ...

class PolymorphicConfig(AppConfig):
    ignored_models: list[Any]
    verbose_name: str

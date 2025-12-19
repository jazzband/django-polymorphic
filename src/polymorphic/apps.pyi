from django_stubs.apps import AppConfig

def check_reserved_field_names(app_configs: list[AppConfig] | None, **kwargs) -> list: ...

class PolymorphicConfig(AppConfig):
    name: str
    verbose_name: str

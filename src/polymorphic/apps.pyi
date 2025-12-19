from django.apps import AppConfig

def check_reserved_field_names(app_configs, **kwargs): ...

class PolymorphicConfig(AppConfig):
    name: str
    verbose_name: str

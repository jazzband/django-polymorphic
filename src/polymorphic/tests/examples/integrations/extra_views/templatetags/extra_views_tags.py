from django import template

register = template.Library()


@register.filter
def model_name(instance):
    """Get the model class name of an instance."""
    return instance._meta.verbose_name.title()

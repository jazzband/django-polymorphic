import json

from django.template import Library
from django.utils.encoding import force_str
from django.utils.text import capfirst
from django.utils.translation import gettext

from polymorphic.formsets import BasePolymorphicModelFormSet

register = Library()


@register.filter()
def include_empty_form(formset):
    """
    Make sure the "empty form" is included when displaying a formset (typically table with input rows)
    """
    yield from formset

    if hasattr(formset, "empty_forms"):
        # BasePolymorphicModelFormSet
        yield from formset.empty_forms
    else:
        # Standard Django formset
        yield formset.empty_form


@register.filter
def as_script_options(formset):
    """
    A JavaScript data structure for the JavaScript code

    This generates the ``data-options`` attribute for ``jquery.django-inlines.js``
    The formset may define the following extra attributes:

    - ``verbose_name``
    - ``add_text``
    - ``show_add_button``
    """
    verbose_name = getattr(formset, "verbose_name", formset.model._meta.verbose_name)
    options = {
        "prefix": formset.prefix,
        "pkFieldName": formset.model._meta.pk.name,
        "addText": getattr(formset, "add_text", None)
        or gettext("Add another %(verbose_name)s") % {"verbose_name": capfirst(verbose_name)},
        "showAddButton": getattr(formset, "show_add_button", True),
        "deleteText": gettext("Delete"),
    }

    if isinstance(formset, BasePolymorphicModelFormSet):
        # Allow to add different types
        options["childTypes"] = [
            {
                "name": force_str(model._meta.verbose_name),
                "type": model._meta.model_name,
            }
            for model in formset.child_forms.keys()
        ]

    return json.dumps(options)


@register.filter
def as_form_type(form):
    """
    Usage: ``{{ form|as_form_type }}``
    """
    return form._meta.model._meta.model_name


@register.filter
def as_model_name(model):
    """
    Usage: ``{{ model|as_model_name }}``
    """
    return model._meta.model_name

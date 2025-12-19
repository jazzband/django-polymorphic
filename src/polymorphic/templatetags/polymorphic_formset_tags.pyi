from collections.abc import Generator

from _typeshed import Incomplete

from polymorphic.formsets import BasePolymorphicModelFormSet as BasePolymorphicModelFormSet

register: Incomplete

def include_empty_form(formset) -> Generator[Incomplete, Incomplete]: ...
@register.filter
def as_script_options(formset): ...
@register.filter
def as_form_type(form): ...
@register.filter
def as_model_name(model): ...

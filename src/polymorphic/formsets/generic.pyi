from _typeshed import Incomplete
from django.contrib.contenttypes.forms import BaseGenericInlineFormSet

from .models import BasePolymorphicModelFormSet as BasePolymorphicModelFormSet
from .models import PolymorphicFormSetChild as PolymorphicFormSetChild
from .models import polymorphic_child_forms_factory as polymorphic_child_forms_factory

class GenericPolymorphicFormSetChild(PolymorphicFormSetChild):
    ct_field: Incomplete
    fk_field: Incomplete
    def __init__(self, *args, **kwargs) -> None: ...
    def get_form(self, ct_field: str = "content_type", fk_field: str = "object_id", **kwargs): ...

class BaseGenericPolymorphicInlineFormSet(
    BaseGenericInlineFormSet, BasePolymorphicModelFormSet
): ...

def generic_polymorphic_inlineformset_factory(
    model,
    formset_children,
    form=...,
    formset=...,
    ct_field: str = "content_type",
    fk_field: str = "object_id",
    fields=None,
    exclude=None,
    extra: int = 1,
    can_order: bool = False,
    can_delete: bool = True,
    max_num=None,
    formfield_callback=None,
    validate_max: bool = False,
    for_concrete_model: bool = True,
    min_num=None,
    validate_min: bool = False,
    child_form_kwargs=None,
): ...

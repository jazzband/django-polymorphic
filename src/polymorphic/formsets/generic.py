from __future__ import annotations

from collections.abc import Callable, Iterable
from typing import Any, cast

from django.contrib.contenttypes.forms import (
    BaseGenericInlineFormSet,
    generic_inlineformset_factory,
)
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.forms.models import ModelForm

from .models import (
    BasePolymorphicModelFormSet,
    PolymorphicFormSetChild,
    polymorphic_child_forms_factory,
)


class GenericPolymorphicFormSetChild(PolymorphicFormSetChild):
    """
    Formset child for generic inlines
    """

    ct_field: str
    fk_field: str

    def __init__(
        self,
        *args: Any,
        ct_field: str = "content_type",
        fk_field: str = "object_id",
        **kwargs: Any,
    ) -> None:
        self.ct_field = ct_field
        self.fk_field = fk_field
        super().__init__(*args, **kwargs)

    def get_form(
        self, ct_field: str = "content_type", fk_field: str = "object_id", **kwargs: Any
    ) -> type[ModelForm[Any]]:
        """
        Construct the form class for the formset child.
        """
        exclude = list(self.exclude)
        extra_exclude = kwargs.pop("extra_exclude", None)
        if extra_exclude:
            exclude += list(extra_exclude)

        # Make sure the GFK fields are excluded by default
        # This is similar to what generic_inlineformset_factory() does
        # if there is no field called `ct_field` let the exception propagate
        opts = self.model._meta
        ct_field_obj = opts.get_field(self.ct_field)

        if (
            not isinstance(ct_field_obj, models.ForeignKey)
            or ct_field_obj.remote_field.model != ContentType
        ):
            raise Exception(f"fk_name '{ct_field_obj}' is not a ForeignKey to ContentType")

        fk_field_obj = opts.get_field(self.fk_field)  # let the exception propagate
        exclude.extend([ct_field_obj.name, fk_field_obj.name])
        kwargs["exclude"] = exclude

        return super().get_form(**kwargs)


class BaseGenericPolymorphicInlineFormSet(BaseGenericInlineFormSet, BasePolymorphicModelFormSet):
    """
    Polymorphic formset variation for inline generic formsets
    """


def generic_polymorphic_inlineformset_factory(
    model: type[models.Model],
    formset_children: Iterable[PolymorphicFormSetChild],
    form: type[ModelForm[Any]] = ModelForm,
    formset: type[BaseGenericPolymorphicInlineFormSet] = BaseGenericPolymorphicInlineFormSet,
    ct_field: str = "content_type",
    fk_field: str = "object_id",
    # Base form
    # TODO: should these fields be removed in favor of creating
    # the base form as a formset child too?
    fields: list[str] | None = None,
    exclude: list[str] | None = None,
    extra: int = 1,
    can_order: bool = False,
    can_delete: bool = True,
    max_num: int | None = None,
    formfield_callback: Callable[..., Any] | None = None,
    validate_max: bool = False,
    for_concrete_model: bool = True,
    min_num: int | None = None,
    validate_min: bool = False,
    child_form_kwargs: dict[str, Any] | None = None,
) -> type[BaseGenericPolymorphicInlineFormSet]:
    """
    Construct the class for a generic inline polymorphic formset.

    All arguments are identical to :func:`~django.contrib.contenttypes.forms.generic_inlineformset_factory`,
    with the exception of the ``formset_children`` argument.

    :param formset_children: A list of all child :class:`PolymorphicFormSetChild` objects
                             that tell the inline how to render the child model types.
    :type formset_children: Iterable[PolymorphicFormSetChild]
    :rtype: type
    """
    kwargs = {
        "model": model,
        "form": form,
        "formfield_callback": formfield_callback,
        "formset": formset,
        "ct_field": ct_field,
        "fk_field": fk_field,
        "extra": extra,
        "can_delete": can_delete,
        "can_order": can_order,
        "fields": fields,
        "exclude": exclude,
        "min_num": min_num,
        "max_num": max_num,
        "validate_min": validate_min,
        "validate_max": validate_max,
        "for_concrete_model": for_concrete_model,
        # 'localized_fields': localized_fields,
        # 'labels': labels,
        # 'help_texts': help_texts,
        # 'error_messages': error_messages,
        # 'field_classes': field_classes,
    }
    if child_form_kwargs is None:
        child_form_kwargs = {}

    child_kwargs = {
        # 'exclude': exclude,
        "ct_field": ct_field,
        "fk_field": fk_field,
    }
    if child_form_kwargs:
        child_kwargs.update(child_form_kwargs)

    FormSet = generic_inlineformset_factory(**kwargs)  # type: ignore[arg-type]
    FormSet.child_forms = polymorphic_child_forms_factory(formset_children, **child_kwargs)  # type: ignore[attr-defined]
    return cast(type[BaseGenericPolymorphicInlineFormSet], FormSet)

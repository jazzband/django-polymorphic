import django
from django.contrib.contenttypes.forms import BaseGenericInlineFormSet, generic_inlineformset_factory
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.forms.models import ModelForm

from .models import BasePolymorphicModelFormSet, polymorphic_child_forms_factory, PolymorphicFormSetChild


class GenericPolymorphicFormSetChild(PolymorphicFormSetChild):
    """
    Formset child for generic inlines
    """
    def __init__(self, *args, **kwargs):
        self.ct_field = kwargs.pop('ct_field', 'content_type')
        self.fk_field = kwargs.pop('fk_field', 'object_id')
        super(GenericPolymorphicFormSetChild, self).__init__(*args, **kwargs)

    def get_form(self, ct_field="content_type", fk_field="object_id", **kwargs):
        """
        Construct the form class for the formset child.
        """
        exclude = list(self.exclude)
        extra_exclude = kwargs.pop('extra_exclude', None)
        if extra_exclude:
            exclude += list(extra_exclude)

        # Make sure the GFK fields are excluded by default
        # This is similar to what generic_inlineformset_factory() does
        # if there is no field called `ct_field` let the exception propagate
        opts = self.model._meta
        ct_field = opts.get_field(self.ct_field)

        if django.VERSION >= (1, 9):
            if not isinstance(ct_field, models.ForeignKey) or ct_field.remote_field.model != ContentType:
                raise Exception("fk_name '%s' is not a ForeignKey to ContentType" % ct_field)
        else:
            if not isinstance(ct_field, models.ForeignKey) or ct_field.rel.to != ContentType:
                raise Exception("fk_name '%s' is not a ForeignKey to ContentType" % ct_field)

        fk_field = opts.get_field(self.fk_field)  # let the exception propagate
        exclude.extend([ct_field.name, fk_field.name])
        kwargs['exclude'] = exclude

        return super(GenericPolymorphicFormSetChild, self).get_form(**kwargs)


class BaseGenericPolymorphicInlineFormSet(BaseGenericInlineFormSet, BasePolymorphicModelFormSet):
    """
    Polymorphic formset variation for inline generic formsets
    """


def generic_polymorphic_inlineformset_factory(model, formset_children, form=ModelForm,
                                              formset=BaseGenericPolymorphicInlineFormSet,
                                              ct_field="content_type", fk_field="object_id",
                                              # Base form
                                              # TODO: should these fields be removed in favor of creating
                                              # the base form as a formset child too?
                                              fields=None, exclude=None,
                                              extra=1, can_order=False, can_delete=True,
                                              max_num=None, formfield_callback=None,
                                              validate_max=False, for_concrete_model=True,
                                              min_num=None, validate_min=False, child_form_kwargs=None):
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
        'model': model,
        'form': form,
        'formfield_callback': formfield_callback,
        'formset': formset,
        'ct_field': ct_field,
        'fk_field': fk_field,
        'extra': extra,
        'can_delete': can_delete,
        'can_order': can_order,
        'fields': fields,
        'exclude': exclude,
        'min_num': min_num,
        'max_num': max_num,
        'validate_min': validate_min,
        'validate_max': validate_max,
        'for_concrete_model': for_concrete_model,
        #'localized_fields': localized_fields,
        #'labels': labels,
        #'help_texts': help_texts,
        #'error_messages': error_messages,
        #'field_classes': field_classes,
    }
    if child_form_kwargs is None:
        child_form_kwargs = {}

    child_kwargs = {
        #'exclude': exclude,
        'ct_field': ct_field,
        'fk_field': fk_field,
    }
    if child_form_kwargs:
        child_kwargs.update(child_form_kwargs)

    FormSet = generic_inlineformset_factory(**kwargs)
    FormSet.child_forms = polymorphic_child_forms_factory(formset_children, **child_kwargs)
    return FormSet

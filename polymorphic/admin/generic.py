from django.contrib.contenttypes.admin import GenericInlineModelAdmin
from django.contrib.contenttypes.models import ContentType
from django.utils.functional import cached_property

from polymorphic.formsets import polymorphic_child_forms_factory, BaseGenericPolymorphicInlineFormSet, GenericPolymorphicFormSetChild
from .inlines import PolymorphicInlineModelAdmin


class GenericPolymorphicInlineModelAdmin(PolymorphicInlineModelAdmin, GenericInlineModelAdmin):
    """
    Base class for variation of inlines based on generic foreign keys.
    """
    #: The formset class
    formset = BaseGenericPolymorphicInlineFormSet

    def get_formset(self, request, obj=None, **kwargs):
        """
        Construct the generic inline formset class.
        """
        # Construct the FormSet class. This is almost the same as parent version,
        # except that a different super is called so generic_inlineformset_factory() is used.
        # NOTE that generic_inlineformset_factory() also makes sure the GFK fields are excluded in the form.
        FormSet = GenericInlineModelAdmin.get_formset(self, request, obj=obj, **kwargs)

        FormSet.child_forms = polymorphic_child_forms_factory(
            formset_children=self.get_formset_children(request, obj=obj)
        )
        return FormSet

    class Child(PolymorphicInlineModelAdmin.Child):
        """
        Variation for generic inlines.
        """
        # Make sure that the GFK fields are excluded from the child forms
        formset_child = GenericPolymorphicFormSetChild
        ct_field = "content_type"
        ct_fk_field = "object_id"

        @cached_property
        def content_type(self):
            """
            Expose the ContentType that the child relates to.
            This can be used for the ``polymorphic_ctype`` field.
            """
            return ContentType.objects.get_for_model(self.model, for_concrete_model=False)

        def get_formset_child(self, request, obj=None, **kwargs):
            # Similar to GenericInlineModelAdmin.get_formset(),
            # make sure the GFK is automatically excluded from the form
            defaults = {
                "ct_field": self.ct_field,
                "fk_field": self.ct_fk_field,
            }
            defaults.update(kwargs)
            return super(GenericPolymorphicInlineModelAdmin.Child, self).get_formset_child(request, obj=obj, **defaults)


class GenericStackedPolymorphicInline(GenericPolymorphicInlineModelAdmin):
    """
    The stacked layout for generic inlines.
    """
    #: The default template to use.
    template = 'admin/polymorphic/edit_inline/stacked.html'

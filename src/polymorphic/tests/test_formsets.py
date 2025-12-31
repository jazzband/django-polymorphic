"""
Tests for polymorphic formsets.
"""

import pytest
from django import forms
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ImproperlyConfigured, ValidationError
from django.test import TestCase

from polymorphic.formsets.models import (
    PolymorphicFormSetChild,
    UnsupportedChildType,
    polymorphic_inlineformset_factory,
    polymorphic_modelformset_factory,
)
from polymorphic.tests.models import Model2A, Model2B, Model2C


class PolymorphicFormSetChildTest(TestCase):
    """Test PolymorphicFormSetChild configuration"""

    def test_content_type_property(self):
        """ContentType is cached for child model"""
        child = PolymorphicFormSetChild(model=Model2A)
        ct = child.content_type

        assert ct.model_class() == Model2A
        assert child.content_type is ct  # Verify caching

    def test_extra_exclude_parameter(self):
        """extra_exclude adds to existing exclude list"""
        child = PolymorphicFormSetChild(model=Model2A, exclude=["field1"])
        form_class = child.get_form(extra_exclude=["field2"])
        form = form_class()

        assert "field1" not in form.fields
        assert "field2" not in form.fields


class PolymorphicModelFormSetTest(TestCase):
    """Test polymorphic model formset functionality"""

    def setUp(self):
        self.obj_a = Model2A.objects.create(field1="A1")
        self.obj_b = Model2B.objects.create(field1="B1", field2="B2")

    def test_empty_form_property_raises_error(self):
        """Accessing empty_form raises RuntimeError (use empty_forms instead)"""
        FormSet = polymorphic_modelformset_factory(
            model=Model2A,
            fields="__all__",
            formset_children=[PolymorphicFormSetChild(model=Model2A)],
        )
        formset = FormSet(queryset=Model2A.objects.none())

        with pytest.raises(RuntimeError, match="use 'empty_forms'"):
            _ = formset.empty_form

    def test_error_no_child_forms(self):
        """get_form_class raises ImproperlyConfigured when child_forms empty"""
        FormSet = polymorphic_modelformset_factory(
            model=Model2A,
            fields="__all__",
            formset_children=[PolymorphicFormSetChild(model=Model2A)],
        )
        formset = FormSet(queryset=Model2A.objects.none())
        formset.child_forms = {}

        with pytest.raises(ImproperlyConfigured, match="No 'child_forms' defined"):
            formset.get_form_class(Model2A)

    def test_error_non_polymorphic_model(self):
        """get_form_class raises TypeError for non-polymorphic models"""
        from django.contrib.auth.models import User

        FormSet = polymorphic_modelformset_factory(
            model=Model2A,
            fields="__all__",
            formset_children=[PolymorphicFormSetChild(model=Model2A)],
        )
        formset = FormSet(queryset=Model2A.objects.none())

        with pytest.raises(TypeError, match="Expect polymorphic model"):
            formset.get_form_class(User)

    def test_error_unsupported_child_type(self):
        """get_form_class raises UnsupportedChildType for unregistered models"""
        FormSet = polymorphic_modelformset_factory(
            model=Model2A,
            fields="__all__",
            formset_children=[PolymorphicFormSetChild(model=Model2A)],
        )
        formset = FormSet(queryset=Model2A.objects.none())

        with pytest.raises(UnsupportedChildType, match="no form class is registered"):
            formset.get_form_class(Model2B)

    def test_bound_formset_with_data(self):
        """Bound formset processes existing objects correctly"""
        FormSet = polymorphic_modelformset_factory(
            model=Model2A,
            fields="__all__",
            formset_children=[
                PolymorphicFormSetChild(model=Model2A),
                PolymorphicFormSetChild(model=Model2B),
            ],
        )

        ct_a = ContentType.objects.get_for_model(Model2A, for_concrete_model=False)
        ct_b = ContentType.objects.get_for_model(Model2B, for_concrete_model=False)

        data = {
            "form-TOTAL_FORMS": "2",
            "form-INITIAL_FORMS": "2",
            "form-MIN_NUM_FORMS": "0",
            "form-MAX_NUM_FORMS": "1000",
            "form-0-id": str(self.obj_a.pk),
            "form-0-field1": "Modified A",
            "form-0-polymorphic_ctype": str(ct_a.pk),
            "form-1-id": str(self.obj_b.pk),
            "form-1-field1": "Modified B",
            "form-1-field2": "Modified B2",
            "form-1-polymorphic_ctype": str(ct_b.pk),
        }

        queryset = Model2A.objects.filter(pk__in=[self.obj_a.pk, self.obj_b.pk])
        formset = FormSet(data=data, queryset=queryset)

        assert formset.is_bound
        assert formset.is_valid()
        assert formset.forms[0].instance.pk == self.obj_a.pk
        assert formset.forms[1].instance.pk == self.obj_b.pk

    def test_extra_forms_cycle_child_types(self):
        """Extra forms cycle through registered child types"""
        FormSet = polymorphic_modelformset_factory(
            model=Model2A,
            fields="__all__",
            extra=3,
            formset_children=[
                PolymorphicFormSetChild(model=Model2A),
                PolymorphicFormSetChild(model=Model2B),
            ],
        )

        formset = FormSet(queryset=Model2A.objects.none())

        # Forms cycle: A, B, A
        assert "field2" not in formset.forms[0].fields  # Model2A
        assert "field2" in formset.forms[1].fields  # Model2B
        assert "field2" not in formset.forms[2].fields  # Model2A

    def test_validation_error_missing_ctype(self):
        """ValidationError raised when polymorphic_ctype missing in bound data"""
        FormSet = polymorphic_modelformset_factory(
            model=Model2A,
            fields="__all__",
            formset_children=[PolymorphicFormSetChild(model=Model2A)],
        )

        data = {
            "form-TOTAL_FORMS": "1",
            "form-INITIAL_FORMS": "0",
            "form-MIN_NUM_FORMS": "0",
            "form-MAX_NUM_FORMS": "1000",
            "form-0-field1": "Test",
        }

        formset = FormSet(data=data, queryset=Model2A.objects.none())

        with pytest.raises(ValidationError, match="has no 'polymorphic_ctype'"):
            _ = formset.forms

    def test_unsupported_child_in_bound_data(self):
        """UnsupportedChildType when bound data has unregistered child type"""
        FormSet = polymorphic_modelformset_factory(
            model=Model2A,
            fields="__all__",
            formset_children=[PolymorphicFormSetChild(model=Model2A)],
        )

        ct_b = ContentType.objects.get_for_model(Model2B, for_concrete_model=False)
        data = {
            "form-TOTAL_FORMS": "1",
            "form-INITIAL_FORMS": "0",
            "form-MIN_NUM_FORMS": "0",
            "form-MAX_NUM_FORMS": "1000",
            "form-0-field1": "Test",
            "form-0-polymorphic_ctype": str(ct_b.pk),
        }

        formset = FormSet(data=data, queryset=Model2A.objects.none())

        with pytest.raises(UnsupportedChildType, match="is not part of the formset"):
            _ = formset.forms

    def test_unbound_with_ctype_in_initial(self):
        """Unbound formset with polymorphic_ctype in initial creates correct form"""
        FormSet = polymorphic_modelformset_factory(
            model=Model2A,
            fields="__all__",
            extra=1,
            formset_children=[
                PolymorphicFormSetChild(model=Model2A),
                PolymorphicFormSetChild(model=Model2B),
            ],
        )

        ct_b = ContentType.objects.get_for_model(Model2B, for_concrete_model=False)
        initial = [{"polymorphic_ctype": ct_b}]
        formset = FormSet(queryset=Model2A.objects.none(), initial=initial)

        # Form should be for Model2B
        assert "field2" in formset.forms[0].fields

    def test_child_form_kwargs(self):
        """child_form_kwargs passed to child form factory"""
        FormSet = polymorphic_modelformset_factory(
            model=Model2A,
            fields="__all__",
            formset_children=[PolymorphicFormSetChild(model=Model2A)],
            child_form_kwargs={"extra_exclude": ["field1"]},
        )

        formset = FormSet(queryset=Model2A.objects.none())
        assert "field1" not in formset.forms[0].fields

    def test_is_multipart_with_file_field(self):
        """is_multipart returns True when form has FileField"""

        class FileForm(forms.ModelForm):
            file = forms.FileField()

            class Meta:
                model = Model2A
                fields = ["field1"]

        FormSet = polymorphic_modelformset_factory(
            model=Model2A,
            fields=["field1"],
            formset_children=[PolymorphicFormSetChild(model=Model2A, form=FileForm)],
            extra=1,
        )
        formset = FormSet(queryset=Model2A.objects.none())

        assert formset.is_multipart()

    def test_media_aggregation(self):
        """media property aggregates all child form media"""

        class MediaForm(forms.ModelForm):
            class Media:
                js = ("test.js",)

            class Meta:
                model = Model2A
                fields = ["field1"]

        FormSet = polymorphic_modelformset_factory(
            model=Model2A,
            fields=["field1"],
            formset_children=[PolymorphicFormSetChild(model=Model2A, form=MediaForm)],
            extra=1,
        )
        formset = FormSet(queryset=Model2A.objects.none())

        assert "test.js" in str(formset.media)


class PolymorphicInlineFormSetTest(TestCase):
    """Test polymorphic inline formsets"""

    def test_inline_formset_factory(self):
        """Inline formset factory creates functional formsets"""
        InlineFormSet = polymorphic_inlineformset_factory(
            parent_model=Model2A,
            model=Model2B,
            fields="__all__",
            formset_children=[
                PolymorphicFormSetChild(model=Model2B),
                PolymorphicFormSetChild(model=Model2C),
            ],
        )

        parent = Model2A.objects.create(field1="Parent")
        formset = InlineFormSet(instance=parent)

        assert formset.instance == parent
        assert len(formset.forms) > 0

    def test_inline_with_child_form_kwargs(self):
        """Inline formset passes child_form_kwargs to children"""
        InlineFormSet = polymorphic_inlineformset_factory(
            parent_model=Model2A,
            model=Model2B,
            fields="__all__",
            formset_children=[PolymorphicFormSetChild(model=Model2B)],
            child_form_kwargs={"extra_exclude": ["field1"]},
        )

        parent = Model2A.objects.create(field1="Parent")
        formset = InlineFormSet(instance=parent)

        assert "field1" not in formset.forms[0].fields

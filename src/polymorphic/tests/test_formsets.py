"""
Tests for polymorphic formsets.
"""

import pytest
from django import forms
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ImproperlyConfigured, ValidationError
from django.test import TestCase

from polymorphic.formsets.generic import (
    GenericPolymorphicFormSetChild,
    generic_polymorphic_inlineformset_factory,
)
from polymorphic.formsets.models import (
    PolymorphicFormSetChild,
    UnsupportedChildType,
    polymorphic_inlineformset_factory,
    polymorphic_modelformset_factory,
)
from polymorphic.tests.models import (
    GenericFKParent,
    Model2A,
    Model2B,
    Model2C,
    PolymorphicTagA,
    PolymorphicTagB,
    PolymorphicTagBase,
)


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


class GenericPolymorphicFormSetChildTest(TestCase):
    """Test GenericPolymorphicFormSetChild configuration"""

    def test_content_type_property(self):
        """ContentType is cached for generic child model"""
        child = GenericPolymorphicFormSetChild(model=PolymorphicTagA)
        ct = child.content_type

        assert ct.model_class() == PolymorphicTagA
        assert child.content_type is ct  # Verify caching

    def test_ct_field_fk_field_defaults(self):
        """Default ct_field and fk_field are 'content_type' and 'object_id'"""
        child = GenericPolymorphicFormSetChild(model=PolymorphicTagA)
        assert child.ct_field == "content_type"
        assert child.fk_field == "object_id"

    def test_custom_ct_field_fk_field(self):
        """Custom ct_field and fk_field can be specified"""
        child = GenericPolymorphicFormSetChild(
            model=PolymorphicTagA, ct_field="content_type", fk_field="object_id"
        )
        assert child.ct_field == "content_type"
        assert child.fk_field == "object_id"

    def test_get_form_excludes_gfk_fields(self):
        """get_form automatically excludes the GFK ct_field and fk_field"""
        child = GenericPolymorphicFormSetChild(model=PolymorphicTagA)
        form_class = child.get_form()
        form = form_class()

        # The GFK fields should be excluded
        assert "content_type" not in form.fields
        assert "object_id" not in form.fields
        # But model-specific fields should be present
        assert "tag" in form.fields
        assert "priority" in form.fields

    def test_get_form_with_extra_exclude(self):
        """get_form with extra_exclude adds to existing excludes"""
        child = GenericPolymorphicFormSetChild(model=PolymorphicTagA, exclude=["tag"])
        form_class = child.get_form(extra_exclude=["priority"])
        form = form_class()

        assert "tag" not in form.fields
        assert "priority" not in form.fields
        # GFK fields also excluded
        assert "content_type" not in form.fields
        assert "object_id" not in form.fields

    def test_get_form_invalid_ct_field_raises(self):
        """get_form raises Exception if ct_field is not a ForeignKey to ContentType"""
        child = GenericPolymorphicFormSetChild(
            model=PolymorphicTagA, ct_field="tag", fk_field="object_id"
        )

        with pytest.raises(Exception, match="is not a ForeignKey to ContentType"):
            child.get_form()


class GenericPolymorphicInlineFormSetTest(TestCase):
    """Test generic polymorphic inline formsets"""

    def setUp(self):
        self.parent = GenericFKParent.objects.create(name="Test Parent")
        self.parent_ct = ContentType.objects.get_for_model(GenericFKParent)

    def test_factory_creates_functional_formset(self):
        """generic_polymorphic_inlineformset_factory creates functional formsets"""
        FormSet = generic_polymorphic_inlineformset_factory(
            model=PolymorphicTagBase,
            formset_children=[
                GenericPolymorphicFormSetChild(model=PolymorphicTagA),
                GenericPolymorphicFormSetChild(model=PolymorphicTagB),
            ],
        )

        formset = FormSet(instance=self.parent)

        assert formset.instance == self.parent
        assert len(formset.forms) > 0

    def test_formset_gfk_fields_excluded(self):
        """GFK fields are excluded from forms in the formset"""
        FormSet = generic_polymorphic_inlineformset_factory(
            model=PolymorphicTagBase,
            formset_children=[
                GenericPolymorphicFormSetChild(model=PolymorphicTagA),
            ],
        )

        formset = FormSet(instance=self.parent)

        # Check all forms have GFK fields excluded
        for form in formset.forms:
            assert "content_type" not in form.fields
            assert "object_id" not in form.fields

    def test_extra_forms_cycle_child_types(self):
        """Extra forms cycle through registered child types"""
        FormSet = generic_polymorphic_inlineformset_factory(
            model=PolymorphicTagBase,
            extra=3,
            formset_children=[
                GenericPolymorphicFormSetChild(model=PolymorphicTagA),
                GenericPolymorphicFormSetChild(model=PolymorphicTagB),
            ],
        )

        formset = FormSet(instance=self.parent)

        # Forms cycle: A, B, A
        assert "priority" in formset.forms[0].fields  # PolymorphicTagA
        assert "color" in formset.forms[1].fields  # PolymorphicTagB
        assert "priority" in formset.forms[2].fields  # PolymorphicTagA

    def test_bound_formset_with_existing_objects(self):
        """Bound formset processes existing polymorphic objects correctly"""
        tag_a = PolymorphicTagA.objects.create(
            tag="tag-a",
            content_type=self.parent_ct,
            object_id=self.parent.pk,
            priority=5,
        )
        tag_b = PolymorphicTagB.objects.create(
            tag="tag-b",
            content_type=self.parent_ct,
            object_id=self.parent.pk,
            color="red",
        )

        FormSet = generic_polymorphic_inlineformset_factory(
            model=PolymorphicTagBase,
            formset_children=[
                GenericPolymorphicFormSetChild(model=PolymorphicTagA),
                GenericPolymorphicFormSetChild(model=PolymorphicTagB),
            ],
        )

        ct_a = ContentType.objects.get_for_model(PolymorphicTagA, for_concrete_model=False)
        ct_b = ContentType.objects.get_for_model(PolymorphicTagB, for_concrete_model=False)

        data = {
            "tests-polymorphictagbase-content_type-object_id-TOTAL_FORMS": "2",
            "tests-polymorphictagbase-content_type-object_id-INITIAL_FORMS": "2",
            "tests-polymorphictagbase-content_type-object_id-MIN_NUM_FORMS": "0",
            "tests-polymorphictagbase-content_type-object_id-MAX_NUM_FORMS": "1000",
            "tests-polymorphictagbase-content_type-object_id-0-id": str(tag_a.pk),
            "tests-polymorphictagbase-content_type-object_id-0-tag": "tag-a-modified",
            "tests-polymorphictagbase-content_type-object_id-0-priority": "10",
            "tests-polymorphictagbase-content_type-object_id-0-polymorphic_ctype": str(ct_a.pk),
            "tests-polymorphictagbase-content_type-object_id-1-id": str(tag_b.pk),
            "tests-polymorphictagbase-content_type-object_id-1-tag": "tag-b-modified",
            "tests-polymorphictagbase-content_type-object_id-1-color": "blue",
            "tests-polymorphictagbase-content_type-object_id-1-polymorphic_ctype": str(ct_b.pk),
        }

        formset = FormSet(data=data, instance=self.parent)

        assert formset.is_bound
        assert formset.is_valid(), formset.errors
        assert formset.forms[0].instance.pk == tag_a.pk
        assert formset.forms[1].instance.pk == tag_b.pk

    def test_formset_with_child_form_kwargs(self):
        """child_form_kwargs passed to child form factory"""
        FormSet = generic_polymorphic_inlineformset_factory(
            model=PolymorphicTagBase,
            formset_children=[
                GenericPolymorphicFormSetChild(model=PolymorphicTagA),
            ],
            child_form_kwargs={"extra_exclude": ["tag"]},
        )

        formset = FormSet(instance=self.parent)
        assert "tag" not in formset.forms[0].fields

    def test_empty_forms_property(self):
        """empty_forms returns all possible empty form types"""
        FormSet = generic_polymorphic_inlineformset_factory(
            model=PolymorphicTagBase,
            formset_children=[
                GenericPolymorphicFormSetChild(model=PolymorphicTagA),
                GenericPolymorphicFormSetChild(model=PolymorphicTagB),
            ],
        )

        formset = FormSet(instance=self.parent)
        empty_forms = formset.empty_forms

        assert len(empty_forms) == 2
        # Check that different form types are represented
        form_models = {form._meta.model for form in empty_forms}
        assert PolymorphicTagA in form_models
        assert PolymorphicTagB in form_models

    def test_empty_form_raises_runtime_error(self):
        """Accessing empty_form raises RuntimeError (use empty_forms instead)"""
        FormSet = generic_polymorphic_inlineformset_factory(
            model=PolymorphicTagBase,
            formset_children=[
                GenericPolymorphicFormSetChild(model=PolymorphicTagA),
            ],
        )

        formset = FormSet(instance=self.parent)

        with pytest.raises(RuntimeError, match="use 'empty_forms'"):
            _ = formset.empty_form

    def test_unsupported_child_type_in_bound_data(self):
        """UnsupportedChildType when bound data has unregistered child type"""
        FormSet = generic_polymorphic_inlineformset_factory(
            model=PolymorphicTagBase,
            formset_children=[
                GenericPolymorphicFormSetChild(model=PolymorphicTagA),
            ],
        )

        ct_b = ContentType.objects.get_for_model(PolymorphicTagB, for_concrete_model=False)
        data = {
            "tests-polymorphictagbase-content_type-object_id-TOTAL_FORMS": "1",
            "tests-polymorphictagbase-content_type-object_id-INITIAL_FORMS": "0",
            "tests-polymorphictagbase-content_type-object_id-MIN_NUM_FORMS": "0",
            "tests-polymorphictagbase-content_type-object_id-MAX_NUM_FORMS": "1000",
            "tests-polymorphictagbase-content_type-object_id-0-tag": "test",
            "tests-polymorphictagbase-content_type-object_id-0-polymorphic_ctype": str(ct_b.pk),
        }

        formset = FormSet(data=data, instance=self.parent)

        with pytest.raises(UnsupportedChildType, match="is not part of the formset"):
            _ = formset.forms

    def test_validation_error_missing_ctype(self):
        """ValidationError raised when polymorphic_ctype missing in bound data"""
        FormSet = generic_polymorphic_inlineformset_factory(
            model=PolymorphicTagBase,
            formset_children=[
                GenericPolymorphicFormSetChild(model=PolymorphicTagA),
            ],
        )

        data = {
            "tests-polymorphictagbase-content_type-object_id-TOTAL_FORMS": "1",
            "tests-polymorphictagbase-content_type-object_id-INITIAL_FORMS": "0",
            "tests-polymorphictagbase-content_type-object_id-MIN_NUM_FORMS": "0",
            "tests-polymorphictagbase-content_type-object_id-MAX_NUM_FORMS": "1000",
            "tests-polymorphictagbase-content_type-object_id-0-tag": "test",
        }

        formset = FormSet(data=data, instance=self.parent)

        with pytest.raises(ValidationError, match="has no 'polymorphic_ctype'"):
            _ = formset.forms

    def test_is_multipart_with_file_field(self):
        """is_multipart returns True when form has FileField"""

        class FileForm(forms.ModelForm):
            file = forms.FileField()

            class Meta:
                model = PolymorphicTagA
                fields = ["tag", "priority"]

        FormSet = generic_polymorphic_inlineformset_factory(
            model=PolymorphicTagBase,
            formset_children=[
                GenericPolymorphicFormSetChild(model=PolymorphicTagA, form=FileForm),
            ],
            extra=1,
        )

        formset = FormSet(instance=self.parent)
        assert formset.is_multipart()

    def test_media_aggregation(self):
        """media property aggregates all child form media"""

        class MediaForm(forms.ModelForm):
            class Media:
                js = ("generic_test.js",)

            class Meta:
                model = PolymorphicTagA
                fields = ["tag", "priority"]

        FormSet = generic_polymorphic_inlineformset_factory(
            model=PolymorphicTagBase,
            formset_children=[
                GenericPolymorphicFormSetChild(model=PolymorphicTagA, form=MediaForm),
            ],
            extra=1,
        )

        formset = FormSet(instance=self.parent)
        assert "generic_test.js" in str(formset.media)

    def test_save_new_objects(self):
        """Formset can save new polymorphic objects via generic relation"""
        FormSet = generic_polymorphic_inlineformset_factory(
            model=PolymorphicTagBase,
            formset_children=[
                GenericPolymorphicFormSetChild(model=PolymorphicTagA),
                GenericPolymorphicFormSetChild(model=PolymorphicTagB),
            ],
        )

        ct_a = ContentType.objects.get_for_model(PolymorphicTagA, for_concrete_model=False)

        data = {
            "tests-polymorphictagbase-content_type-object_id-TOTAL_FORMS": "1",
            "tests-polymorphictagbase-content_type-object_id-INITIAL_FORMS": "0",
            "tests-polymorphictagbase-content_type-object_id-MIN_NUM_FORMS": "0",
            "tests-polymorphictagbase-content_type-object_id-MAX_NUM_FORMS": "1000",
            "tests-polymorphictagbase-content_type-object_id-0-tag": "new-tag",
            "tests-polymorphictagbase-content_type-object_id-0-priority": "99",
            "tests-polymorphictagbase-content_type-object_id-0-polymorphic_ctype": str(ct_a.pk),
        }

        formset = FormSet(data=data, instance=self.parent)
        assert formset.is_valid(), formset.errors

        saved_objects = formset.save()
        assert len(saved_objects) == 1
        assert isinstance(saved_objects[0], PolymorphicTagA)
        assert saved_objects[0].tag == "new-tag"
        assert saved_objects[0].priority == 99
        assert saved_objects[0].content_object == self.parent

"""
Tests for polymorphic templatetags.
"""

import html
import json

import pytest
from django.template import Context, Template, TemplateSyntaxError
from django.test import TestCase

from polymorphic.formsets import (
    PolymorphicFormSetChild,
    polymorphic_modelformset_factory,
)
from polymorphic.tests.models import Model2A, Model2B


def parse_json_from_template(result):
    """Parse JSON from template output, handling HTML escaping."""
    return json.loads(html.unescape(result))


class BreadcrumbScopeTagTest(TestCase):
    """Tests for the breadcrumb_scope template tag"""

    def test_breadcrumb_scope_sets_app_label(self):
        """breadcrumb_scope sets app_label from base_opts"""
        template = Template(
            "{% load polymorphic_admin_tags %}"
            "{% breadcrumb_scope base_opts %}{{ app_label }}{% endbreadcrumb_scope %}"
        )
        context = Context({"base_opts": Model2A._meta})
        result = template.render(context)

        assert result == "tests"

    def test_breadcrumb_scope_sets_opts(self):
        """breadcrumb_scope sets opts from base_opts"""
        template = Template(
            "{% load polymorphic_admin_tags %}"
            "{% breadcrumb_scope base_opts %}{{ opts.model_name }}{% endbreadcrumb_scope %}"
        )
        context = Context({"base_opts": Model2A._meta})
        result = template.render(context)

        assert result == "model2a"

    def test_breadcrumb_scope_restores_context(self):
        """breadcrumb_scope restores original context after block"""
        template = Template(
            "{% load polymorphic_admin_tags %}"
            "before:{{ app_label }}|"
            "{% breadcrumb_scope base_opts %}inside:{{ app_label }}{% endbreadcrumb_scope %}|"
            "after:{{ app_label }}"
        )
        context = Context({"base_opts": Model2A._meta, "app_label": "original"})
        result = template.render(context)

        assert result == "before:original|inside:tests|after:original"

    def test_breadcrumb_scope_with_none_base_opts(self):
        """breadcrumb_scope handles None base_opts gracefully"""
        template = Template(
            "{% load polymorphic_admin_tags %}"
            "{% breadcrumb_scope base_opts %}{{ app_label|default:'empty' }}{% endbreadcrumb_scope %}"
        )
        context = Context({"base_opts": None, "app_label": "fallback"})
        result = template.render(context)

        # When base_opts is None, original context values are preserved
        assert result == "fallback"

    def test_breadcrumb_scope_with_string_base_opts(self):
        """breadcrumb_scope handles string base_opts (doesn't set new values)"""
        template = Template(
            "{% load polymorphic_admin_tags %}"
            "{% breadcrumb_scope base_opts %}{{ app_label|default:'empty' }}{% endbreadcrumb_scope %}"
        )
        context = Context({"base_opts": "some_string", "app_label": "original"})
        result = template.render(context)

        # When base_opts is a string, original context values are preserved
        assert result == "original"

    def test_breadcrumb_scope_missing_argument_raises_error(self):
        """breadcrumb_scope raises TemplateSyntaxError without argument"""
        with pytest.raises(TemplateSyntaxError, match="expects 1 argument"):
            Template(
                "{% load polymorphic_admin_tags %}{% breadcrumb_scope %}{% endbreadcrumb_scope %}"
            )

    def test_breadcrumb_scope_too_many_arguments_raises_error(self):
        """breadcrumb_scope raises TemplateSyntaxError with too many arguments"""
        with pytest.raises(TemplateSyntaxError, match="expects 1 argument"):
            Template(
                "{% load polymorphic_admin_tags %}"
                "{% breadcrumb_scope arg1 arg2 %}{% endbreadcrumb_scope %}"
            )

    def test_breadcrumb_scope_with_variable_lookup(self):
        """breadcrumb_scope works with variable lookup"""
        template = Template(
            "{% load polymorphic_admin_tags %}"
            "{% breadcrumb_scope model_meta %}{{ opts.verbose_name }}{% endbreadcrumb_scope %}"
        )
        context = Context({"model_meta": Model2B._meta})
        result = template.render(context)

        assert "model2b" in result.lower()


class IncludeEmptyFormFilterTest(TestCase):
    """Tests for the include_empty_form filter"""

    def test_include_empty_form_with_polymorphic_formset(self):
        """include_empty_form yields forms and empty_forms for polymorphic formsets"""
        FormSet = polymorphic_modelformset_factory(
            model=Model2A,
            fields="__all__",
            extra=0,
            formset_children=[
                PolymorphicFormSetChild(model=Model2A),
                PolymorphicFormSetChild(model=Model2B),
            ],
        )

        obj = Model2A.objects.create(field1="test")
        formset = FormSet(queryset=Model2A.objects.filter(pk=obj.pk))

        template = Template(
            "{% load polymorphic_formset_tags %}"
            "{% for form in formset|include_empty_form %}{{ forloop.counter }},{% endfor %}"
        )
        context = Context({"formset": formset})
        result = template.render(context)

        # 1 existing form + 2 empty forms (one for each child type)
        assert result == "1,2,3,"

    def test_include_empty_form_with_standard_formset(self):
        """include_empty_form yields forms and single empty_form for standard formsets"""
        from django.forms import modelformset_factory

        FormSet = modelformset_factory(Model2A, fields="__all__", extra=0)
        obj = Model2A.objects.create(field1="test")
        formset = FormSet(queryset=Model2A.objects.filter(pk=obj.pk))

        template = Template(
            "{% load polymorphic_formset_tags %}"
            "{% for form in formset|include_empty_form %}{{ forloop.counter }},{% endfor %}"
        )
        context = Context({"formset": formset})
        result = template.render(context)

        # 1 existing form + 1 empty form
        assert result == "1,2,"

    def test_include_empty_form_with_empty_polymorphic_formset(self):
        """include_empty_form with no existing objects yields only empty forms"""
        FormSet = polymorphic_modelformset_factory(
            model=Model2A,
            fields="__all__",
            extra=0,
            formset_children=[
                PolymorphicFormSetChild(model=Model2A),
                PolymorphicFormSetChild(model=Model2B),
            ],
        )

        formset = FormSet(queryset=Model2A.objects.none())

        template = Template(
            "{% load polymorphic_formset_tags %}"
            "{% for form in formset|include_empty_form %}{{ forloop.counter }},{% endfor %}"
        )
        context = Context({"formset": formset})
        result = template.render(context)

        # 0 existing forms + 2 empty forms
        assert result == "1,2,"


class AsScriptOptionsFilterTest(TestCase):
    """Tests for the as_script_options filter"""

    def test_as_script_options_returns_valid_json(self):
        """as_script_options returns valid JSON"""
        FormSet = polymorphic_modelformset_factory(
            model=Model2A,
            fields="__all__",
            formset_children=[
                PolymorphicFormSetChild(model=Model2A),
            ],
        )

        formset = FormSet(queryset=Model2A.objects.none())

        template = Template("{% load polymorphic_formset_tags %}{{ formset|as_script_options }}")
        context = Context({"formset": formset})
        result = template.render(context)

        # Should be valid JSON
        options = parse_json_from_template(result)
        assert isinstance(options, dict)

    def test_as_script_options_contains_prefix(self):
        """as_script_options includes formset prefix"""
        FormSet = polymorphic_modelformset_factory(
            model=Model2A,
            fields="__all__",
            formset_children=[
                PolymorphicFormSetChild(model=Model2A),
            ],
        )

        formset = FormSet(queryset=Model2A.objects.none())

        template = Template("{% load polymorphic_formset_tags %}{{ formset|as_script_options }}")
        context = Context({"formset": formset})
        result = template.render(context)

        options = parse_json_from_template(result)
        assert "prefix" in options
        assert options["prefix"] == formset.prefix

    def test_as_script_options_contains_pk_field_name(self):
        """as_script_options includes pkFieldName"""
        FormSet = polymorphic_modelformset_factory(
            model=Model2A,
            fields="__all__",
            formset_children=[
                PolymorphicFormSetChild(model=Model2A),
            ],
        )

        formset = FormSet(queryset=Model2A.objects.none())

        template = Template("{% load polymorphic_formset_tags %}{{ formset|as_script_options }}")
        context = Context({"formset": formset})
        result = template.render(context)

        options = parse_json_from_template(result)
        assert "pkFieldName" in options
        assert options["pkFieldName"] == "id"

    def test_as_script_options_contains_add_text(self):
        """as_script_options includes addText"""
        FormSet = polymorphic_modelformset_factory(
            model=Model2A,
            fields="__all__",
            formset_children=[
                PolymorphicFormSetChild(model=Model2A),
            ],
        )

        formset = FormSet(queryset=Model2A.objects.none())

        template = Template("{% load polymorphic_formset_tags %}{{ formset|as_script_options }}")
        context = Context({"formset": formset})
        result = template.render(context)

        options = parse_json_from_template(result)
        assert "addText" in options
        assert "Add another" in options["addText"]

    def test_as_script_options_contains_show_add_button(self):
        """as_script_options includes showAddButton"""
        FormSet = polymorphic_modelformset_factory(
            model=Model2A,
            fields="__all__",
            formset_children=[
                PolymorphicFormSetChild(model=Model2A),
            ],
        )

        formset = FormSet(queryset=Model2A.objects.none())

        template = Template("{% load polymorphic_formset_tags %}{{ formset|as_script_options }}")
        context = Context({"formset": formset})
        result = template.render(context)

        options = parse_json_from_template(result)
        assert "showAddButton" in options
        assert options["showAddButton"] is True

    def test_as_script_options_contains_delete_text(self):
        """as_script_options includes deleteText"""
        FormSet = polymorphic_modelformset_factory(
            model=Model2A,
            fields="__all__",
            formset_children=[
                PolymorphicFormSetChild(model=Model2A),
            ],
        )

        formset = FormSet(queryset=Model2A.objects.none())

        template = Template("{% load polymorphic_formset_tags %}{{ formset|as_script_options }}")
        context = Context({"formset": formset})
        result = template.render(context)

        options = parse_json_from_template(result)
        assert "deleteText" in options
        assert options["deleteText"] == "Delete"

    def test_as_script_options_polymorphic_contains_child_types(self):
        """as_script_options includes childTypes for polymorphic formsets"""
        FormSet = polymorphic_modelformset_factory(
            model=Model2A,
            fields="__all__",
            formset_children=[
                PolymorphicFormSetChild(model=Model2A),
                PolymorphicFormSetChild(model=Model2B),
            ],
        )

        formset = FormSet(queryset=Model2A.objects.none())

        template = Template("{% load polymorphic_formset_tags %}{{ formset|as_script_options }}")
        context = Context({"formset": formset})
        result = template.render(context)

        options = parse_json_from_template(result)
        assert "childTypes" in options
        assert len(options["childTypes"]) == 2

        child_type_names = [ct["type"] for ct in options["childTypes"]]
        assert "model2a" in child_type_names
        assert "model2b" in child_type_names

    def test_as_script_options_child_types_have_name_and_type(self):
        """as_script_options childTypes have name and type keys"""
        FormSet = polymorphic_modelformset_factory(
            model=Model2A,
            fields="__all__",
            formset_children=[
                PolymorphicFormSetChild(model=Model2A),
            ],
        )

        formset = FormSet(queryset=Model2A.objects.none())

        template = Template("{% load polymorphic_formset_tags %}{{ formset|as_script_options }}")
        context = Context({"formset": formset})
        result = template.render(context)

        options = parse_json_from_template(result)
        child_type = options["childTypes"][0]
        assert "name" in child_type
        assert "type" in child_type

    def test_as_script_options_standard_formset_no_child_types(self):
        """as_script_options for standard formsets doesn't include childTypes"""
        from django.forms import modelformset_factory

        FormSet = modelformset_factory(Model2A, fields="__all__")
        formset = FormSet(queryset=Model2A.objects.none())

        template = Template("{% load polymorphic_formset_tags %}{{ formset|as_script_options }}")
        context = Context({"formset": formset})
        result = template.render(context)

        options = parse_json_from_template(result)
        assert "childTypes" not in options

    def test_as_script_options_custom_verbose_name(self):
        """as_script_options uses custom verbose_name from formset"""
        FormSet = polymorphic_modelformset_factory(
            model=Model2A,
            fields="__all__",
            formset_children=[
                PolymorphicFormSetChild(model=Model2A),
            ],
        )

        formset = FormSet(queryset=Model2A.objects.none())
        formset.verbose_name = "Custom Name"

        template = Template("{% load polymorphic_formset_tags %}{{ formset|as_script_options }}")
        context = Context({"formset": formset})
        result = template.render(context)

        options = parse_json_from_template(result)
        assert "Custom Name" in options["addText"]

    def test_as_script_options_custom_add_text(self):
        """as_script_options uses custom add_text from formset"""
        FormSet = polymorphic_modelformset_factory(
            model=Model2A,
            fields="__all__",
            formset_children=[
                PolymorphicFormSetChild(model=Model2A),
            ],
        )

        formset = FormSet(queryset=Model2A.objects.none())
        formset.add_text = "Custom Add Button"

        template = Template("{% load polymorphic_formset_tags %}{{ formset|as_script_options }}")
        context = Context({"formset": formset})
        result = template.render(context)

        options = parse_json_from_template(result)
        assert options["addText"] == "Custom Add Button"

    def test_as_script_options_custom_show_add_button(self):
        """as_script_options uses custom show_add_button from formset"""
        FormSet = polymorphic_modelformset_factory(
            model=Model2A,
            fields="__all__",
            formset_children=[
                PolymorphicFormSetChild(model=Model2A),
            ],
        )

        formset = FormSet(queryset=Model2A.objects.none())
        formset.show_add_button = False

        template = Template("{% load polymorphic_formset_tags %}{{ formset|as_script_options }}")
        context = Context({"formset": formset})
        result = template.render(context)

        options = parse_json_from_template(result)
        assert options["showAddButton"] is False


class AsFormTypeFilterTest(TestCase):
    """Tests for the as_form_type filter"""

    def test_as_form_type_returns_model_name(self):
        """as_form_type returns the model name from a form"""
        FormSet = polymorphic_modelformset_factory(
            model=Model2A,
            fields="__all__",
            formset_children=[
                PolymorphicFormSetChild(model=Model2A),
                PolymorphicFormSetChild(model=Model2B),
            ],
        )

        formset = FormSet(queryset=Model2A.objects.none())
        # Get one of the empty forms
        form = formset.empty_forms[0]

        template = Template("{% load polymorphic_formset_tags %}{{ form|as_form_type }}")
        context = Context({"form": form})
        result = template.render(context)

        assert result in ["model2a", "model2b"]

    def test_as_form_type_with_model2a_form(self):
        """as_form_type returns 'model2a' for Model2A form"""
        FormSet = polymorphic_modelformset_factory(
            model=Model2A,
            fields="__all__",
            formset_children=[
                PolymorphicFormSetChild(model=Model2A),
            ],
        )

        formset = FormSet(queryset=Model2A.objects.none())
        form = formset.empty_forms[0]

        template = Template("{% load polymorphic_formset_tags %}{{ form|as_form_type }}")
        context = Context({"form": form})
        result = template.render(context)

        assert result == "model2a"

    def test_as_form_type_with_model2b_form(self):
        """as_form_type returns 'model2b' for Model2B form"""
        FormSet = polymorphic_modelformset_factory(
            model=Model2A,
            fields="__all__",
            formset_children=[
                PolymorphicFormSetChild(model=Model2B),
            ],
        )

        formset = FormSet(queryset=Model2A.objects.none())
        form = formset.empty_forms[0]

        template = Template("{% load polymorphic_formset_tags %}{{ form|as_form_type }}")
        context = Context({"form": form})
        result = template.render(context)

        assert result == "model2b"


class AsModelNameFilterTest(TestCase):
    """Tests for the as_model_name filter"""

    def test_as_model_name_with_model_class(self):
        """as_model_name returns model name from a model class"""
        template = Template("{% load polymorphic_formset_tags %}{{ model|as_model_name }}")
        context = Context({"model": Model2A})
        result = template.render(context)

        assert result == "model2a"

    def test_as_model_name_with_model_instance(self):
        """as_model_name returns model name from a model instance"""
        obj = Model2A(field1="test")

        template = Template("{% load polymorphic_formset_tags %}{{ model|as_model_name }}")
        context = Context({"model": obj})
        result = template.render(context)

        assert result == "model2a"

    def test_as_model_name_with_child_model(self):
        """as_model_name returns correct name for child model"""
        template = Template("{% load polymorphic_formset_tags %}{{ model|as_model_name }}")
        context = Context({"model": Model2B})
        result = template.render(context)

        assert result == "model2b"

    def test_as_model_name_with_child_model_instance(self):
        """as_model_name returns correct name for child model instance"""
        obj = Model2B(field1="test", field2="test2")

        template = Template("{% load polymorphic_formset_tags %}{{ model|as_model_name }}")
        context = Context({"model": obj})
        result = template.render(context)

        assert result == "model2b"

    def test_as_model_name_in_loop(self):
        """as_model_name works correctly in a loop over models"""
        template = Template(
            "{% load polymorphic_formset_tags %}"
            "{% for model in models %}{{ model|as_model_name }},{% endfor %}"
        )
        context = Context({"models": [Model2A, Model2B]})
        result = template.render(context)

        assert result == "model2a,model2b,"

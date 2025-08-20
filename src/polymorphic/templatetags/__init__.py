"""
Template tags for polymorphic


The ``polymorphic_formset_tags`` Library
----------------------------------------

.. versionadded:: 1.1

To render formsets in the frontend, the ``polymorphic_tags`` provides extra
filters to implement HTML rendering of polymorphic formsets.

The following filters are provided;

* ``{{ formset|as_script_options }}`` render the ``data-options`` for a JavaScript formset library.
* ``{{ formset|include_empty_form }}`` provide the placeholder form for an add button.
* ``{{ form|as_form_type }}`` return the model name that the form instance uses.
* ``{{ model|as_model_name }}`` performs the same, for a model class or instance.

.. code-block:: html+django

    {% load i18n polymorphic_formset_tags %}

    <div class="inline-group" id="{{ formset.prefix }}-group" data-options="{{ formset|as_script_options }}">
        {% block add_button %}
            {% if formset.show_add_button|default_if_none:'1' %}
                {% if formset.empty_forms %}
                    {# django-polymorphic formset (e.g. PolymorphicInlineFormSetView) #}
                    <div class="btn-group" role="group">
                      {% for model in formset.child_forms %}
                          <a type="button" data-type="{{ model|as_model_name }}" class="js-add-form btn btn-default">{% glyphicon 'plus' %} {{ model|as_verbose_name }}</a>
                      {% endfor %}
                    </div>
                {% else %}
                    <a class="btn btn-default js-add-form">{% trans "Add" %}</a>
                {% endif %}
            {% endif %}
        {% endblock %}

        {{ formset.management_form }}

        {% for form in formset|include_empty_form %}
          {% block formset_form_wrapper %}
            <div id="{{ form.prefix }}" data-inline-type="{{ form|as_form_type|lower }}" class="inline-related{% if '__prefix__' in form.prefix %} empty-form{% endif %}">
                {{ form.non_field_errors }}

                {# Add the 'pk' field that is not mentioned in crispy #}
                {% for field in form.hidden_fields %}
                  {{ field }}
                {% endfor %}

                {% block formset_form %}
                    {% crispy form %}
                {% endblock %}
            </div>
          {% endblock %}
        {% endfor %}
    </div>


The ``polymorphic_admin_tags`` Library
--------------------------------------

The ``{% breadcrumb_scope ... %}`` tag makes sure the ``{{ opts }}`` and ``{{ app_label }}``
values are temporary based on the provided ``{{ base_opts }}``.
This allows fixing the breadcrumb in admin templates:

.. code-block:: html+django

    {% extends "admin/change_form.html" %}
    {% load polymorphic_admin_tags %}

    {% block breadcrumbs %}
      {% breadcrumb_scope base_opts %}{{ block.super }}{% endbreadcrumb_scope %}
    {% endblock %}

"""

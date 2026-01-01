.. _views:

Class Based Views
=================

.. versionadded:: 1.4

While :pypi:`django-polymorphic` provides full admin integration, you might want to build front-end views that allow users to create polymorphic objects.
Since a single URL cannot easily handle different form fields for different models, the best approach is a two-step process:

1.  **Step 1:** Let the user choose the desired type.
2.  **Step 2:** Display the form for that specific type.

This is similar to how the Django admin works (it redirects to a URL with ``?ct_id=...``).


Step 1: Selecting the Type
--------------------------

You can use the :class:`~polymorphic.admin.forms.PolymorphicModelChoiceForm` to display a list of available types.
This form is also used by the admin interface.

.. code-block:: python

    from django.shortcuts import render, redirect
    from django.views.generic import FormView
    from polymorphic.admin.forms import PolymorphicModelChoiceForm
    from .models import Project, ArtProject, ResearchProject

    class ProjectTypeSelectView(FormView):
        form_class = PolymorphicModelChoiceForm
        template_name = "project_type_select.html"

        def get_form_kwargs(self):
            kwargs = super().get_form_kwargs()
            # Tell the form which base model to use:
            kwargs['initial'] = {'ct_id': self.request.GET.get('ct_id')}
            return kwargs

        def form_valid(self, form):
            # Cleaned data contains the chosen ContentType
            ct = form.cleaned_data['ct_id']
            # Redirect to the creation view, passing the content type ID
            return redirect(f'project-create/?ct_id={ct.id}')

        def get_context_data(self, **kwargs):
            context = super().get_context_data(**kwargs)
            # You might want to filter the choices to only those allowed:
            # context['form'].fields['ct_id'].queryset = ...
            return context


Step 2: Displaying the Form
---------------------------

The creation view needs to dynamically select the correct form class based on the chosen content type.

.. code-block:: python

    from django.contrib.contenttypes.models import ContentType
    from django.views.generic import CreateView
    from .models import Project

    class ProjectCreateView(CreateView):
        model = Project
        template_name = "project_form.html"
        # success_url = ...

        def get_form_class(self):
            # 1. Get the requested content type
            ct_id = self.request.GET.get('ct_id')
            if not ct_id:
                # Fallback or redirect to selection view
                return super().get_form_class()

            # 2. Get the model class
            ct = ContentType.objects.get_for_id(ct_id)
            model_class = ct.model_class()

            # 3. Create a form for this model
            # You can also use a factory or a dict mapping if you have custom forms
            from django import forms
            class SpecificForm(forms.ModelForm):
                class Meta:
                    model = model_class
                    fields = '__all__'  # Or specify fields

            return SpecificForm

        def get_context_data(self, **kwargs):
            context = super().get_context_data(**kwargs)
            # Pass the ct_id to the template so it can be preserved in the form action
            context['ct_id'] = self.request.GET.get('ct_id')
            return context


In your template ``project_form.html``, make sure to preserve the ``ct_id``:

.. code-block:: html

    <form method="post" action=".?ct_id={{ ct_id }}">
        {% csrf_token %}
        {{ form.as_p }}
        <button type="submit">Save</button>
    </form>


Using ``extra_views``
---------------------

If you are using :pypi:`django-extra-views`, :pypi:`django-polymorphic` provides mixins to help with formsets.
See :mod:`polymorphic.contrib.extra_views` for more details.

from django.apps import apps
from django.shortcuts import redirect
from django.urls import reverse
from django.views.generic import FormView, CreateView
from .models import Project, ArtProject, ResearchProject

from django import forms
from django.utils.translation import gettext_lazy as _


class ProjectTypeChoiceForm(forms.Form):
    model_type = forms.ChoiceField(
        label=_("Project Type"),
        widget=forms.RadioSelect(attrs={"class": "radiolist"}),
    )


class ProjectTypeSelectView(FormView):
    form_class = ProjectTypeChoiceForm
    template_name = "project_type_select.html"

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        # Build choices using model labels: [(model_label, verbose_name), ...]
        choices = [
            (model._meta.label, model._meta.verbose_name)
            for model in [ArtProject, ResearchProject]
        ]
        kwargs["initial"] = {"model_type": choices[0][0] if choices else None}
        return kwargs

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        # Populate the choices for the form using model labels
        choices = [
            (model._meta.label, model._meta.verbose_name)
            for model in [ArtProject, ResearchProject]
        ]
        form.fields["model_type"].choices = choices
        return form

    def form_valid(self, form):
        model_label = form.cleaned_data["model_type"]
        return redirect(f"{reverse('project-create')}?model={model_label}")


class ProjectCreateView(CreateView):
    model = Project
    template_name = "project_form.html"

    def get_success_url(self):
        return reverse("project-select")

    def get_form_class(self):
        # Get the requested model label from query parameter
        model_label = self.request.GET.get("model")
        if not model_label:
            # Fallback or redirect to selection view
            return super().get_form_class()

        # Get the model class using the app registry
        model_class = apps.get_model(model_label)

        # Create a form for this model
        # You can also use a factory or a dict mapping if you have custom forms
        class SpecificForm(forms.ModelForm):
            class Meta:
                model = model_class
                fields = "__all__"  # Or specify fields

        return SpecificForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Pass the model label to the template so it can be preserved
        # in the form action
        context["model_label"] = self.request.GET.get("model")
        return context

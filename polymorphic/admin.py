"""
ModelAdmin code to display polymorphic models.
"""
from django.contrib import admin
from django.contrib.admin.helpers import AdminForm, AdminErrorList
from django.contrib.admin.widgets import AdminRadioSelect
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import PermissionDenied, ImproperlyConfigured
from django.core.urlresolvers import resolve
from django.forms import Form, ChoiceField
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from django.utils.encoding import force_text
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _


__all__ = (
    'PolymorphicModelChoiceForm', 'PolymorphicChildModelFilter',
    'PolymorphicParentModelAdmin', 'PolymorphicChildModelAdmin',
)


class PolymorphicModelChoiceForm(Form):
    """
    The default form for the ``add_type_form``. Can be overwritten and replaced.
    """
    #: Define the label for the radiofield
    type_label = _("Type")

    ct_id = ChoiceField(label=type_label, widget=AdminRadioSelect(attrs={'class': 'radiolist'}))

    def __init__(self, *args, **kwargs):
        # Allow to easily redefine the label (a commonly expected usecase)
        super(PolymorphicModelChoiceForm, self).__init__(*args, **kwargs)
        self.fields['ct_id'].label = self.type_label


class PolymorphicChildModelFilter(admin.SimpleListFilter):
    """
    An admin list filter for the PolymorphicParentModelAdmin which enables
    filtering by its child models.
    """
    title = _('Content type')
    parameter_name = 'polymorphic_ctype'

    def lookups(self, request, model_admin):
        try:
            return model_admin.get_child_type_choices()
        except AttributeError:  # Happens when model_admin is of a child model.
            return ()

    def queryset(self, request, queryset):
        try:
            value = int(self.value())
        except TypeError:
            value = None
        if value:
            # ensure the content type is allowed
            for choice_value, _ in self.lookup_choices:
                if choice_value == value:
                    return queryset.filter(polymorphic_ctype_id=choice_value)
            raise PermissionDenied(
                'Invalid ContentType "{0}". It must be registered as child model.'.format(value))
        return queryset


class PolymorphicParentModelAdmin(admin.ModelAdmin):
    """
    A admin interface that can displays different change/delete pages, depending on the polymorphic model.
    To use this class, two variables need to be defined:

    * :attr:`base_model` should
    * :attr:`child_models` should be an iterable of Model

    Alternatively, the following methods can be implemented:

    * :func:`get_child_models` should return an iterable of Model
    * optionally, :func:`get_child_type_choices` can be overwritten to refine the choices for the add dialog.

    This class needs to be inherited by the model admin base class that is registered in the site.
    """

    #: The base model that the class uses
    base_model = None

    #: The child models that should be displayed
    child_models = None

    #: Whether the list should be polymorphic too, leave to ``False`` to optimize
    polymorphic_list = False

    add_type_template = None
    add_type_form = PolymorphicModelChoiceForm

    def __init__(self, model, admin_site, *args, **kwargs):
        super(PolymorphicParentModelAdmin, self).__init__(model, admin_site, *args, **kwargs)

    def get_child_models(self):
        """
        Return the derived model classes which this admin should handle.
        This should return a list of tuples, exactly like :attr:`child_models` is.

        The model classes can be retrieved as ``base_model.__subclasses__()``,
        a setting in a config file, or a query of a plugin registration system at your option
        """
        if self.child_models is None:
            raise NotImplementedError("Implement get_child_models() or child_models")

        return self.child_models

    def get_child_type_choices(self):
        """
        Return a list of polymorphic types which can be added.
        """
        choices = []
        for model in self.get_child_models():
            ct = ContentType.objects.get_for_model(model, for_concrete_model=False)
            choices.append((ct.id, model._meta.verbose_name))
        return choices

    def _get_real_admin(self, object_id):
        ct_id = self.model.objects.non_polymorphic().values_list(
            'polymorphic_ctype', flat=True).get(pk=object_id)
        return self._get_real_admin_by_ct(ct_id)

    def _get_real_admin_by_ct(self, ct_id):
        try:
            ct = ContentType.objects.get_for_id(ct_id)
        except ContentType.DoesNotExist as e:
            raise Http404(e)   # Handle invalid GET parameters

        model_class = ct.model_class()
        if not model_class:
            raise Http404("No model found for '{0}.{1}'.".format(*ct.natural_key()))  # Handle model deletion

        return self._get_real_admin_by_model(model_class)

    def _get_real_admin_by_model(self, model_class):
        # In case of a ?ct_id=### parameter, the view is already checked for permissions.
        # Hence, make sure this is a derived object, or risk exposing other admin interfaces.
        if model_class not in self.child_models:
            raise PermissionDenied("Invalid model '{0}', it must be registered as child model.".format(model_class))

        try:
            # HACK: the only way to get the instance of an model admin,
            # is to read the registry of the AdminSite.
            return self.admin_site._registry[model_class]
        except KeyError:
            raise ImproperlyConfigured("No child admin site was registered for a '{0}' model.".format(model_class))

    def queryset(self, request):
        # optimize the list display.
        qs = super(PolymorphicParentModelAdmin, self).queryset(request)
        if not self.polymorphic_list:
            qs = qs.non_polymorphic()
        return qs

    def add_view(self, request, form_url='', extra_context=None):
        """Redirect the add view to the real admin."""
        ct_id = int(request.GET.get('ct_id', 0))
        if not ct_id:
            # Display choices
            return self.add_type_view(request)
        real_admin = self._get_real_admin_by_ct(ct_id)
        return real_admin.add_view(request, form_url, extra_context)

    def change_view(self, request, object_id, *args, **kwargs):
        """Redirect the change view to the real admin."""
        # between Django 1.3 and 1.4 this method signature differs. Hence the *args, **kwargs
        real_admin = self._get_real_admin(object_id)
        return real_admin.change_view(request, object_id, *args, **kwargs)

    def delete_view(self, request, object_id, extra_context=None):
        """Redirect the delete view to the real admin."""
        real_admin = self._get_real_admin(object_id)
        return real_admin.delete_view(request, object_id, extra_context)

    def add_type_view(self, request, form_url=''):
        """
        Display a choice form to select which page type to add.
        """
        if not self.has_add_permission(request):
            raise PermissionDenied

        extra_qs = ''
        if request.META['QUERY_STRING']:
            extra_qs = '&' + request.META['QUERY_STRING']

        choices = self.get_child_type_choices()
        if len(choices) == 1:
            return HttpResponseRedirect('?ct_id={0}{1}'.format(choices[0][0], extra_qs))

        # Create form
        form = self.add_type_form(
            data=request.POST if request.method == 'POST' else None,
            initial={'ct_id': choices[0][0]}
        )
        form.fields['ct_id'].choices = choices

        if form.is_valid():
            return HttpResponseRedirect('?ct_id={0}{1}'.format(form.cleaned_data['ct_id'], extra_qs))

        # Wrap in all admin layout
        fieldsets = ((None, {'fields': ('ct_id',)}),)
        adminForm = AdminForm(form, fieldsets, {}, model_admin=self)
        media = self.media + adminForm.media
        opts = self.model._meta

        context = {
            'title': _('Add %s') % force_text(opts.verbose_name),
            'adminform': adminForm,
            'is_popup': "_popup" in request.REQUEST,
            'media': mark_safe(media),
            'errors': AdminErrorList(form, ()),
            'app_label': opts.app_label,
        }
        return self.render_add_type_form(request, context, form_url)

    def render_add_type_form(self, request, context, form_url=''):
        """
        Render the page type choice form.
        """
        opts = self.model._meta
        app_label = opts.app_label
        context.update({
            'has_change_permission': self.has_change_permission(request),
            'form_url': mark_safe(form_url),
            'opts': opts,
            'add': True,
            'save_on_top': self.save_on_top,
        })
        if hasattr(self.admin_site, 'root_path'):
            context['root_path'] = self.admin_site.root_path  # Django < 1.4
        context_instance = RequestContext(request, current_app=self.admin_site.name)
        return render_to_response(self.add_type_template or [
            "admin/%s/%s/add_type_form.html" % (app_label, opts.object_name.lower()),
            "admin/%s/add_type_form.html" % app_label,
            "admin/polymorphic/add_type_form.html",  # added default here
            "admin/add_type_form.html"
        ], context, context_instance=context_instance)

    @property
    def change_list_template(self):
        opts = self.model._meta
        app_label = opts.app_label

        # Pass the base options
        base_opts = self.base_model._meta
        base_app_label = base_opts.app_label

        return [
            "admin/%s/%s/change_list.html" % (app_label, opts.object_name.lower()),
            "admin/%s/change_list.html" % app_label,
            # Added base class:
            "admin/%s/%s/change_list.html" % (base_app_label, base_opts.object_name.lower()),
            "admin/%s/change_list.html" % base_app_label,
            "admin/change_list.html"
        ]


class PolymorphicChildModelAdmin(admin.ModelAdmin):
    """
    The *optional* base class for the admin interface of derived models.

    This base class defines some convenience behavior for the admin interface:

    * It corrects the breadcrumbs in the admin pages.
    * It adds the base model to the template lookup paths.

    The ``base_model`` attribute must be set.
    """
    base_model = None

    def get_model_perms(self, request):
        match = resolve(request.path)
        if match.app_name == 'admin' and match.url_name in ('index', 'app_list'):
            return {'add': False, 'change': False, 'delete': False}
        return super(PolymorphicChildModelAdmin, self).get_model_perms(request)

    @property
    def change_form_template(self):
        opts = self.model._meta
        app_label = opts.app_label

        # Pass the base options
        base_opts = self.base_model._meta
        base_app_label = base_opts.app_label

        return [
            "admin/%s/%s/change_form.html" % (app_label, opts.object_name.lower()),
            "admin/%s/change_form.html" % app_label,
            # Added:
            "admin/%s/%s/change_form.html" % (base_app_label, base_opts.object_name.lower()),
            "admin/%s/change_form.html" % base_app_label,
            "admin/polymorphic/change_form.html",
            "admin/change_form.html"
        ]

    @property
    def delete_confirmation_template(self):
        opts = self.model._meta
        app_label = opts.app_label

        # Pass the base options
        base_opts = self.base_model._meta
        base_app_label = base_opts.app_label

        return [
            "admin/%s/%s/delete_confirmation.html" % (app_label, opts.object_name.lower()),
            "admin/%s/delete_confirmation.html" % app_label,
            # Added:
            "admin/%s/%s/delete_confirmation.html" % (base_app_label, base_opts.object_name.lower()),
            "admin/%s/delete_confirmation.html" % base_app_label,
            "admin/polymorphic/delete_confirmation.html",
            "admin/delete_confirmation.html"
        ]

    def render_change_form(self, request, context, add=False, change=False,
                           form_url='', obj=None):
        context['base_opts'] = self.base_model._meta
        return super(PolymorphicChildModelAdmin, self).render_change_form(
            request, context, add=add, change=change, form_url=form_url, obj=obj)

    def delete_view(self, request, object_id, context=None):
        extra_context = {'base_opts': self.base_model._meta}
        return super(PolymorphicChildModelAdmin, self).delete_view(
            request, object_id, extra_context)

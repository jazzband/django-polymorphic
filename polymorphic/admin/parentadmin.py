"""
The parent admin displays the list view of the base model.
"""
import sys
import warnings

import django
from django.conf.urls import url
from django.contrib import admin
from django.contrib.admin.helpers import AdminErrorList, AdminForm
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import PermissionDenied
from django.core.urlresolvers import RegexURLResolver
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from django.utils.encoding import force_text
from django.utils.http import urlencode
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _

from .forms import PolymorphicModelChoiceForm

try:
    # Django 1.6 implements this
    from django.contrib.admin.templatetags.admin_urls import add_preserved_filters
except ImportError:
    def add_preserved_filters(context, form_url):
        return form_url

if sys.version_info[0] >= 3:
    long = int


class RegistrationClosed(RuntimeError):
    "The admin model can't be registered anymore at this point."
    pass


class ChildAdminNotRegistered(RuntimeError):
    "The admin site for the model is not registered."
    pass


class PolymorphicParentModelAdmin(admin.ModelAdmin):
    """
    A admin interface that can displays different change/delete pages, depending on the polymorphic model.
    To use this class, two variables need to be defined:

    * :attr:`base_model` should
    * :attr:`child_models` should be a list of (Model, Admin) tuples

    Alternatively, the following methods can be implemented:

    * :func:`get_child_models` should return a list of (Model, ModelAdmin) tuples
    * optionally, :func:`get_child_type_choices` can be overwritten to refine the choices for the add dialog.

    This class needs to be inherited by the model admin base class that is registered in the site.
    The derived models should *not* register the ModelAdmin, but instead it should be returned by :func:`get_child_models`.
    """

    #: The base model that the class uses
    base_model = None

    #: The child models that should be displayed
    child_models = None

    #: Whether the list should be polymorphic too, leave to ``False`` to optimize
    polymorphic_list = False

    add_type_template = None
    add_type_form = PolymorphicModelChoiceForm

    #: The regular expression to filter the primary key in the URL.
    #: This accepts only numbers as defensive measure against catch-all URLs.
    #: If your primary key consists of string values, update this regular expression.
    pk_regex = '(\d+|__fk__)'

    def __init__(self, model, admin_site, *args, **kwargs):
        super(PolymorphicParentModelAdmin, self).__init__(model, admin_site, *args, **kwargs)
        self._is_setup = False

    def _lazy_setup(self):
        if self._is_setup:
            return

        # By not having this in __init__() there is less stress on import dependencies as well,
        # considering an advanced use cases where a plugin system scans for the child models.
        child_models = self.get_child_models()
        # Check if get_child_models() returns an iterable of models (new format) or an iterable
        # of (Model, Admin) (legacy format). When iterable is empty, assume the new format.
        self._compat_mode = len(child_models) and isinstance(child_models[0], (list, tuple))
        if not self._compat_mode:
            self._child_models = child_models
            self._child_admin_site = self.admin_site
            self._is_setup = True
            return

        # Continue only if in compatibility mode
        warnings.warn("Using tuples of (Model, ModelAdmin) in PolymorphicParentModelAdmin.child_models is "
                      "deprecated; instead child_models should be iterable of child models eg. "
                      "(Model1, Model2, ..) and child admins should be registered to default admin site",
                      DeprecationWarning)
        self._child_admin_site = self.admin_site.__class__(name=self.admin_site.name)
        self._child_admin_site.get_app_list = lambda request: ()  # HACK: workaround for Django 1.9

        for Model, Admin in child_models:
            self.register_child(Model, Admin)
        self._child_models = dict(child_models)

        # This is needed to deal with the improved ForeignKeyRawIdWidget in Django 1.4 and perhaps other widgets too.
        # The ForeignKeyRawIdWidget checks whether the referenced model is registered in the admin, otherwise it displays itself as a textfield.
        # As simple solution, just make sure all parent admin models are also know in the child admin site.
        # This should be done after all parent models are registered off course.
        complete_registry = self.admin_site._registry.copy()
        complete_registry.update(self._child_admin_site._registry)

        self._child_admin_site._registry = complete_registry
        self._is_setup = True

    def register_child(self, model, model_admin):
        """
        Register a model with admin to display.
        """
        # After the get_urls() is called, the URLs of the child model can't be exposed anymore to the Django URLconf,
        # which also means that a "Save and continue editing" button won't work.
        if self._is_setup:
            raise RegistrationClosed("The admin model can't be registered anymore at this point.")

        if not issubclass(model, self.base_model):
            raise TypeError("{0} should be a subclass of {1}".format(model.__name__, self.base_model.__name__))
        if not issubclass(model_admin, admin.ModelAdmin):
            raise TypeError("{0} should be a subclass of {1}".format(model_admin.__name__, admin.ModelAdmin.__name__))

        self._child_admin_site.register(model, model_admin)

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

    def get_child_type_choices(self, request, action):
        """
        Return a list of polymorphic types for which the user has the permission to perform the given action.
        """
        self._lazy_setup()
        choices = []
        for child_model_desc in self.get_child_models():
            if self._compat_mode:
                model = child_model_desc[0]
            else:
                model = child_model_desc
            perm_function_name = 'has_{0}_permission'.format(action)
            model_admin = self._get_real_admin_by_model(model)
            perm_function = getattr(model_admin, perm_function_name)
            if not perm_function(request):
                continue
            ct = ContentType.objects.get_for_model(model, for_concrete_model=False)
            choices.append((ct.id, model._meta.verbose_name))
        return choices

    def _get_real_admin(self, object_id, super_if_self=True):
        try:
            obj = self.model.objects.non_polymorphic() \
                .values('polymorphic_ctype').get(pk=object_id)
        except self.model.DoesNotExist:
            raise Http404
        return self._get_real_admin_by_ct(obj['polymorphic_ctype'], super_if_self=super_if_self)

    def _get_real_admin_by_ct(self, ct_id, super_if_self=True):
        try:
            ct = ContentType.objects.get_for_id(ct_id)
        except ContentType.DoesNotExist as e:
            raise Http404(e)   # Handle invalid GET parameters

        model_class = ct.model_class()
        if not model_class:
            raise Http404("No model found for '{0}.{1}'.".format(*ct.natural_key()))  # Handle model deletion

        return self._get_real_admin_by_model(model_class, super_if_self=super_if_self)

    def _get_real_admin_by_model(self, model_class, super_if_self=True):
        # In case of a ?ct_id=### parameter, the view is already checked for permissions.
        # Hence, make sure this is a derived object, or risk exposing other admin interfaces.
        if model_class not in self._child_models:
            raise PermissionDenied("Invalid model '{0}', it must be registered as child model.".format(model_class))

        try:
            # HACK: the only way to get the instance of an model admin,
            # is to read the registry of the AdminSite.
            real_admin = self._child_admin_site._registry[model_class]
        except KeyError:
            raise ChildAdminNotRegistered("No child admin site was registered for a '{0}' model.".format(model_class))

        if super_if_self and real_admin is self:
            return super(PolymorphicParentModelAdmin, self)
        else:
            return real_admin

    def get_queryset(self, request):
        # optimize the list display.
        qs = super(PolymorphicParentModelAdmin, self).get_queryset(request)
        if not self.polymorphic_list:
            qs = qs.non_polymorphic()
        return qs

    # For Django 1.5:
    def queryset(self, request):
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
        else:
            real_admin = self._get_real_admin_by_ct(ct_id)
            # rebuild form_url, otherwise libraries below will override it.
            form_url = add_preserved_filters({
                'preserved_filters': urlencode({'ct_id': ct_id}),
                'opts': self.model._meta},
                form_url
            )
            return real_admin.add_view(request, form_url, extra_context)

    def change_view(self, request, object_id, *args, **kwargs):
        """Redirect the change view to the real admin."""
        real_admin = self._get_real_admin(object_id)
        return real_admin.change_view(request, object_id, *args, **kwargs)

    if django.VERSION >= (1, 7):
        def changeform_view(self, request, object_id=None, *args, **kwargs):
            # The `changeform_view` is available as of Django 1.7, combining the add_view and change_view.
            # As it's directly called by django-reversion, this method is also overwritten to make sure it
            # also redirects to the child admin.
            if object_id:
                real_admin = self._get_real_admin(object_id)
                return real_admin.changeform_view(request, object_id, *args, **kwargs)
            else:
                # Add view. As it should already be handled via `add_view`, this means something custom is done here!
                return super(PolymorphicParentModelAdmin, self).changeform_view(request, object_id, *args, **kwargs)

    def history_view(self, request, object_id, extra_context=None):
        """Redirect the history view to the real admin."""
        real_admin = self._get_real_admin(object_id)
        return real_admin.history_view(request, object_id, extra_context=extra_context)

    def delete_view(self, request, object_id, extra_context=None):
        """Redirect the delete view to the real admin."""
        real_admin = self._get_real_admin(object_id)
        return real_admin.delete_view(request, object_id, extra_context)

    def get_preserved_filters(self, request):
        if '_changelist_filters' in request.GET:
            request.GET = request.GET.copy()
            filters = request.GET.get('_changelist_filters')
            f = filters.split("&")
            for x in f:
                c = x.split('=')
                request.GET[c[0]] = c[1]
            del request.GET['_changelist_filters']
        return super(PolymorphicParentModelAdmin, self).get_preserved_filters(request)

    def get_urls(self):
        """
        Expose the custom URLs for the subclasses and the URL resolver.
        """
        urls = super(PolymorphicParentModelAdmin, self).get_urls()

        # At this point. all admin code needs to be known.
        self._lazy_setup()

        # Continue only if in compatibility mode
        if not self._compat_mode:
            return urls

        info = _get_opt(self.model)

        # Patch the change view URL so it's not a big catch-all; allowing all
        # custom URLs to be added to the end. This is done by adding '/$' to the
        # end of the regex.  The url needs to be recreated, patching url.regex
        # is not an option Django 1.4's LocaleRegexProvider changed it.
        if django.VERSION < (1, 9):
            # On Django 1.9, the change view URL has been changed from
            # /<app>/<model>/<pk>/ to /<app>/<model>/<pk>/change/, which is
            # why we can skip this workaround for Django >= 1.9.
            new_change_url = url(
                r'^{0}/$'.format(self.pk_regex),
                self.admin_site.admin_view(self.change_view),
                name='{0}_{1}_change'.format(*info)
            )

            redirect_urls = []
            for i, oldurl in enumerate(urls):
                if oldurl.name == new_change_url.name:
                    urls[i] = new_change_url
        else:
            # For Django 1.9, the redirect at the end acts as catch all.
            # The custom urls need to be inserted before that.
            redirect_urls = [pat for pat in urls if not pat.name]  # redirect URL has no name.
            urls = [pat for pat in urls if pat.name]

        # Define the catch-all for custom views
        custom_urls = [
            url(r'^(?P<path>.+)$', self.admin_site.admin_view(self.subclass_view))
        ]

        # Add reverse names for all polymorphic models, so the delete button and "save and add" just work.
        # These definitions are masked by the definition above, since it needs special handling (and a ct_id parameter).
        dummy_urls = []
        for model, _ in self.get_child_models():
            admin = self._get_real_admin_by_model(model)
            dummy_urls += admin.get_urls()

        return urls + custom_urls + dummy_urls + redirect_urls

    def subclass_view(self, request, path):
        """
        Forward any request to a custom view of the real admin.
        """
        ct_id = int(request.GET.get('ct_id', 0))
        if not ct_id:
            # See if the path started with an ID.
            try:
                pos = path.find('/')
                if pos == -1:
                    object_id = long(path)
                else:
                    object_id = long(path[0:pos])
            except ValueError:
                raise Http404("No ct_id parameter, unable to find admin subclass for path '{0}'.".format(path))

            ct_id = self.model.objects.values_list('polymorphic_ctype_id', flat=True).get(pk=object_id)

        real_admin = self._get_real_admin_by_ct(ct_id)
        resolver = RegexURLResolver('^', real_admin.urls)
        resolvermatch = resolver.resolve(path)  # May raise Resolver404
        if not resolvermatch:
            raise Http404("No match for path '{0}' in admin subclass.".format(path))

        return resolvermatch.func(request, *resolvermatch.args, **resolvermatch.kwargs)

    def add_type_view(self, request, form_url=''):
        """
        Display a choice form to select which page type to add.
        """
        if not self.has_add_permission(request):
            raise PermissionDenied

        extra_qs = ''
        if request.META['QUERY_STRING']:
            extra_qs = '&' + request.META['QUERY_STRING']

        choices = self.get_child_type_choices(request, 'add')
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
            'is_popup': ("_popup" in request.POST or
                         "_popup" in request.GET),
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

        templates = self.add_type_template or [
            "admin/%s/%s/add_type_form.html" % (app_label, opts.object_name.lower()),
            "admin/%s/add_type_form.html" % app_label,
            "admin/polymorphic/add_type_form.html",  # added default here
            "admin/add_type_form.html"
        ]

        if django.VERSION >= (1, 8):
            from django.template.response import TemplateResponse
            request.current_app = self.admin_site.name
            return TemplateResponse(request, templates, context)
        else:
            context_instance = RequestContext(request, current_app=self.admin_site.name)
            return render_to_response(templates, context, context_instance=context_instance)

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


def _get_opt(model):
    try:
        return model._meta.app_label, model._meta.model_name  # Django 1.7 format
    except AttributeError:
        return model._meta.app_label, model._meta.module_name

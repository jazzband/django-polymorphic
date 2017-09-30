from django.contrib import admin
from django.utils.html import escape

from polymorphic.admin import PolymorphicChildModelAdmin, PolymorphicChildModelFilter, PolymorphicInlineSupportMixin, \
    PolymorphicParentModelAdmin, StackedPolymorphicInline
from polymorphic.tests.admintestcase import AdminTestCase
from polymorphic.tests.models import InlineModelA, InlineModelB, InlineParent, Model2A, Model2B, Model2C, Model2D


class PolymorphicAdminTests(AdminTestCase):

    def test_admin_registration(self):
        """
        Test how the registration works
        """
        @self.register(Model2A)
        class Model2Admin(PolymorphicParentModelAdmin):
            base_model = Model2A
            list_filter = (PolymorphicChildModelFilter,)
            child_models = (Model2B, Model2C, Model2D)

        @self.register(Model2B)
        @self.register(Model2C)
        @self.register(Model2D)
        class Model2ChildAdmin(PolymorphicChildModelAdmin):
            base_model = Model2A
            base_fieldsets = (
                ("Base fields", {
                    'fields': ('field1',)
                }),
            )

        # Now test which results are returned
        d_obj = Model2D.objects.create(field1='A', field2='B', field3='C', field4='D')
        self.admin_get_changelist(Model2A)  # asserts 200

        # See that the child object was returned
        response = self.admin_get_change(Model2A, d_obj.pk)
        self.assertContains(response, 'field4')

    def test_admin_inlines(self):
        """
        Test the registration of inline models.
        """
        class InlineModelAChild(StackedPolymorphicInline.Child):
            model = InlineModelA

        class InlineModelBChild(StackedPolymorphicInline.Child):
            model = InlineModelB

        class Inline(StackedPolymorphicInline):
            model = InlineModelA
            child_inlines = (
                InlineModelAChild,
                InlineModelBChild,
            )

        @self.register(InlineParent)
        class InlineParentAdmin(PolymorphicInlineSupportMixin, admin.ModelAdmin):
            inlines = (Inline,)

        obj = InlineParent.objects.create(title='FOO')
        response = self.admin_get_change(InlineParent, obj.pk)

        # Make sure the fieldset has the right data exposed in data-inline-formset
        self.assertContains(response, 'childTypes')
        self.assertContains(response, escape('"type": "inlinemodela"'))
        self.assertContains(response, escape('"type": "inlinemodelb"'))

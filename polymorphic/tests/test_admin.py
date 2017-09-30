from django.contrib import admin
from django.contrib.contenttypes.models import ContentType
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

        # -- add page
        ct_id = ContentType.objects.get_for_model(Model2D).pk
        self.admin_get_add(Model2A)  # shows type page
        self.admin_get_add(Model2A, qs='?ct_id={}'.format(ct_id))  # shows type page

        self.admin_get_add(Model2A)  # shows type page
        self.admin_post_add(Model2A, {
            'field1': 'A',
            'field2': 'B',
            'field3': 'C',
            'field4': 'D'
        }, qs='?ct_id={}'.format(ct_id))

        d_obj = Model2A.objects.all()[0]
        self.assertEqual(d_obj.__class__, Model2D)
        self.assertEqual(d_obj.field1, 'A')
        self.assertEqual(d_obj.field2, 'B')

        # -- list page
        self.admin_get_changelist(Model2A)  # asserts 200

        # -- edit
        response = self.admin_get_change(Model2A, d_obj.pk)
        self.assertContains(response, 'field4')
        self.admin_post_change(Model2A, d_obj.pk, {
            'field1': 'A2',
            'field2': 'B2',
            'field3': 'C2',
            'field4': 'D2'
        })

        d_obj.refresh_from_db()
        self.assertEqual(d_obj.field1, 'A2')
        self.assertEqual(d_obj.field2, 'B2')
        self.assertEqual(d_obj.field3, 'C2')
        self.assertEqual(d_obj.field4, 'D2')

        # -- history
        self.admin_get_history(Model2A, d_obj.pk)

        # -- delete
        self.admin_get_delete(Model2A, d_obj.pk)
        self.admin_post_delete(Model2A, d_obj.pk)
        self.assertRaises(Model2A.DoesNotExist, lambda: d_obj.refresh_from_db())

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

        parent = InlineParent.objects.create(title='FOO')
        self.assertEqual(parent.inline_children.count(), 0)

        # -- get edit page
        response = self.admin_get_change(InlineParent, parent.pk)

        # Make sure the fieldset has the right data exposed in data-inline-formset
        self.assertContains(response, 'childTypes')
        self.assertContains(response, escape('"type": "inlinemodela"'))
        self.assertContains(response, escape('"type": "inlinemodelb"'))

        # -- post edit page
        self.admin_post_change(InlineParent, parent.pk, {
            'title': 'FOO2',
            'inline_children-INITIAL_FORMS': 0,
            'inline_children-TOTAL_FORMS': 1,
            'inline_children-MIN_NUM_FORMS': 0,
            'inline_children-MAX_NUM_FORMS': 1000,
            'inline_children-0-parent': parent.pk,
            'inline_children-0-polymorphic_ctype': ContentType.objects.get_for_model(InlineModelB).pk,
            'inline_children-0-field1': 'A2',
            'inline_children-0-field2': 'B2',
        })

        parent.refresh_from_db()
        self.assertEqual(parent.title, 'FOO2')
        self.assertEqual(parent.inline_children.count(), 1)
        child = parent.inline_children.all()[0]
        self.assertEqual(child.__class__, InlineModelB)
        self.assertEqual(child.field1, 'A2')
        self.assertEqual(child.field2, 'B2')

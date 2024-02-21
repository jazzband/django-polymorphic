import os
import pytest
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib import admin
from django.contrib.contenttypes.models import ContentType
from django.utils.html import escape

from django.contrib.staticfiles.testing import StaticLiveServerTestCase

from polymorphic.admin import (
    PolymorphicChildModelAdmin,
    PolymorphicChildModelFilter,
    PolymorphicInlineSupportMixin,
    PolymorphicParentModelAdmin,
    StackedPolymorphicInline,
)
from polymorphic import tests
from polymorphic.tests.admintestcase import AdminTestCase
from polymorphic.tests.models import (
    PlainA,
    InlineModelA,
    InlineModelB,
    InlineParent,
    Model2A,
    Model2B,
    Model2C,
    Model2D,
)

from playwright.sync_api import sync_playwright, expect


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
            base_fieldsets = (("Base fields", {"fields": ("field1",)}),)

        # -- add page
        ct_id = ContentType.objects.get_for_model(Model2D).pk
        self.admin_get_add(Model2A)  # shows type page
        self.admin_get_add(Model2A, qs=f"?ct_id={ct_id}")  # shows type page

        self.admin_get_add(Model2A)  # shows type page
        self.admin_post_add(
            Model2A,
            {"field1": "A", "field2": "B", "field3": "C", "field4": "D"},
            qs=f"?ct_id={ct_id}",
        )

        d_obj = Model2A.objects.all()[0]
        assert d_obj.__class__ == Model2D
        assert d_obj.field1 == "A"
        assert d_obj.field2 == "B"

        # -- list page
        self.admin_get_changelist(Model2A)  # asserts 200

        # -- edit
        response = self.admin_get_change(Model2A, d_obj.pk)
        self.assertContains(response, "field4")
        self.admin_post_change(
            Model2A,
            d_obj.pk,
            {"field1": "A2", "field2": "B2", "field3": "C2", "field4": "D2"},
        )

        d_obj.refresh_from_db()
        assert d_obj.field1 == "A2"
        assert d_obj.field2 == "B2"
        assert d_obj.field3 == "C2"
        assert d_obj.field4 == "D2"

        # -- history
        self.admin_get_history(Model2A, d_obj.pk)

        # -- delete
        self.admin_get_delete(Model2A, d_obj.pk)
        self.admin_post_delete(Model2A, d_obj.pk)
        pytest.raises(Model2A.DoesNotExist, (lambda: d_obj.refresh_from_db()))

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
            child_inlines = (InlineModelAChild, InlineModelBChild)

        @self.register(InlineParent)
        class InlineParentAdmin(PolymorphicInlineSupportMixin, admin.ModelAdmin):
            inlines = (Inline,)

        parent = InlineParent.objects.create(title="FOO")
        assert parent.inline_children.count() == 0

        # -- get edit page
        response = self.admin_get_change(InlineParent, parent.pk)

        # Make sure the fieldset has the right data exposed in data-inline-formset
        self.assertContains(response, "childTypes")
        self.assertContains(response, escape('"type": "inlinemodela"'))
        self.assertContains(response, escape('"type": "inlinemodelb"'))

        # -- post edit page
        self.admin_post_change(
            InlineParent,
            parent.pk,
            {
                "title": "FOO2",
                "inline_children-INITIAL_FORMS": 0,
                "inline_children-TOTAL_FORMS": 1,
                "inline_children-MIN_NUM_FORMS": 0,
                "inline_children-MAX_NUM_FORMS": 1000,
                "inline_children-0-parent": parent.pk,
                "inline_children-0-polymorphic_ctype": ContentType.objects.get_for_model(
                    InlineModelB
                ).pk,
                "inline_children-0-field1": "A2",
                "inline_children-0-field2": "B2",
            },
        )

        parent.refresh_from_db()
        assert parent.title == "FOO2"
        assert parent.inline_children.count() == 1
        child = parent.inline_children.all()[0]
        assert child.__class__ == InlineModelB
        assert child.field1 == "A2"
        assert child.field2 == "B2"


class _GenericAdminFormTest(StaticLiveServerTestCase):
    """Generic admin form test using Playwright."""

    HEADLESS = tests.HEADLESS

    admin_username = "admin"
    admin_password = "password"
    admin = None

    def add_url(self, model):
        path = reverse(f"admin:{model._meta.label_lower.replace('.', '_')}_add")
        return f"{self.live_server_url}{path}"

    def change_url(self, model, id):
        path = reverse(
            f"admin:{model._meta.label_lower.replace('.', '_')}_change",
            args=[id],
        )
        return f"{self.live_server_url}{path}"

    def list_url(self, model):
        path = reverse(f"admin:{model._meta.label_lower.replace('.', '_')}_changelist")
        return f"{self.live_server_url}{path}"

    def get_object_ids(self, model):
        self.page.goto(self.list_url(model))
        return self.page.eval_on_selector_all(
            "input[name='_selected_action']", "elements => elements.map(e => e.value)"
        )

    @classmethod
    def setUpClass(cls):
        """Set up the test class with a live server and Playwright instance."""
        os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "1"
        super().setUpClass()
        cls.playwright = sync_playwright().start()
        cls.browser = cls.playwright.chromium.launch(headless=cls.HEADLESS)

        cls.admin = get_user_model().objects.create_superuser(
            username=cls.admin_username, email="admin@example.com", password=cls.admin_password
        )

    @classmethod
    def tearDownClass(cls):
        """Clean up Playwright instance after tests."""
        cls.browser.close()
        cls.playwright.stop()
        if cls.admin:
            cls.admin.delete()
        super().tearDownClass()
        del os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"]

    def setUp(self):
        """Create an admin user before running tests."""
        self.admin_username = "admin"
        self.admin_password = "password"

        self.page = self.browser.new_page()
        # Log in to the Django admin
        self.page.goto(f"{self.live_server_url}/admin/login/")
        self.page.fill("input[name='username']", self.admin_username)
        self.page.fill("input[name='password']", self.admin_password)
        self.page.click("input[type='submit']")

        # Ensure login is successful
        expect(self.page).to_have_url(f"{self.live_server_url}/admin/")

    def tearDown(self):
        if self.page:
            self.page.close()


class StackedInlineTests(_GenericAdminFormTest):
    def setUp(self):
        PlainA.objects.all().delete()
        InlineParent.objects.all().delete()
        super().setUp()
        for name in ["Brian", "Alice", "Emma", "Anna"]:
            PlainA.objects.create(field1=name)

    def tearDown(self):
        PlainA.objects.all().delete()
        InlineParent.objects.all().delete()
        super().tearDown()

    def test_admin_inline_add_autocomplete(self):
        # https://github.com/jazzband/django-polymorphic/issues/546
        self.page.goto(self.add_url(InlineParent))
        self.page.fill("input[name='title']", "Parent 1")
        with self.page.expect_navigation(timeout=10000) as nav_info:
            self.page.click("input[name='_save']")

        response = nav_info.value
        assert response.status < 400

        # verify the add
        added = InlineParent.objects.get(title="Parent 1")
        self.page.goto(self.change_url(InlineParent, added.pk))
        polymorphic_menu = self.page.locator(
            "div.polymorphic-add-choice div.polymorphic-type-menu"
        )
        expect(polymorphic_menu).to_be_hidden()

        self.page.click("div.polymorphic-add-choice a")

        expect(polymorphic_menu).to_be_visible()

        self.page.click("div.polymorphic-type-menu a[data-type='inlinemodelb']")

        selector_menu = self.page.locator("span.select2-dropdown.select2-dropdown--below")
        expect(selector_menu).to_be_hidden()
        with self.page.expect_response("**autocomplete**", timeout=10000):
            self.page.click("span.select2-selection__arrow b[role='presentation']")

        expect(selector_menu).to_be_visible()

        suggestions = self.page.locator("ul.select2-results__options > li").all_inner_texts()
        assert "Alice" in suggestions
        assert "Anna" in suggestions
        assert "Brian" in suggestions
        assert "Emma" in suggestions

        with self.page.expect_response("**autocomplete**", timeout=10000):
            self.page.locator("input.select2-search__field[type='search']").type("B")

        suggestions = self.page.locator("ul.select2-results__options > li").all_inner_texts()
        assert suggestions == ["Brian"]


class PolymorphicFormTests(_GenericAdminFormTest):
    def setUp(self):
        Model2A.objects.all().delete()
        super().setUp()

    def tearDown(self):
        Model2A.objects.all().delete()
        super().tearDown()

    def test_admin_polymorphic_add(self):
        model2b_ct = ContentType.objects.get_for_model(Model2B)
        model2c_ct = ContentType.objects.get_for_model(Model2C)
        model2d_ct = ContentType.objects.get_for_model(Model2D)

        for model_type, fields in [
            (
                model2b_ct,
                {
                    "field1": "2B1",
                    "field2": "2B2",
                },
            ),
            (
                model2c_ct,
                {
                    "field1": "2C1",
                    "field2": "2C2",
                    "field3": "2C3",
                },
            ),
            (
                model2d_ct,
                {
                    "field1": "2D1",
                    "field2": "2D2",
                    "field3": "2D3",
                    "field4": "2D4",
                },
            ),
        ]:
            self.page.goto(self.add_url(Model2A))

            # https://github.com/jazzband/django-polymorphic/pull/580
            expect(self.page.locator("div.breadcrumbs")).to_have_count(1)
            expect(self.page.locator("form#logout-form")).to_have_count(1)

            self.page.locator(f"input[type=radio][value='{model_type.pk}']").check()
            with self.page.expect_navigation(timeout=10000) as nav_info:
                self.page.click("input[name='_save']")

            response = nav_info.value
            assert response.status < 400

            for field, value in fields.items():
                self.page.fill(f"input[name='{field}']", value)

            with self.page.expect_navigation(timeout=10000) as nav_info:
                self.page.click("input[name='_save']")

            response = nav_info.value
            assert response.status < 400

        assert Model2A.objects.count() == 3

        object_ids = [int(oid) for oid in self.get_object_ids(Model2A)]

        assert len(object_ids) == 3

        assert Model2B.objects.first().pk in object_ids
        assert Model2C.objects.first().pk in object_ids
        assert Model2D.objects.first().pk in object_ids

        assert Model2B.objects.first().field1 == "2B1"
        assert Model2B.objects.first().field2 == "2B2"

        assert Model2C.objects.first().field1 == "2C1"
        assert Model2C.objects.first().field2 == "2C2"
        assert Model2C.objects.first().field3 == "2C3"

        assert Model2D.objects.first().field1 == "2D1"
        assert Model2D.objects.first().field2 == "2D2"
        assert Model2D.objects.first().field3 == "2D3"
        assert Model2D.objects.first().field4 == "2D4"

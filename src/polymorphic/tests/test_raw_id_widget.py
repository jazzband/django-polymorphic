"""
Tests for PolymorphicForeignKeyRawIdWidget and raw ID field filtering.
"""

from django.contrib.admin.sites import AdminSite
from django.contrib.contenttypes.models import ContentType
from django.test import RequestFactory, TestCase

from polymorphic.admin import PolymorphicForeignKeyRawIdWidget, PolymorphicParentModelAdmin
from polymorphic.tests.models import Model2A, Model2B, Model2C, Model2D, RelationBase


class RawIdWidgetTests(TestCase):
    """Test the PolymorphicForeignKeyRawIdWidget functionality."""

    def setUp(self):
        self.factory = RequestFactory()
        self.site = AdminSite()

    def test_widget_adds_polymorphic_ctype_parameter(self):
        """Test that the widget adds polymorphic_ctype to URL parameters."""
        # Use a real model field's remote_field
        from polymorphic.tests.models import RelationBase

        # Get the FK field's remote_field which points to RelationBase (polymorphic)
        fk_field = RelationBase._meta.get_field("fk")

        widget = PolymorphicForeignKeyRawIdWidget(fk_field.remote_field, self.site)
        params = widget.url_parameters()

        # Should include the polymorphic_ctype parameter
        self.assertIn("polymorphic_ctype", params)

        # Should be the content type ID for RelationBase
        expected_ct = ContentType.objects.get_for_model(RelationBase, for_concrete_model=False)
        self.assertEqual(params["polymorphic_ctype"], expected_ct.id)

    def test_widget_with_non_polymorphic_model(self):
        """Test that the widget works with non-polymorphic models."""
        from polymorphic.tests.models import (
            PlainParentModelWithManager,
            PlainChildModelWithManager,
        )

        # Get a FK field that points to a non-polymorphic model
        fk_field = PlainChildModelWithManager._meta.get_field("fk")

        widget = PolymorphicForeignKeyRawIdWidget(fk_field.remote_field, self.site)
        params = widget.url_parameters()

        # Should not include polymorphic_ctype for non-polymorphic models
        self.assertNotIn("polymorphic_ctype", params)

    def test_widget_with_different_child_models(self):
        """Test widget with different polymorphic child models."""
        from polymorphic.tests.models import RelationA, RelationB, RelationBC

        for model_class in [RelationA, RelationB, RelationBC]:
            # Get the FK field from the model
            fk_field = model_class._meta.get_field("fk")

            widget = PolymorphicForeignKeyRawIdWidget(fk_field.remote_field, self.site)
            params = widget.url_parameters()

            # All these models have FK to RelationBase (the parent)
            expected_ct = ContentType.objects.get_for_model(RelationBase, for_concrete_model=False)
            self.assertEqual(params["polymorphic_ctype"], expected_ct.id)

    def test_widget_with_no_rel(self):
        """Test widget handles missing rel gracefully."""
        widget = PolymorphicForeignKeyRawIdWidget(None, self.site)
        params = widget.url_parameters()

        # Should not crash, just return empty params
        self.assertNotIn("polymorphic_ctype", params)


class ParentAdminQuerysetFilteringTests(TestCase):
    """Test the queryset filtering in PolymorphicParentModelAdmin."""

    def setUp(self):
        self.factory = RequestFactory()
        self.site = AdminSite()

        # Create test data
        self.obj_a = Model2A.objects.create(field1="A1")
        self.obj_b = Model2B.objects.create(field1="B1", field2="B2")
        self.obj_c = Model2C.objects.create(field1="C1", field2="C2", field3="C3")
        self.obj_d = Model2D.objects.create(field1="D1", field2="D2", field3="D3", field4="D4")

        # Create admin instance
        class TestParentAdmin(PolymorphicParentModelAdmin):
            base_model = Model2A
            child_models = [Model2A, Model2B, Model2C, Model2D]

        self.admin = TestParentAdmin(Model2A, self.site)

    def test_queryset_without_ctype_filter(self):
        """Test that queryset returns all objects when no filter is applied."""
        request = self.factory.get("/admin/tests/model2a/")
        qs = self.admin.get_queryset(request)

        # Should return all objects (non-polymorphic by default)
        self.assertEqual(qs.count(), 4)

    def test_queryset_with_valid_ctype_filter(self):
        """Test queryset filtering with valid polymorphic_ctype parameter."""
        ct_b = ContentType.objects.get_for_model(Model2B, for_concrete_model=False)
        request = self.factory.get(f"/admin/tests/model2a/?polymorphic_ctype={ct_b.id}")
        qs = self.admin.get_queryset(request)

        # Should only return Model2B instances
        self.assertEqual(qs.count(), 1)
        obj = qs.first()
        self.assertEqual(obj.pk, self.obj_b.pk)

    def test_queryset_with_child_ctype_filter(self):
        """Test filtering by a deeper child model."""
        ct_d = ContentType.objects.get_for_model(Model2D, for_concrete_model=False)
        request = self.factory.get(f"/admin/tests/model2a/?polymorphic_ctype={ct_d.id}")
        qs = self.admin.get_queryset(request)

        # Should only return Model2D instances
        self.assertEqual(qs.count(), 1)
        obj = qs.first()
        self.assertEqual(obj.pk, self.obj_d.pk)

    def test_queryset_with_invalid_ctype_filter(self):
        """Test that invalid ctype parameter is ignored gracefully."""
        request = self.factory.get("/admin/tests/model2a/?polymorphic_ctype=invalid")
        qs = self.admin.get_queryset(request)

        # Should return all objects (filter ignored)
        self.assertEqual(qs.count(), 4)

    def test_queryset_with_non_integer_ctype(self):
        """Test that non-integer ctype parameter is ignored."""
        request = self.factory.get("/admin/tests/model2a/?polymorphic_ctype=abc")
        qs = self.admin.get_queryset(request)

        # Should return all objects (filter ignored)
        self.assertEqual(qs.count(), 4)

    def test_queryset_with_nonexistent_ctype_id(self):
        """Test with a content type ID that doesn't match any objects."""
        # Use a very high ID that shouldn't exist
        request = self.factory.get("/admin/tests/model2a/?polymorphic_ctype=99999")
        qs = self.admin.get_queryset(request)

        # Should return no objects
        self.assertEqual(qs.count(), 0)

    def test_queryset_filtering_preserves_other_filters(self):
        """Test that polymorphic_ctype filter works with other query parameters."""
        ct_c = ContentType.objects.get_for_model(Model2C, for_concrete_model=False)
        request = self.factory.get(f"/admin/tests/model2a/?polymorphic_ctype={ct_c.id}&field1=C1")
        qs = self.admin.get_queryset(request)

        # The polymorphic_ctype filter should be applied
        # (other filters are handled by changelist, not get_queryset)
        self.assertEqual(qs.count(), 1)


class IntegrationTests(TestCase):
    """Integration tests for the complete raw ID widget workflow."""

    def setUp(self):
        self.factory = RequestFactory()
        self.site = AdminSite()

        # Create test data using RelationBase models
        from polymorphic.tests.models import RelationBase, RelationB

        self.obj_b1 = RelationB.objects.create(field_base="B1", field_b="B2-1")
        self.obj_b2 = RelationB.objects.create(field_base="B2", field_b="B2-2")
        self.obj_base = RelationBase.objects.create(field_base="Base1")

    def test_widget_url_filters_admin_popup(self):
        """Test that widget-generated URL properly filters the admin popup."""
        from polymorphic.tests.models import RelationB, RelationBase

        # Use a real FK field that points to RelationBase
        fk_field = RelationB._meta.get_field("fk")

        widget = PolymorphicForeignKeyRawIdWidget(fk_field.remote_field, self.site)
        params = widget.url_parameters()

        # Create admin and request with those parameters
        class TestParentAdmin(PolymorphicParentModelAdmin):
            base_model = RelationBase
            child_models = [RelationBase, RelationB]

        admin = TestParentAdmin(RelationBase, self.site)

        # Build URL with widget parameters
        query_string = "&".join(f"{k}={v}" for k, v in params.items())
        request = self.factory.get(f"/admin/tests/relationbase/?{query_string}")

        qs = admin.get_queryset(request)

        # The widget adds the content type for RelationBase (the model the FK points to)
        # When filtering by RelationBase content type, we only get instances with that exact type
        # RelationB instances have their own content type, so they won't be included
        self.assertEqual(qs.count(), 1)
        pks = list(qs.values_list("pk", flat=True))
        self.assertIn(self.obj_base.pk, pks)
        # RelationB instances are NOT included because they have RelationB content type
        self.assertNotIn(self.obj_b1.pk, pks)
        self.assertNotIn(self.obj_b2.pk, pks)

    def test_backward_compatibility(self):
        """Test that existing behavior without the widget still works."""
        from polymorphic.tests.models import RelationBase, RelationB

        class TestParentAdmin(PolymorphicParentModelAdmin):
            base_model = RelationBase
            child_models = [RelationBase, RelationB]

        admin = TestParentAdmin(RelationBase, self.site)
        request = self.factory.get("/admin/tests/relationbase/")

        qs = admin.get_queryset(request)

        # Should return all objects as before
        self.assertEqual(qs.count(), 3)

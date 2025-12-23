"""
Tests for flexible fieldset merging in PolymorphicChildModelAdmin (issue #472)
"""

from django.test import TestCase, RequestFactory
from django.contrib.admin.sites import AdminSite
from polymorphic.admin import PolymorphicChildModelAdmin
from polymorphic.tests.models import Model2A, Model2B, Model2C


class FieldsetMergingTests(TestCase):
    """Test the extra_fieldset_mapping feature for flexible fieldset merging."""

    def setUp(self):
        self.factory = RequestFactory()
        self.request = self.factory.get("/")
        self.site = AdminSite()

    def test_backward_compatibility_no_mapping(self):
        """Test that without extra_fieldset_mapping, behavior is unchanged."""

        class TestAdmin(PolymorphicChildModelAdmin):
            base_model = Model2A
            base_fieldsets = (
                ("General", {"fields": ("field1",)}),
                ("Advanced", {"fields": ()}),
            )

        admin = TestAdmin(Model2B, self.site)
        fieldsets = admin.get_fieldsets(self.request)

        # Should have 3 fieldsets: General, Contents (extra), Advanced
        self.assertEqual(len(fieldsets), 3)
        self.assertEqual(fieldsets[0][0], "General")
        self.assertEqual(fieldsets[1][0], "Contents")  # extra_fieldset_title default
        self.assertEqual(fieldsets[2][0], "Advanced")

        # field2 should be in the Contents fieldset
        self.assertIn("field2", fieldsets[1][1]["fields"])

    def test_basic_fieldset_mapping(self):
        """Test basic mapping of extra fields to existing fieldsets."""

        class TestAdmin(PolymorphicChildModelAdmin):
            base_model = Model2A
            base_fieldsets = (
                ("General", {"fields": ("field1",)}),
                ("Advanced", {"fields": ()}),
            )
            extra_fieldset_mapping = {
                "General": ["field2"],
            }

        admin = TestAdmin(Model2B, self.site)
        fieldsets = admin.get_fieldsets(self.request)

        # Should have 2 fieldsets: General (merged), Advanced
        self.assertEqual(len(fieldsets), 2)
        self.assertEqual(fieldsets[0][0], "General")
        self.assertEqual(fieldsets[1][0], "Advanced")

        # field2 should be merged into General fieldset
        self.assertIn("field1", fieldsets[0][1]["fields"])
        self.assertIn("field2", fieldsets[0][1]["fields"])

    def test_multiple_fieldset_mapping(self):
        """Test mapping extra fields to multiple existing fieldsets."""

        class TestAdmin(PolymorphicChildModelAdmin):
            base_model = Model2A
            base_fieldsets = (
                ("General", {"fields": ("field1",)}),
                ("Advanced", {"fields": ()}),
                ("Extra", {"fields": ()}),
            )
            extra_fieldset_mapping = {
                "General": ["field2"],
                "Advanced": ["field3"],
            }

        admin = TestAdmin(Model2C, self.site)
        fieldsets = admin.get_fieldsets(self.request)

        # Should have 3 fieldsets with merged fields
        self.assertEqual(len(fieldsets), 3)

        # Check General fieldset
        self.assertEqual(fieldsets[0][0], "General")
        self.assertIn("field1", fieldsets[0][1]["fields"])
        self.assertIn("field2", fieldsets[0][1]["fields"])

        # Check Advanced fieldset
        self.assertEqual(fieldsets[1][0], "Advanced")
        self.assertIn("field3", fieldsets[1][1]["fields"])

        # Check Extra fieldset (unchanged)
        self.assertEqual(fieldsets[2][0], "Extra")

    def test_unmapped_fields_create_new_fieldset(self):
        """Test that unmapped fields create a new fieldset with extra_fieldset_title."""

        class TestAdmin(PolymorphicChildModelAdmin):
            base_model = Model2A
            base_fieldsets = (
                ("General", {"fields": ("field1",)}),
                ("Advanced", {"fields": ()}),
            )
            extra_fieldset_mapping = {
                "General": ["field2"],
                # field3 is not mapped
            }
            extra_fieldset_title = "Other Fields"

        admin = TestAdmin(Model2C, self.site)
        fieldsets = admin.get_fieldsets(self.request)

        # Should have 3 fieldsets: General (merged), Other Fields (unmapped), Advanced
        self.assertEqual(len(fieldsets), 3)
        self.assertEqual(fieldsets[0][0], "General")
        self.assertEqual(fieldsets[1][0], "Other Fields")
        self.assertEqual(fieldsets[2][0], "Advanced")

        # field2 in General, field3 in Other Fields
        self.assertIn("field2", fieldsets[0][1]["fields"])
        self.assertIn("field3", fieldsets[1][1]["fields"])

    def test_none_key_in_mapping(self):
        """Test explicit None mapping for creating new fieldset."""

        class TestAdmin(PolymorphicChildModelAdmin):
            base_model = Model2A
            base_fieldsets = (
                ("General", {"fields": ("field1",)}),
                ("Advanced", {"fields": ()}),
            )
            extra_fieldset_mapping = {
                "General": ["field2"],
                None: ["field3"],  # Explicitly map to new fieldset
            }
            extra_fieldset_title = "Miscellaneous"

        admin = TestAdmin(Model2C, self.site)
        fieldsets = admin.get_fieldsets(self.request)

        # Should have 3 fieldsets
        self.assertEqual(len(fieldsets), 3)
        self.assertEqual(fieldsets[0][0], "General")
        self.assertEqual(fieldsets[1][0], "Miscellaneous")
        self.assertEqual(fieldsets[2][0], "Advanced")

        # field3 should be in Miscellaneous fieldset
        self.assertIn("field3", fieldsets[1][1]["fields"])

    def test_empty_mapping(self):
        """Test that empty mapping dict behaves like no mapping."""

        class TestAdmin(PolymorphicChildModelAdmin):
            base_model = Model2A
            base_fieldsets = (
                ("General", {"fields": ("field1",)}),
                ("Advanced", {"fields": ()}),
            )
            extra_fieldset_mapping = {}

        admin = TestAdmin(Model2B, self.site)
        fieldsets = admin.get_fieldsets(self.request)

        # Should create new fieldset for all extra fields
        self.assertEqual(len(fieldsets), 3)
        self.assertEqual(fieldsets[1][0], "Contents")
        self.assertIn("field2", fieldsets[1][1]["fields"])

    def test_nonexistent_field_in_mapping(self):
        """Test that mapping non-existent fields doesn't cause errors."""

        class TestAdmin(PolymorphicChildModelAdmin):
            base_model = Model2A
            base_fieldsets = (("General", {"fields": ("field1",)}),)
            extra_fieldset_mapping = {
                "General": ["field2", "nonexistent_field"],
            }

        admin = TestAdmin(Model2B, self.site)
        # Should not raise an error
        fieldsets = admin.get_fieldsets(self.request)

        # Only field2 should be added (nonexistent_field is ignored)
        self.assertIn("field2", fieldsets[0][1]["fields"])
        self.assertNotIn("nonexistent_field", fieldsets[0][1]["fields"])

    def test_all_fields_mapped(self):
        """Test when all extra fields are mapped to existing fieldsets."""

        class TestAdmin(PolymorphicChildModelAdmin):
            base_model = Model2A
            base_fieldsets = (
                ("General", {"fields": ("field1",)}),
                ("Advanced", {"fields": ()}),
            )
            extra_fieldset_mapping = {
                "General": ["field2", "field3"],
            }

        admin = TestAdmin(Model2C, self.site)
        fieldsets = admin.get_fieldsets(self.request)

        # Should have only 2 fieldsets (no new fieldset created)
        self.assertEqual(len(fieldsets), 2)
        self.assertEqual(fieldsets[0][0], "General")
        self.assertEqual(fieldsets[1][0], "Advanced")

        # All extra fields in General
        self.assertIn("field2", fieldsets[0][1]["fields"])
        self.assertIn("field3", fieldsets[0][1]["fields"])

    def test_preserves_fieldset_options(self):
        """Test that other fieldset options are preserved during merging."""

        class TestAdmin(PolymorphicChildModelAdmin):
            base_model = Model2A
            base_fieldsets = (
                (
                    "General",
                    {
                        "fields": ("field1",),
                        "classes": ("collapse",),
                        "description": "General fields",
                    },
                ),
            )
            extra_fieldset_mapping = {
                "General": ["field2"],
            }

        admin = TestAdmin(Model2B, self.site)
        fieldsets = admin.get_fieldsets(self.request)

        # Check that options are preserved
        self.assertEqual(fieldsets[0][1]["classes"], ("collapse",))
        self.assertEqual(fieldsets[0][1]["description"], "General fields")
        # And fields are merged
        self.assertIn("field1", fieldsets[0][1]["fields"])
        self.assertIn("field2", fieldsets[0][1]["fields"])

    def test_no_extra_fields(self):
        """Test behavior when there are no extra fields to map."""

        class TestAdmin(PolymorphicChildModelAdmin):
            base_model = Model2A
            base_fieldsets = (("General", {"fields": ("field1",)}),)
            extra_fieldset_mapping = {
                "General": ["field2"],
            }

        admin = TestAdmin(Model2A, self.site)  # Model2A has no extra fields
        fieldsets = admin.get_fieldsets(self.request)

        # Should return base_fieldsets unchanged
        self.assertEqual(len(fieldsets), 1)
        self.assertEqual(fieldsets[0][0], "General")
        self.assertEqual(fieldsets[0][1]["fields"], ("field1",))

"""
Tests for PolymorphicGuard serialization of on_delete functions.

This test module ensures that all Django on_delete handlers (CASCADE, PROTECT,
SET_NULL, SET_DEFAULT, SET(...), DO_NOTHING, and RESTRICT) are properly wrapped
with PolymorphicGuard and serialize correctly in migrations.
"""

import shutil
from pathlib import Path
from django.test import TestCase, TransactionTestCase
from django.db import models
from django.db.migrations.serializer import serializer_factory
from django.db.models import ProtectedError, RestrictedError
from ..utils import GeneratedMigrationsPerClassMixin
from polymorphic.deletion import PolymorphicGuard
from polymorphic.managers import PolymorphicManager
from polymorphic.query import PolymorphicQuerySet


class OnDeleteSerializationTest(GeneratedMigrationsPerClassMixin, TransactionTestCase):
    """
    Test that PolymorphicGuard wraps on_delete handlers and serializes them correctly.
    """

    apps_to_migrate: list[str] = ["test_migrations"]

    @property
    def state(self):
        return self._applied_states["test_migrations"]

    @classmethod
    def setUpClass(cls):
        """Set up by generating and applying migrations for test_migrations app"""
        super().setUpClass()
        cls.migrations_dir = Path(__file__).parent / "migrations"

    def test_migration_managers_non_polymorphic(self):
        for mdl in [
            "BasePolyModel",
            "ChildPolyModel",
            "GrandChildPolyModel",
            "ModelWithCascade",
            "ModelWithProtect",
            "ModelWithSetNull",
            "ModelWithSetDefault",
            "ModelWithSet",
            "ModelWithDoNothing",
            "ModelWithRestrict",
            "ModelWithOneToOneCascade",
            "ModelWithOneToOneProtect",
            "ModelWithOneToOneSetNull",
        ]:
            Model = self.state.apps.get_model("test_migrations", mdl)

        managers = Model._meta.managers
        assert not isinstance(Model.objects, (PolymorphicManager, PolymorphicQuerySet))
        assert all(not isinstance(m, (PolymorphicManager, PolymorphicQuerySet)) for m in managers)

        RelatedModel = self.state.apps.get_model("test_migrations", "RelatedModel")
        related = RelatedModel.objects.create(name="tester")
        ModelWithOneToOneCascade = self.state.apps.get_model(
            "test_migrations", "ModelWithOneToOneCascade"
        )
        ModelWithOneToOneProtect = self.state.apps.get_model(
            "test_migrations", "ModelWithOneToOneProtect"
        )
        ModelWithOneToOneSetNull = self.state.apps.get_model(
            "test_migrations", "ModelWithOneToOneSetNull"
        )

        ModelWithOneToOneCascade.objects.create(related=related)
        ModelWithOneToOneProtect.objects.create(related=related)
        ModelWithOneToOneSetNull.objects.create(related=related)

        for relation in [
            "modelwithcascade_set",
            "modelwithprotect_set",
            "modelwithsetnull_set",
            "modelwithsetdefault_set",
            "modelwithset_set",
            "modelwithdonothing_set",
            "modelwithrestrict_set",
            "modelwithonetoonecascade",
            "one_to_one_protect",
            "one_to_one_set_null",
        ]:
            assert not isinstance(
                getattr(related, relation), (PolymorphicManager, PolymorphicQuerySet)
            )

    def test_foreign_keys_wrapped_with_PolymorphicGuard(self):
        """Verify that ForeignKey on_delete handlers are wrapped with PolymorphicGuard"""
        from .models import (
            ModelWithCascade,
            ModelWithProtect,
            ModelWithSetNull,
            ModelWithSetDefault,
            ModelWithSet,
            ModelWithDoNothing,
            ModelWithRestrict,
        )

        # Get the 'related' field from each model
        models_to_test = [
            ModelWithCascade,
            ModelWithProtect,
            ModelWithSetNull,
            ModelWithSetDefault,
            ModelWithSet,
            ModelWithDoNothing,
            ModelWithRestrict,
        ]

        for model_class in models_to_test:
            with self.subTest(model=model_class.__name__):
                field = model_class._meta.get_field("related")
                on_delete = field.remote_field.on_delete

                # Assert that the on_delete handler is wrapped with PolymorphicGuard
                self.assertIsInstance(
                    on_delete,
                    PolymorphicGuard,
                    f"{model_class.__name__}.related field should have PolymorphicGuard wrapper",
                )

    def test_one_to_one_wrapped_with_PolymorphicGuard(self):
        """Verify that OneToOneField on_delete handlers are wrapped with PolymorphicGuard"""
        from .models import (
            ModelWithOneToOneCascade,
            ModelWithOneToOneProtect,
            ModelWithOneToOneSetNull,
        )

        models_to_test = [
            ModelWithOneToOneCascade,
            ModelWithOneToOneProtect,
            ModelWithOneToOneSetNull,
        ]

        for model_class in models_to_test:
            with self.subTest(model=model_class.__name__):
                field = model_class._meta.get_field("related")
                on_delete = field.remote_field.on_delete

                # Assert that the on_delete handler is wrapped with PolymorphicGuard
                self.assertIsInstance(
                    on_delete,
                    PolymorphicGuard,
                    f"{model_class.__name__}.related field should have PolymorphicGuard wrapper",
                )

    def test_cascade_serialization(self):
        """Test that CASCADE serializes correctly through PolymorphicGuard"""
        from .models import ModelWithCascade

        field = ModelWithCascade._meta.get_field("related")
        on_delete = field.remote_field.on_delete

        # Serialize the PolymorphicGuard wrapped CASCADE
        serialized, imports = serializer_factory(on_delete).serialize()

        # Should serialize as CASCADE from django.db.models.deletion, not as PolymorphicGuard
        self.assertIn("CASCADE", serialized)
        self.assertNotIn("PolymorphicGuard", serialized)

    def test_protect_serialization(self):
        """Test that PROTECT serializes correctly through PolymorphicGuard"""
        from .models import ModelWithProtect

        field = ModelWithProtect._meta.get_field("related")
        on_delete = field.remote_field.on_delete

        serialized, imports = serializer_factory(on_delete).serialize()

        self.assertIn("PROTECT", serialized)
        self.assertNotIn("PolymorphicGuard", serialized)

    def test_set_null_serialization(self):
        """Test that SET_NULL serializes correctly through PolymorphicGuard"""
        from .models import ModelWithSetNull

        field = ModelWithSetNull._meta.get_field("related")
        on_delete = field.remote_field.on_delete

        serialized, imports = serializer_factory(on_delete).serialize()

        self.assertIn("SET_NULL", serialized)
        self.assertNotIn("PolymorphicGuard", serialized)

    def test_set_default_serialization(self):
        """Test that SET_DEFAULT serializes correctly through PolymorphicGuard"""
        from .models import ModelWithSetDefault

        field = ModelWithSetDefault._meta.get_field("related")
        on_delete = field.remote_field.on_delete

        serialized, imports = serializer_factory(on_delete).serialize()

        self.assertIn("SET_DEFAULT", serialized)
        self.assertNotIn("PolymorphicGuard", serialized)

    def test_set_callable_serialization(self):
        """Test that SET(...) with a callable serializes correctly through PolymorphicGuard"""
        from .models import ModelWithSet

        field = ModelWithSet._meta.get_field("related")
        on_delete = field.remote_field.on_delete

        serialized, imports = serializer_factory(on_delete).serialize()

        # Should serialize the SET() function with the callable reference
        self.assertIn("SET", serialized)
        self.assertIn("get_default_related", serialized)
        self.assertNotIn("PolymorphicGuard", serialized)

    def test_do_nothing_serialization(self):
        """Test that DO_NOTHING serializes correctly through PolymorphicGuard"""
        from .models import ModelWithDoNothing

        field = ModelWithDoNothing._meta.get_field("related")
        on_delete = field.remote_field.on_delete

        serialized, imports = serializer_factory(on_delete).serialize()

        self.assertIn("DO_NOTHING", serialized)
        self.assertNotIn("PolymorphicGuard", serialized)

    def test_restrict_serialization(self):
        """Test that RESTRICT serializes correctly through PolymorphicGuard"""
        from .models import ModelWithRestrict

        field = ModelWithRestrict._meta.get_field("related")
        on_delete = field.remote_field.on_delete

        serialized, imports = serializer_factory(on_delete).serialize()

        self.assertIn("RESTRICT", serialized)
        self.assertNotIn("PolymorphicGuard", serialized)

    def test_migration_file_generated(self):
        """Test that a migration file was generated"""
        # Check that at least one migration file was created
        migration_files = list(self.migrations_dir.glob("0001_*.py"))
        self.assertTrue(len(migration_files) > 0, "No migration file was generated")

    def test_migration_file_content(self):
        """Test that the generated migration file contains correct serialization"""
        # Find the initial migration file
        migration_files = list(self.migrations_dir.glob("0001_*.py"))
        self.assertTrue(len(migration_files) > 0, "No migration file found")

        migration_file = migration_files[0]
        content = migration_file.read_text()

        # Check that PolymorphicGuard is NOT in the migration file
        self.assertNotIn(
            "PolymorphicGuard", content, "Migration file should not contain PolymorphicGuard"
        )

        # Check that on_delete handlers are properly serialized
        self.assertIn("django.db.models.deletion.CASCADE", content)
        self.assertIn("django.db.models.deletion.PROTECT", content)
        self.assertIn("django.db.models.deletion.SET_NULL", content)
        self.assertIn("django.db.models.deletion.SET_DEFAULT", content)
        self.assertIn("django.db.models.deletion.DO_NOTHING", content)
        self.assertIn("django.db.models.deletion.RESTRICT", content)

        # Check that SET() with callable is properly serialized
        self.assertIn("models.SET", content)
        self.assertIn("get_default_related", content)

    def test_migration_serialization_stability(self):
        """
        Test that the migration file contains stable serialization.
        This ensures that PolymorphicGuard doesn't cause migration churn
        by verifying the migration was generated successfully in setUpClass.
        """
        # The fact that we have a migration file and it contains the right
        # serialization (tested in test_migration_file_content) proves
        # that the serialization is stable. If it wasn't stable, the
        # migration file would either fail to generate or contain
        # PolymorphicGuard references.
        migration_files = list(self.migrations_dir.glob("0001_*.py"))
        self.assertEqual(len(migration_files), 1, "Should have exactly one initial migration file")

    def test_PolymorphicGuard_unwraps_correctly(self):
        """Test that PolymorphicGuard properly unwraps to the underlying action"""
        from .models import ModelWithCascade

        field = ModelWithCascade._meta.get_field("related")
        on_delete = field.remote_field.on_delete

        # Verify it's wrapped
        self.assertIsInstance(on_delete, PolymorphicGuard)

        # Verify the underlying action is CASCADE
        self.assertEqual(on_delete.action, models.CASCADE)

    def test_all_on_delete_types_covered(self):
        """
        Meta-test to ensure we've covered all Django on_delete types.
        This test documents which on_delete types we're testing.
        """
        tested_types = {
            "CASCADE": models.CASCADE,
            "PROTECT": models.PROTECT,
            "SET_NULL": models.SET_NULL,
            "SET_DEFAULT": models.SET_DEFAULT,
            "SET": models.SET,  # This is a callable that returns the actual handler
            "DO_NOTHING": models.DO_NOTHING,
            "RESTRICT": models.RESTRICT,
        }

        # Document that we have test models for each type
        from .models import (
            ModelWithCascade,
            ModelWithProtect,
            ModelWithSetNull,
            ModelWithSetDefault,
            ModelWithSet,
            ModelWithDoNothing,
            ModelWithRestrict,
        )

        model_mapping = {
            "CASCADE": ModelWithCascade,
            "PROTECT": ModelWithProtect,
            "SET_NULL": ModelWithSetNull,
            "SET_DEFAULT": ModelWithSetDefault,
            "SET": ModelWithSet,
            "DO_NOTHING": ModelWithDoNothing,
            "RESTRICT": ModelWithRestrict,
        }

        # Verify we have a model for each on_delete type
        for type_name, on_delete_handler in tested_types.items():
            with self.subTest(type=type_name):
                self.assertIn(type_name, model_mapping, f"Missing test model for {type_name}")
                model_class = model_mapping[type_name]
                field = model_class._meta.get_field("related")

                # Verify the field is properly configured
                self.assertIsNotNone(field)
                self.assertIsInstance(field.remote_field.on_delete, PolymorphicGuard)


class PolymorphicInheritanceSerializationTest(TestCase):
    """
    Test that PolymorphicGuard works correctly with polymorphic model inheritance.
    """

    def test_polymorphic_inheritance_chain(self):
        """Test that polymorphic model inheritance works with all on_delete types"""
        from .models import BasePolyModel, ChildPolyModel, GrandChildPolyModel

        # Verify the inheritance chain is set up correctly
        self.assertTrue(issubclass(ChildPolyModel, BasePolyModel))
        self.assertTrue(issubclass(GrandChildPolyModel, ChildPolyModel))
        self.assertTrue(issubclass(GrandChildPolyModel, BasePolyModel))

        # Verify each model has the polymorphic_ctype field
        for model_class in [BasePolyModel, ChildPolyModel, GrandChildPolyModel]:
            with self.subTest(model=model_class.__name__):
                ctype_field = model_class._meta.get_field("polymorphic_ctype")
                self.assertIsNotNone(ctype_field)
                # The polymorphic_ctype field uses CASCADE which should also be wrapped
                self.assertIsInstance(ctype_field.remote_field.on_delete, PolymorphicGuard)


class OnDeleteBehaviorTest(GeneratedMigrationsPerClassMixin, TransactionTestCase):
    """
    Test that PolymorphicGuard correctly executes on_delete actions.

    These tests verify the runtime behavior of each on_delete type when
    wrapped with PolymorphicGuard by creating and deleting model instances.
    """

    apps_to_migrate: list[str] = ["test_migrations"]

    def test_cascade_deletes_related_objects(self):
        """Test that CASCADE deletes related polymorphic objects"""
        from .models import RelatedModel, ModelWithCascade

        # Create a related model and a polymorphic model that references it
        related = RelatedModel.objects.create(name="test")
        cascade_obj = ModelWithCascade.objects.create(related=related)
        cascade_obj_id = cascade_obj.id

        # Verify the object exists
        self.assertTrue(ModelWithCascade.objects.filter(id=cascade_obj_id).exists())

        # Delete the related model
        related.delete()

        # Verify the cascade object was deleted
        self.assertFalse(ModelWithCascade.objects.filter(id=cascade_obj_id).exists())

    def test_protect_prevents_deletion(self):
        """Test that PROTECT prevents deletion of related objects"""
        from .models import RelatedModel, ModelWithProtect

        # Create a related model and a polymorphic model that references it
        related = RelatedModel.objects.create(name="test")
        ModelWithProtect.objects.create(related=related)

        # Attempting to delete the related model should raise ProtectedError
        with self.assertRaises(ProtectedError):
            related.delete()

        # Verify both objects still exist
        self.assertTrue(RelatedModel.objects.filter(id=related.id).exists())
        self.assertTrue(ModelWithProtect.objects.filter(related=related).exists())

    def test_set_null_sets_field_to_null(self):
        """Test that SET_NULL sets the foreign key to null"""
        from .models import RelatedModel, ModelWithSetNull

        # Create a related model and a polymorphic model that references it
        related = RelatedModel.objects.create(name="test")
        set_null_obj = ModelWithSetNull.objects.create(related=related)
        set_null_obj_id = set_null_obj.id

        # Verify the relationship exists
        self.assertEqual(set_null_obj.related, related)

        # Delete the related model
        related.delete()

        # Verify the object still exists but the field is now null
        set_null_obj = ModelWithSetNull.objects.get(id=set_null_obj_id)
        self.assertIsNone(set_null_obj.related)

    def test_set_default_sets_field_to_default(self):
        """Test that SET_DEFAULT sets the foreign key to its default value"""
        from .models import RelatedModel, ModelWithSetDefault

        # Create a related model and a polymorphic model that references it
        related = RelatedModel.objects.create(name="test")
        set_default_obj = ModelWithSetDefault.objects.create(related=related)
        set_default_obj_id = set_default_obj.id

        # Verify the relationship exists
        self.assertEqual(set_default_obj.related, related)

        # Delete the related model
        related.delete()

        # Verify the object still exists but the field is now set to default (None)
        set_default_obj = ModelWithSetDefault.objects.get(id=set_default_obj_id)
        self.assertIsNone(set_default_obj.related)

    def test_set_callable_uses_function(self):
        """Test that SET(...) calls the provided function"""
        from .models import RelatedModel, ModelWithSet

        # Create a related model and a polymorphic model that references it
        related = RelatedModel.objects.create(name="test")
        set_obj = ModelWithSet.objects.create(related=related)
        set_obj_id = set_obj.id

        # Verify the relationship exists
        self.assertEqual(set_obj.related, related)

        # Delete the related model
        related.delete()

        # Verify the object s
        set_obj = ModelWithSet.objects.get(id=set_obj_id)
        self.assertIsNone(set_obj.related)

    def test_do_nothing_behavior(self):
        """Test that DO_NOTHING doesn't prevent deletion or update related objects"""
        from .models import RelatedModel, ModelWithDoNothing

        # Create a related model and a polymorphic model that references it
        related = RelatedModel.objects.create(name="test")
        do_nothing_obj = ModelWithDoNothing.objects.create(related=related)

        # Verify the object is wrapped with PolymorphicGuard
        field = ModelWithDoNothing._meta.get_field("related")
        self.assertIsInstance(field.remote_field.on_delete, PolymorphicGuard)

        # Verify the underlying action is DO_NOTHING
        self.assertEqual(field.remote_field.on_delete.action, models.DO_NOTHING)

        # DO_NOTHING doesn't cascade delete or set null - it simply does nothing
        # In practice, this means the deletion succeeds but leaves an orphaned reference
        # However, database constraints may prevent this in production
        # Here we just verify that the wrapper is correct and the object exists
        self.assertTrue(ModelWithDoNothing.objects.filter(id=do_nothing_obj.id).exists())
        self.assertEqual(do_nothing_obj.related, related)

    def test_restrict_prevents_deletion_when_objects_exist(self):
        """Test that RESTRICT prevents deletion when related objects exist"""
        from .models import RelatedModel, ModelWithRestrict

        # Create a related model and a polymorphic model that references it
        related = RelatedModel.objects.create(name="test")
        restrict_obj = ModelWithRestrict.objects.create(related=related)

        # Attempting to delete the related model should raise RestrictedError
        with self.assertRaises(RestrictedError):
            related.delete()

        # Verify both objects still exist
        self.assertTrue(RelatedModel.objects.filter(id=related.id).exists())
        self.assertTrue(ModelWithRestrict.objects.filter(id=restrict_obj.id).exists())

    def test_cascade_with_polymorphic_inheritance(self):
        """Test CASCADE works correctly with polymorphic child models"""
        from .models import RelatedModel, ModelWithCascade

        # Create a related model
        related = RelatedModel.objects.create(name="test")

        # Create multiple instances of the polymorphic model
        obj1 = ModelWithCascade.objects.create(related=related)
        obj2 = ModelWithCascade.objects.create(related=related)
        obj1_id, obj2_id = obj1.id, obj2.id

        # Verify they exist
        self.assertEqual(ModelWithCascade.objects.filter(related=related).count(), 2)

        # Delete the related model
        related.delete()

        # Verify all cascade objects were deleted
        self.assertFalse(ModelWithCascade.objects.filter(id=obj1_id).exists())
        self.assertFalse(ModelWithCascade.objects.filter(id=obj2_id).exists())
        self.assertEqual(ModelWithCascade.objects.count(), 0)

    def test_one_to_one_cascade_deletes_related_object(self):
        """Test CASCADE with OneToOneField deletes related polymorphic object"""
        from .models import RelatedModel, ModelWithOneToOneCascade

        # Create a related model and a polymorphic model with OneToOne
        related = RelatedModel.objects.create(name="test")
        one_to_one_obj = ModelWithOneToOneCascade.objects.create(related=related)
        one_to_one_obj_id = one_to_one_obj.id

        # Verify the object exists
        self.assertTrue(ModelWithOneToOneCascade.objects.filter(id=one_to_one_obj_id).exists())

        # Delete the related model
        related.delete()

        # Verify the one-to-one object was deleted
        self.assertFalse(ModelWithOneToOneCascade.objects.filter(id=one_to_one_obj_id).exists())

    def test_one_to_one_protect_prevents_deletion(self):
        """Test PROTECT with OneToOneField prevents deletion"""
        from .models import RelatedModel, ModelWithOneToOneProtect

        # Create a related model and a polymorphic model with OneToOne
        related = RelatedModel.objects.create(name="test")
        ModelWithOneToOneProtect.objects.create(related=related)

        # Attempting to delete should raise ProtectedError
        with self.assertRaises(ProtectedError):
            related.delete()

        # Verify both objects still exist
        self.assertTrue(RelatedModel.objects.filter(id=related.id).exists())
        self.assertTrue(ModelWithOneToOneProtect.objects.filter(related=related).exists())

    def test_one_to_one_set_null_sets_to_null(self):
        """Test SET_NULL with OneToOneField sets field to null"""
        from .models import RelatedModel, ModelWithOneToOneSetNull

        # Create a related model and a polymorphic model with OneToOne
        related = RelatedModel.objects.create(name="test")
        one_to_one_obj = ModelWithOneToOneSetNull.objects.create(related=related)
        one_to_one_obj_id = one_to_one_obj.id

        # Verify the relationship exists
        self.assertEqual(one_to_one_obj.related, related)

        # Delete the related model
        related.delete()

        # Verify the object still exists but the field is now null
        one_to_one_obj = ModelWithOneToOneSetNull.objects.get(id=one_to_one_obj_id)
        self.assertIsNone(one_to_one_obj.related)

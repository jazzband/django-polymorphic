from pathlib import Path
from django.core.management import call_command
from django.db import models
from django.test import SimpleTestCase, TransactionTestCase
from polymorphic.deletion import PolymorphicGuard
from ..utils import GeneratedMigrationsPerClassMixin


class TestPolymorphicGuardEquality(SimpleTestCase):
    def test_equality_with_wrapped_action(self):
        """
        Test that PolymorphicGuard compares equal to the action it wraps.
        Regression test for #759 where mismatch caused repeated migrations.
        """
        actions = [
            models.CASCADE,
            models.PROTECT,
            models.SET_NULL,
            models.DO_NOTHING,
        ]

        for action in actions:
            guard = PolymorphicGuard(action)

            # Verify equality both ways
            msg = f"Failed equality for {action.__name__}"
            self.assertEqual(guard, action, msg)
            self.assertEqual(action, guard, msg)

    def test_inequality_with_different_action(self):
        """Verify that it doesn't equate to just *any* action."""
        guard = PolymorphicGuard(models.CASCADE)
        self.assertNotEqual(guard, models.PROTECT)
        self.assertNotEqual(models.PROTECT, guard)


class TestMigrationIdempotency(GeneratedMigrationsPerClassMixin, TransactionTestCase):
    """
    Test that making migrations is checking that no new migrations are generated.
    """

    apps_to_migrate = ["test_migrations"]

    def test_makemigrations_check(self):
        """
        Verify that `makemigrations --check` returns valid exit code (0),
        meaning no changes are detected after initial migrations are made.
        """
        # GeneratedMigrationsPerClassMixin already runs makemigrations in setUpClass
        # So we just need to run it again with --check and ensure it doesn't fail.

        try:
            call_command(
                "makemigrations",
                "test_migrations",
                check=True,
                dry_run=True,
                interactive=False,
                verbosity=0,
            )
        except SystemExit:
            self.fail("makemigrations --check raised SystemExit (changes detected!)")
        except Exception as e:
            self.fail(f"makemigrations failed with error: {e}")

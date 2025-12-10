from django.core.checks import Error, run_checks
from django.test.utils import override_settings
from django.test import SimpleTestCase


@override_settings(
    INSTALLED_APPS=[
        "polymorphic.tests.errata",
        "django.contrib.contenttypes",
        "django.contrib.auth",
    ]
)
class TestErrata(SimpleTestCase):
    def test_reserved_field_name_triggers_system_check(self):
        """Test that using reserved field names triggers polymorphic.E001 system check."""

        # Run the check function directly on the model
        errors = run_checks()

        assert len(errors) == 2, f"Expected 2 system check errors but got {len(errors)}: {errors}"

        # Verify all errors are the correct type
        assert all(isinstance(err, Error) and err.id == "polymorphic.E001" for err in errors), (
            f"Expected all errors to have ID 'polymorphic.E001' but got: {errors}"
        )

        # Verify the error messages mention the correct field names
        error_messages = [err.msg for err in errors]
        assert any("instance_of" in msg for msg in error_messages), (
            f"Expected error for 'instance_of' field but got: {error_messages}"
        )
        assert any("not_instance_of" in msg for msg in error_messages), (
            f"Expected error for 'not_instance_of' field but got: {error_messages}"
        )

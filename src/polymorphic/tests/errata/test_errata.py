from django.core.checks import Error, run_checks
from django.test.utils import override_settings
from django.test import SimpleTestCase, TestCase
from django.core.exceptions import FieldError


@override_settings(
    INSTALLED_APPS=[
        "polymorphic.tests.errata",
        "django.contrib.contenttypes",
        "django.contrib.auth",
    ]
)
class TestErrata(SimpleTestCase):
    def test_system_checks(self):
        """Test that using reserved field names triggers polymorphic.E001 system check."""

        # Run the check function directly on the model
        errors = run_checks()

        assert len(errors) == 5, f"Expected 12 system check errors but got {len(errors)}: {errors}"

        assert errors[0].id == "polymorphic.E001"
        assert errors[0].msg == "Field 'instance_of' on model 'BadModel' is a reserved name."
        assert errors[1].id == "polymorphic.E001"
        assert errors[1].msg == "Field 'not_instance_of' on model 'BadModel' is a reserved name."

        assert errors[2].id == "polymorphic.E002"
        assert (
            errors[2].msg
            == "The migration manager 'errata.BadMigrationManager.objects' is polymorphic."
        )

        assert errors[3].id == "polymorphic.W001"
        assert (
            errors[3].msg == "The default manager errata.BadManager.objects' is not polymorphic."
        )

        assert errors[4].id == "polymorphic.W002"
        assert (
            errors[4].msg
            == "The default manager errata.BadManager.objects' is not using a PolymorphicQuerySet."
        )

    def test_polymorphic_guard_requires_callable(self):
        """Test that PolymorphicGuard raises TypeError if initialized with non-callable."""

        from polymorphic.deletion import PolymorphicGuard

        non_callable_values = [42, "not a function", None, 3.14, [], {}]

        for value in non_callable_values:
            try:
                PolymorphicGuard(value)
            except TypeError as e:
                assert str(e) == "action must be callable", (
                    f"Expected TypeError with message 'action must be callable' but got: {e}"
                )
            else:
                assert False, f"Expected TypeError when initializing PolymorphicGuard with {value}"


class TestFilterErrata(TestCase):
    def test_invalid_field_lookup_raises_field_error(self):
        from polymorphic.tests.models import Participant

        with self.assertRaises(FieldError):
            Participant.objects.get(tests__Model2C___field3="userprofile1")

        with self.assertRaises(FieldError):
            Participant.objects.get(notreal__Model2C___field3="userprofile1")

        with self.assertRaises(FieldError):
            Participant.objects.get(tests__NotReal___field3="userprofile1")

"""
Tests for base.py metaclass edge cases to achieve high-value coverage.
"""

import os
import sys
import warnings
from unittest.mock import patch

from django.db import models
from django.test import TestCase

from polymorphic.base import ManagerInheritanceWarning, PolymorphicModelBase
from polymorphic.managers import PolymorphicManager
from polymorphic.models import PolymorphicModel
from polymorphic.query import PolymorphicQuerySet


class PolymorphicModelBaseTest(TestCase):
    """Test edge cases in PolymorphicModelBase metaclass for manager validation."""

    def test_validate_model_manager_with_non_polymorphic_manager(self):
        """Test warning when manager is not a PolymorphicManager subclass"""
        # Create a regular Django manager (not PolymorphicManager)
        regular_manager = models.Manager()

        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            PolymorphicModelBase.validate_model_manager(regular_manager, "TestModel", "objects")

            # Should have emitted ManagerInheritanceWarning
            assert len(w) == 1
            assert issubclass(w[0].category, ManagerInheritanceWarning)
            assert "must be a subclass of PolymorphicManager" in str(w[0].message)
            assert "TestModel.objects" in str(w[0].message)

    def test_validate_model_manager_with_wrong_queryset_class(self):
        """Test warning when manager has non-Polymorphic QuerySet queryset_class"""

        # Create a PolymorphicManager with wrong queryset_class
        class BadQuerySet(models.QuerySet):
            pass

        class BadManager(PolymorphicManager):
            queryset_class = BadQuerySet

        bad_manager = BadManager()

        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            PolymorphicModelBase.validate_model_manager(bad_manager, "TestModel", "objects")

            # Should have emitted ManagerInheritanceWarning
            assert len(w) == 1
            assert issubclass(w[0].category, ManagerInheritanceWarning)
            assert "not a subclass of PolymorphicQuerySet" in str(w[0].message)
            assert "TestModel.objects" in str(w[0].message)

    def test_validate_model_manager_with_no_queryset_class(self):
        """Test warning when manager has no queryset_class attribute"""

        class ManagerWithoutQuerySet(PolymorphicManager):
            queryset_class = None  # Set to None instead of deleting

        manager = ManagerWithoutQuerySet()

        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            PolymorphicModelBase.validate_model_manager(manager, "TestModel", "objects")

            # Should have emitted ManagerInheritanceWarning
            assert len(w) == 1
            assert issubclass(w[0].category, ManagerInheritanceWarning)
            assert "not a subclass of PolymorphicQuerySet" in str(w[0].message)


class DumpdataIntegrationTest(TestCase):
    """Test the dumpdata command detection in _default_manager property."""

    def test_default_manager_with_dumpdata_command(self):
        """Test that _default_manager returns base_objects when called from dumpdata"""
        from polymorphic.tests.models import Model2A

        # Mock sys.argv to simulate running dumpdata command
        original_argv = sys.argv
        try:
            sys.argv = ["manage.py", "dumpdata"]

            # Mock inspect.stack to simulate being called from dumpdata.py
            # inspect.stack() returns a list of FrameInfo namedtuples
            # FrameInfo has: frame, filename, lineno, function, code_context, index
            # The code does: frm = inspect.stack()[1], then checks: frm[1] (which is filename)
            import collections

            FrameInfo = collections.namedtuple(
                "FrameInfo", ["frame", "filename", "lineno", "function", "code_context", "index"]
            )

            # Use os.path.join to generate platform-specific path (Windows: \\, Unix: /)
            dumpdata_path = os.path.join(
                "path", "to", "django", "core", "management", "commands", "dumpdata.py"
            )

            fake_frame_info = FrameInfo(
                frame=None,
                filename=dumpdata_path,
                lineno=100,
                function="handle",
                code_context=None,
                index=None,
            )

            fake_stack = [
                None,  # Current frame (index 0)
                fake_frame_info,  # Caller frame (index 1) - this is what gets accessed
            ]

            with patch("inspect.stack", return_value=fake_stack):
                # Access _default_manager should return base_objects
                manager = Model2A._default_manager

                # The manager should be a non-polymorphic manager
                # (base_objects returns a regular models.Manager)
                assert isinstance(manager, models.Manager)
                assert manager.name == "base_objects"

        finally:
            sys.argv = original_argv

    def test_default_manager_without_dumpdata_command(self):
        """Test that _default_manager returns normal polymorphic manager when not dumpdata"""
        from polymorphic.tests.models import Model2A

        # Normal access (not from dumpdata)
        manager = Model2A._default_manager

        # Should be a PolymorphicManager
        assert isinstance(manager, PolymorphicManager)


class PrimaryKeyNameTest(TestCase):
    def test_polymorphic_primary_key_name_correctness(self):
        """
        Verify that polymorphic_primary_key_name points to the root pk in the
        inheritance chain.

        Regression test for #758. Will go away in version 5.0
        """
        from polymorphic.tests.models import (
            CustomPkInherit,
            CustomPkBase,
            Model2A,
            Model2B,
            Model2C,
        )

        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            self.assertEqual(
                CustomPkInherit.polymorphic_primary_key_name, CustomPkBase._meta.pk.attname
            )
            self.assertEqual(CustomPkInherit.polymorphic_primary_key_name, "id")

            self.assertEqual(Model2A.polymorphic_primary_key_name, Model2A._meta.pk.attname)
            self.assertEqual(Model2A.polymorphic_primary_key_name, "id")

            self.assertEqual(Model2B.polymorphic_primary_key_name, Model2A._meta.pk.attname)
            self.assertEqual(Model2B.polymorphic_primary_key_name, "id")

            self.assertEqual(Model2C.polymorphic_primary_key_name, Model2A._meta.pk.attname)
            self.assertEqual(Model2C.polymorphic_primary_key_name, "id")

            assert w[0].category is DeprecationWarning
            assert "polymorphic_primary_key_name" in str(w[0].message)

    def test_multiple_inheritance_pk_name(self):
        """
        Verify multiple inheritance scenarios.
        """
        from polymorphic.tests.models import Enhance_Inherit, Enhance_Base

        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            self.assertEqual(
                Enhance_Inherit.polymorphic_primary_key_name, Enhance_Base._meta.pk.attname
            )
            self.assertEqual(Enhance_Inherit.polymorphic_primary_key_name, "base_id")
            assert w[0].category is DeprecationWarning
            assert "polymorphic_primary_key_name" in str(w[0].message)

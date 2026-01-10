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

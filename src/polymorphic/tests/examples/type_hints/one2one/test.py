import typing as t
from django.db.models.fields.reverse_related import OneToOneRel
from typing_extensions import assert_type
from django.test import TestCase
from polymorphic.managers import PolymorphicQuerySet

# from django.db import models
from .models import ParentModel, Child1, Child2, RelatedModel


class TypeHintsOne2OneTest(TestCase):
    def test_type_hints(self):
        related1 = RelatedModel.objects.create()
        related2 = RelatedModel.objects.create()
        related3 = RelatedModel.objects.create()
        parent = ParentModel.objects.create(related_forward=related1)
        child1 = Child1.objects.create(related_forward=related2)
        Child2.objects.create(related_forward=related3)
        assert_type(
            related1.parent_forward, t.Optional[ParentModel | Child1 | Child2]
        )
        assert_type(related1.parent_reverse, ParentModel | Child1 | Child2)

        related1.parent_forward = child1
        related1.save()

        assert_type(RelatedModel.parent_reverse.related, OneToOneRel)
        _1: PolymorphicQuerySet[ParentModel | Child1 | Child2, ParentModel] = (
            RelatedModel.parent_reverse.get_queryset()
        )
        assert _1.all().count() == 3

        # assert_type(RelatedModel.parent_forward.related, OneToOneRel)
        _2: PolymorphicQuerySet[ParentModel | Child1 | Child2, ParentModel] = (
            RelatedModel.parent_forward.get_queryset()
        )
        assert _2.all().count() == 3

        _3: ParentModel | Child1 | Child2 = related1.parent_reverse
        assert _3 == parent

        _4: t.Optional[ParentModel | Child1 | Child2] = related1.parent_forward
        assert _4 == child1

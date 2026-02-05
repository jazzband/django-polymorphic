import typing as t
from typing_extensions import assert_type
from django.test import TestCase
from .models import ParentModel, Child1, Child2, RelatedModel


class TypeHintsFKTest(TestCase):
    def test_type_hints(self):
        related = RelatedModel.objects.create()
        parent = ParentModel.objects.create(related_forward=related)
        child1 = Child1.objects.create(related_forward=related)
        child2 = Child2.objects.create(related_forward=related)

        assert_type(related.parent, t.Optional[ParentModel | Child1 | Child2])

        related.parent = child1
        related.save()

        if t.TYPE_CHECKING:
            from django.db.models.fields.related import ForeignKey
            from django.db.models.fields.reverse_related import ManyToOneRel

            assert_type(
                RelatedModel.parents_reverse.field, ForeignKey[t.Any, t.Any]
            )
            assert_type(RelatedModel.parents_reverse.rel, ManyToOneRel)

        _1: t.Optional[ParentModel | Child1 | Child2] = (
            related.parents_reverse.first()
        )
        assert _1 == parent

        _2: t.Optional[ParentModel | Child1 | Child2] = (
            related.parents_reverse.filter().first()
        )
        assert _2 == parent

        _3: t.Optional[ParentModel] = (
            related.parents_reverse.non_polymorphic().last()
        )
        assert _3 == ParentModel.objects.non_polymorphic().get(pk=child2.pk)

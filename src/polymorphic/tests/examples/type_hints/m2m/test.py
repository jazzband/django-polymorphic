import typing as t
from django.test import TestCase
from django.db import models

# from django.db import models
from .models import (
    ParentModel,
    Child1,
    Child2,
    RelatedModel,
    PolyThrough,
    ThroughChild,
)


class TypeHintsM2MTest(TestCase):
    def test_type_hints(self):
        parent = ParentModel.objects.create()
        child1 = Child1.objects.create()
        child2 = Child2.objects.create()
        related1 = RelatedModel.objects.create()
        related2 = RelatedModel.objects.create()

        _t1 = PolyThrough.objects.create(parent=child1, related=related1)

        _t2 = ThroughChild.objects.create(parent=child2, related=related2)

        related1.to_parents.add(parent)
        related1.to_related_reverse.add(child2)
        related2.to_parents.add(child2)

        related1.refresh_from_db()
        assert set(related1.to_parents.all()) == {parent}
        assert set(related2.to_parents.all()) == {child2}
        assert set(related1.to_related_reverse.all()) == {child1, child2}
        assert set(related2.to_related_reverse.all()) == {child2}

        assert parent.to_related.count() == 0
        assert set(child1.to_related.all()) == {related1}
        assert set(child2.to_related.all()) == {related1, related2}

        through1: type[PolyThrough] = parent.to_related.through
        assert through1.objects.count() == 3

        tlist1: t.List[PolyThrough | ThroughChild] = list(
            parent.to_related.through.objects.all()
        )
        assert len(tlist1) == 3

        _1: t.List[PolyThrough] = list(
            parent.to_related.through.objects.non_polymorphic()
        )
        assert len(_1) == 3

        _2: t.List[ParentModel | Child1 | Child2] = list(
            related1.to_related_reverse.all()
        )
        assert set(_2) == {child1, child2}

        _3: t.List[ParentModel | Child1 | Child2] = list(
            related1.to_parents.all()
        )

        assert set(_3) == {parent}

        _through2: type[models.Model] = related1.to_parents.through
        _through3: type[PolyThrough] = related1.to_related_reverse.through

        assert _through2.objects.count() == 2  # type: ignore[attr-defined]

        assert set(_through3.objects.all()) == {
            _t1,
            _t2,
            PolyThrough.objects.last(),
        }

        _4: t.List[ParentModel] = list(
            related1.to_related_reverse.non_polymorphic()
        )
        assert set(_4) == set(
            ParentModel.objects.non_polymorphic().filter(
                pk__in=[child1.pk, child2.pk]
            )
        )

        _5: t.List[ParentModel] = list(
            related1.to_parents.all().non_polymorphic()
        )
        assert set(_5) == {parent}

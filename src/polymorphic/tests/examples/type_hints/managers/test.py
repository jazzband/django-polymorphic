import typing as t
from django.test import TestCase
from .models import ParentModel, Child1, Child2


class TypeHintsManagersTest(TestCase):
    def test_type_hints(self):

        parent = ParentModel.objects.create()
        child1 = Child1.objects.create()
        child2 = Child2.objects.create()

        _1: t.Optional[ParentModel | Child1 | Child2] = (
            ParentModel.objects.first()
        )
        assert _1 == parent or _1 == child1 or _1 == child2
        assert _1 == parent
        _2: t.Optional[ParentModel | Child1 | Child2] = (
            ParentModel.objects.order_by("pk").first()
        )
        assert _2 == parent
        _3: t.Optional[Child1 | Child2] = Child1.objects.first()
        assert _3 == child1 or _3 == child2
        _4: Child1 | Child2 = Child1.objects.filter().all().get(pk=child1.pk)
        assert _4 == child1
        _5: t.Optional[Child2] = Child2.objects.first()
        assert _5 == child2
        _6: Child2 = Child2.objects.filter().get(pk=child2.pk)
        assert _6 == child2

        assert ParentModel.objects.count() == 3
        assert Child1.objects.count() == 2
        assert Child2.objects.count() == 1

        # mypy has trouble with these - they work on pyright/pylance. I consider this
        # a failing of mypy type inference not a deficiency in our typing - for now
        # we can ignore the errors
        _7: t.Optional[ParentModel] = (
            ParentModel.objects.non_polymorphic().first()  # type: ignore[assignment]
        )
        assert _7 == parent
        _8: t.Optional[ParentModel] = (
            ParentModel.objects.all().non_polymorphic().first()  # type: ignore[assignment]
        )
        assert _8 == parent
        _9: t.Optional[Child1] = Child1.objects.non_polymorphic().first()  # type: ignore[assignment]
        assert _9 == child1
        _10: t.Optional[Child1] = (
            Child1.objects.filter().non_polymorphic().all().first()  # type: ignore[assignment]
        )
        assert _10 == child1
        _11: t.Optional[Child2] = Child2.objects.non_polymorphic().first()
        assert _11 == child2
        _12: Child2 = (
            Child2.objects.filter().non_polymorphic().get(pk=child2.pk)
        )
        assert _12 == child2

        _13: t.Optional[ParentModel] = ParentModel.objects.instance_of(
            ParentModel
        ).first()
        assert _13 == parent
        _14: t.Optional[ParentModel] = (
            ParentModel.objects.all().instance_of(ParentModel).first()
        )
        assert _14 == parent

        _15: t.Optional[Child1] = ParentModel.objects.instance_of(
            Child1
        ).first()
        assert _15 == child1
        _16: t.Optional[Child1] = (
            ParentModel.objects.all().instance_of(Child1).first()
        )
        assert _16 == child1
        _17: t.Optional[Child2] = ParentModel.objects.instance_of(
            Child2
        ).first()
        assert _17 == child2
        _18: t.Optional[Child2] = (
            ParentModel.objects.all().instance_of(Child2).first()
        )
        assert _18 == child2

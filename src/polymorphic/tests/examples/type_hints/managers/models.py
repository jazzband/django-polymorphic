from __future__ import annotations
import typing as t
from typing_extensions import Self
from polymorphic.models import PolymorphicModel
from polymorphic.managers import PolymorphicManager


class ParentModel(PolymorphicModel):
    # fmt: off
    # If you want a polymorphic manager with type hint support you can
    # override the default one like this:
    objects: t.ClassVar[
        PolymorphicManager[
            Self | Child1 | Child2,  # union of all polymorphic types
            Self,                    # the base type (for non_polymorphic)
        ]
    ] = PolymorphicManager()
    # fmt: on


class Child1(ParentModel):
    # you may also override the type hints for the child default
    # managers to narrow the filter returns at this level
    objects: t.ClassVar[PolymorphicManager[Self | Child2, Self]]


class Child2(Child1):
    objects: t.ClassVar[PolymorphicManager[Self, Self]]

from __future__ import annotations
from typing import ClassVar
from django.db import models
from polymorphic.models import PolymorphicModel
from polymorphic.managers import (
    PolymorphicManager,
    PolymorphicManyToManyDescriptor,
    PolymorphicForwardManyToOneDescriptor,
    PolymorphicReverseManyToOneDescriptor,
)


class ParentModel(PolymorphicModel):
    to_related = models.ManyToManyField(  # type: ignore[var-annotated]
        "RelatedModel", related_name="to_related_reverse", through="PolyThrough"
    )

    parents: PolymorphicReverseManyToOneDescriptor[
        ParentModel | Child1 | Child2, ParentModel
    ]

    objects: ClassVar[
        PolymorphicManager[ParentModel | Child1 | Child2, ParentModel]
    ]


class Child1(ParentModel):
    pass


class Child2(Child1):
    pass


class PolyThrough(PolymorphicModel):
    parent: PolymorphicForwardManyToOneDescriptor[
        ParentModel | Child1 | Child2, ParentModel
    ] = models.ForeignKey(  # type: ignore[assignment]
        ParentModel, on_delete=models.CASCADE, related_name="parents"
    )

    related = models.ForeignKey("RelatedModel", on_delete=models.CASCADE)

    objects: ClassVar[
        PolymorphicManager[PolyThrough | ThroughChild, PolyThrough]
    ]


class ThroughChild(PolyThrough):
    pass


class RelatedModel(models.Model):
    # fmt: off
    # ManyToMany Descriptor Type Hint:
    #   1. Class Attribute: ManyToManyDescriptor
    #   2. Instance attribute: PolymorphicManager for related type(s)
    to_parents: PolymorphicManyToManyDescriptor[
        ParentModel | Child1 | Child2,  # all possible polymorphic types
        ParentModel,                    # the base type (for non_polymorphic)
                                        # no custom through model
    ] = models.ManyToManyField(         # type: ignore[assignment]
        "ParentModel",
        related_name="to_parents_reverse"
    )

    # ManyToMany Descriptor for the reverse relation
    #   1. Class Attribute: ManyToManyDescriptor
    #   2. Instance attribute: PolymorphicManager for related type(s)
    to_related_reverse: PolymorphicManyToManyDescriptor[
        ParentModel | Child1 | Child2,
        ParentModel,
        PolyThrough  # custom through model (may be polymorphic!)
    ]
    # fmt: on

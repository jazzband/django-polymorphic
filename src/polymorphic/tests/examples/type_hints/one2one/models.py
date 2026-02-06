from django.db import models
from polymorphic.models import PolymorphicModel
from polymorphic.managers import (
    PolymorphicForwardOneToOneDescriptor,
    PolymorphicReverseOneToOneDescriptor,
    Nullable,  # Alias for typing.Literal[True]
)


class ParentModel(PolymorphicModel):
    related_forward = models.OneToOneField(
        "RelatedModel", on_delete=models.CASCADE, related_name="parent_reverse"
    )


class Child1(ParentModel):
    pass


class Child2(Child1):
    pass


class RelatedModel(models.Model):
    # fmt: off
    # Forward Relation Descriptor Type Hint:
    #   1. Class Attribute: ForwardOneToOneDescriptor
    #   2. Instance attribute: Union of all listed model types or None
    parent_forward: PolymorphicForwardOneToOneDescriptor[
        ParentModel | Child1 | Child2,  # all possible polymorphic types
        ParentModel,                    # the base type (for non_polymorphic)
        Nullable,                       # when null=True
    ] = models.OneToOneField(           # type: ignore[assignment]
        "ParentModel",
        on_delete=models.CASCADE,
        null=True
    )

    # Reverse Relation Descriptor Type Hint:
    #   1. Class Attribute: ReverseOneToOneDescriptor
    #   2. Instance attribute: Union of all listed model types
    parent_reverse: PolymorphicReverseOneToOneDescriptor[
        ParentModel | Child1 | Child2,  # possible polymorphic types
        ParentModel,                    # the base type (for non_polymorphic)
                                        # nullable defaults to False
    ]
    # fmt: on

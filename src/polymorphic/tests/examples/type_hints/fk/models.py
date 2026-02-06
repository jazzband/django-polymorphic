from django.db import models
from polymorphic.models import PolymorphicModel
from polymorphic.managers import (
    PolymorphicForwardManyToOneDescriptor,
    PolymorphicReverseManyToOneDescriptor,
    Nullable,  # Alias for typing.Literal[True]
)


class ParentModel(PolymorphicModel):
    related_forward = models.ForeignKey(
        "RelatedModel", on_delete=models.CASCADE, related_name="parents_reverse"
    )


class Child1(ParentModel):
    pass


class Child2(Child1):
    pass


class RelatedModel(models.Model):
    # fmt: off
    # Foreign Key Descriptor Type Hint:
    #   1. Class Attribute: ForwardManyToOneDescriptor
    #   2. Instance attribute: Union of all listed model types or None
    parent: PolymorphicForwardManyToOneDescriptor[
        ParentModel | Child1 | Child2,  # all possible polymorphic types
        ParentModel,                    # the base type (for non_polymorphic)
        Nullable,                       # when null=True
    ] = models.ForeignKey(              # type: ignore[assignment]
        ParentModel,
        on_delete=models.CASCADE,
        null=True,
    )

    # Reverse FK Relation Descriptor Type Hint:
    #   1. Class Attribute: ReverseManyToOneDescriptor
    #   2. Instance attribute: Union of all listed model types
    parents_reverse: PolymorphicReverseManyToOneDescriptor[
        ParentModel | Child1 | Child2,  # all possible polymorphic types
        ParentModel,                    # the base type (for non_polymorphic)
                                        # nullable defaults to False
    ]
    # fmt: on

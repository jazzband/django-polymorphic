from django.db.models.fields.related_descriptors import (
    ForwardOneToOneDescriptor,
    ReverseOneToOneDescriptor,
)


class NonPolymorphicForwardOneToOneDescriptor(ForwardOneToOneDescriptor):
    """
    A custom descriptor for forward OneToOne relations to polymorphic models that
    returns non-polymorphic instances. This is used for the parent to child links
    in multi-table polymorphic models.
    """

    def get_queryset(self, **hints):
        return (
            (
                getattr(
                    self.field.remote_field.model,
                    "_base_objects",
                    # don't fail if we've been used on a non-poly model
                    self.field.remote_field.model._base_manager,
                )
            )
            .db_manager(hints=hints)
            .all()
        )


class NonPolymorphicReverseOneToOneDescriptor(ReverseOneToOneDescriptor):
    """
    A custom descriptor for reverse OneToOne relations to polymorphic models that
    returns non-polymorphic instances. This is used for the child to parent links
    in multi-table polymorphic models.
    """

    def get_queryset(self, **hints):
        return (
            (
                getattr(
                    self.related.related_model,
                    "_base_objects",
                    # don't fail if we've been used on a non-poly model
                    self.related.related_model._base_manager,
                )
            )
            .db_manager(hints=hints)
            .all()
        )

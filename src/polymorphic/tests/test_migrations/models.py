from django.db import models
from polymorphic.models import PolymorphicModel


def get_default_related():
    """Default function for SET() callable"""
    return None


class RelatedModel(models.Model):
    """A regular non-polymorphic model that will be referenced"""

    name = models.CharField(max_length=100)


class BasePolyModel(PolymorphicModel):
    """
    Base polymorphic model to test that PolymorphicGuard wraps
    on_delete handlers properly and serializes them correctly.
    """

    name = models.CharField(max_length=100)


class ChildPolyModel(BasePolyModel):
    """Child polymorphic model"""

    description = models.CharField(max_length=200, blank=True)


class GrandChildPolyModel(ChildPolyModel):
    """Grandchild polymorphic model"""

    extra_info = models.CharField(max_length=200, blank=True)


# Models with ForeignKey using different on_delete behaviors
# These should all be wrapped with PolymorphicGuard automatically


class ModelWithCascade(PolymorphicModel):
    """Test CASCADE on_delete"""

    related = models.ForeignKey(RelatedModel, on_delete=models.CASCADE)


class ModelWithProtect(PolymorphicModel):
    """Test PROTECT on_delete"""

    related = models.ForeignKey(RelatedModel, on_delete=models.PROTECT)


class ModelWithSetNull(PolymorphicModel):
    """Test SET_NULL on_delete"""

    related = models.ForeignKey(RelatedModel, on_delete=models.SET_NULL, null=True)


class ModelWithSetDefault(PolymorphicModel):
    """Test SET_DEFAULT on_delete"""

    related = models.ForeignKey(
        RelatedModel, on_delete=models.SET_DEFAULT, null=True, default=None
    )


class ModelWithSet(PolymorphicModel):
    """Test SET(...) on_delete"""

    related = models.ForeignKey(RelatedModel, on_delete=models.SET(get_default_related), null=True)


class ModelWithDoNothing(PolymorphicModel):
    """Test DO_NOTHING on_delete"""

    related = models.ForeignKey(RelatedModel, on_delete=models.DO_NOTHING)


class ModelWithRestrict(PolymorphicModel):
    """Test RESTRICT on_delete"""

    related = models.ForeignKey(RelatedModel, on_delete=models.RESTRICT)


# OneToOneField tests


class ModelWithOneToOneCascade(PolymorphicModel):
    """Test CASCADE on_delete with OneToOneField"""

    related = models.OneToOneField(RelatedModel, on_delete=models.CASCADE)


class ModelWithOneToOneProtect(PolymorphicModel):
    """Test PROTECT on_delete with OneToOneField"""

    related = models.OneToOneField(
        RelatedModel, on_delete=models.PROTECT, related_name="one_to_one_protect"
    )


class ModelWithOneToOneSetNull(PolymorphicModel):
    """Test SET_NULL on_delete with OneToOneField"""

    related = models.OneToOneField(
        RelatedModel, on_delete=models.SET_NULL, null=True, related_name="one_to_one_set_null"
    )

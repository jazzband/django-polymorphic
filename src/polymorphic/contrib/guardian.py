from django.contrib.contenttypes.models import ContentType

from ..models import PolymorphicModel
from ..utils import get_base_polymorphic_model


def get_polymorphic_base_content_type(obj):
    """
    Helper function to return the base polymorphic content type id. This should used
    with django-guardian and the ``GUARDIAN_GET_CONTENT_TYPE`` option.

    See the django-guardian documentation for more information:

    https://django-guardian.readthedocs.io/en/latest/configuration
    """
    model_type = obj if isinstance(obj, type) else type(obj)
    if issubclass(model_type, PolymorphicModel) and (
        base := get_base_polymorphic_model(model_type)
    ):
        return ContentType.objects.get_for_model(base)
    return ContentType.objects.get_for_model(model_type)

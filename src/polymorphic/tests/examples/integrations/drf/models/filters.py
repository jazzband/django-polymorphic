"""
https://github.com/jazzband/django-polymorphic/issues/520
"""

from polymorphic.models import PolymorphicModel
from django.db import models
from django.contrib.auth import get_user_model


class Annotator(PolymorphicModel):
    pass


class UserAnnotator(Annotator):
    user = models.ForeignKey(
        get_user_model(), on_delete=models.PROTECT, default=None
    )


class AiModelAnnotator(Annotator):
    ai_model = models.CharField(max_length=255)
    version = models.CharField(max_length=16, default=None, null=True)


class Data(models.Model):
    annotator = models.ForeignKey(Annotator, on_delete=models.PROTECT)

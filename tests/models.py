from django.db import models

from polymorphic.models import PolymorphicModel


class BlogBase(PolymorphicModel):
    name = models.CharField(max_length=10)
    slug = models.SlugField(max_length=255, unique=True)


class BlogOne(BlogBase):
    info = models.CharField(max_length=10)


class BlogTwo(BlogBase):
    pass

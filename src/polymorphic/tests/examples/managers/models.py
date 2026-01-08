from django.db import models
from polymorphic.models import PolymorphicModel
from polymorphic.managers import PolymorphicManager


class ArticleManager(PolymorphicManager):
    def get_by_natural_key(self, slug):
        return self.non_polymorphic().get(slug=slug)


class Article(PolymorphicModel):
    slug = models.SlugField(unique=True)
    title = models.CharField(max_length=200)
    objects = ArticleManager()

    def natural_key(self):
        return (self.slug,)


class BlogPost(Article):
    author = models.CharField(max_length=100)

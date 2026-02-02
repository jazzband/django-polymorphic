import typing as t
from typing_extensions import Self
from django.db import models
from polymorphic.models import PolymorphicModel
from polymorphic.managers import PolymorphicManager


class Article(PolymorphicModel):
    title = models.CharField(max_length=100)
    content = models.TextField()
    created = models.DateTimeField(auto_now_add=True)

    objects: t.ClassVar[PolymorphicManager[Self | "BlogPost" | "NewsArticle"]]

    def __str__(self):
        return self.title


class BlogPost(Article):
    author = models.CharField(max_length=100)


class NewsArticle(Article):
    source = models.CharField(max_length=100)


class Topic(models.Model):
    name = models.CharField(max_length=50)
    articles = models.ManyToManyField(Article, related_name="topics")

    def __str__(self):
        return self.name

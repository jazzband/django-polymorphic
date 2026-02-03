from __future__ import annotations
import typing as t
from typing_extensions import Self
from django.db import models
from polymorphic.models import PolymorphicModel
from polymorphic.managers import PolymorphicManager

if t.TYPE_CHECKING:
    from polymorphic.managers import (
        PolymorphicManyToManyDescriptor,
        PolymorphicRelatedManager,
    )


class Article(PolymorphicModel):
    title = models.CharField(max_length=100)

    outlet: "MediaOutlet" | "Newspaper" | "OnlineBlog" = models.ForeignKey(  # type: ignore[assignment]
        "MediaOutlet", on_delete=models.CASCADE, related_name="articles"
    )

    objects: t.ClassVar[
        PolymorphicManager[Self | "BlogPost" | "NewsArticle", Self]
    ] = PolymorphicManager()

    topics: PolymorphicManyToManyDescriptor[
        "Topic" | "LocationTopic" | "EditorialTopic", "Topic"
    ]


class BlogPost(Article):
    author = models.CharField(max_length=100)


class NewsArticle(Article):
    source = models.CharField(max_length=100)


class Topic(PolymorphicModel):
    name = models.CharField(max_length=50)
    articles: PolymorphicManyToManyDescriptor[
        Article | BlogPost | NewsArticle, Article
    ] = models.ManyToManyField(Article, related_name="topics")  # type: ignore[assignment]

    articles2 = models.ManyToManyField(Article, related_name="topics2")
    if t.TYPE_CHECKING:
        objects: t.ClassVar[
            PolymorphicManager[Self | "LocationTopic" | "EditorialTopic", Self]
        ]


class LocationTopic(Topic):
    location = models.CharField(max_length=100)


class EditorialTopic(Topic):
    editor = models.CharField(max_length=100)


class MediaOutlet(PolymorphicModel):
    name = models.CharField(max_length=100)

    articles: PolymorphicRelatedManager[
        Article | NewsArticle | BlogPost, "Article"
    ]


class Newspaper(MediaOutlet):
    service_area = models.CharField(max_length=100)


class OnlineBlog(MediaOutlet):
    url = models.URLField()

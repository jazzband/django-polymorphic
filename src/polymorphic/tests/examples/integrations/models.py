from django.db import models
from polymorphic.models import PolymorphicModel


class Article(PolymorphicModel):
    title = models.CharField(max_length=100)
    content = models.TextField()
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class BlogPost(Article):
    author = models.CharField(max_length=100)


class NewsArticle(Article):
    source = models.CharField(max_length=100)

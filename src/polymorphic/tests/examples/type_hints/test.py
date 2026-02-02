from django.test import TestCase
from .models import Article, BlogPost, NewsArticle


class TypeHintsTest(TestCase):
    def test_type_hints_example_models(self):
        # Just a placeholder test to ensure the example models file is included in test
        # runs

        objs: list[Article | BlogPost | NewsArticle] = list(Article.objects.all())

        objs2: list[BlogPost] = list(Article.objects.instance_of(BlogPost).all())
        objs3: list[BlogPost | NewsArticle] = list(
            Article.objects.instance_of(NewsArticle, BlogPost).all()
        )

        assert len(objs) == 0
        assert len(objs2) == 0
        assert len(objs3) == 0

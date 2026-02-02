from django.test import TestCase
from .models import Article, BlogPost, NewsArticle


class TypeHintsTest(TestCase):
    def test_type_hints_example_models(self):
        # Just a placeholder test to ensure the example models file is included in test
        # runs

        Article.objects.create(title="Test Article", content="This is a test article.")
        BlogPost.objects.create(
            title="Test Blog Post", content="This is a test blog post.", author="Author A"
        )
        NewsArticle.objects.create(
            title="Test News Article", content="This is a test news article.", source="Source A"
        )

        objs: list[Article | BlogPost | NewsArticle] = list(Article.objects.all())

        objs2: list[BlogPost] = list(Article.objects.instance_of(BlogPost).all())
        objs3: list[BlogPost | NewsArticle] = list(
            Article.objects.instance_of(NewsArticle, BlogPost).all()
        )

        objs4: list[BlogPost] = list(Article.objects.all().instance_of(BlogPost).all())
        objs5: list[BlogPost | NewsArticle] = list(
            Article.objects.all().instance_of(NewsArticle, BlogPost).all()
        )

        assert len(objs) == 3
        assert len(objs2) == 1
        assert len(objs3) == 2
        assert len(objs4) == 1
        assert len(objs5) == 2

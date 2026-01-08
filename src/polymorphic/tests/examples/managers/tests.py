from django.test import TestCase
from django.core import serializers
from .models import Article, BlogPost


class NaturalKeyTests(TestCase):
    def test_natural_key_serialization(self):
        # Create objects
        Article.objects.create(slug="article-1", title="First Article")
        BlogPost.objects.create(slug="blog-post-1", title="First Blog Post", author="John Doe")

        # Serialize using natural keys
        data = serializers.serialize(
            "json",
            Article.objects.all(),
            use_natural_foreign_keys=True,
            use_natural_primary_keys=True,
        )

        # Verify serialization contains natural keys (slugs)
        self.assertIn("article-1", data)
        self.assertIn("blog-post-1", data)

        # Deserialize
        for obj in serializers.deserialize("json", data):
            obj.save()

        # Verify objects still exist and are correct types
        self.assertEqual(Article.objects.count(), 2)
        self.assertEqual(BlogPost.objects.count(), 1)

        a1 = Article.objects.get(slug="article-1")
        self.assertIsInstance(a1, Article)
        self.assertNotIsInstance(a1, BlogPost)

        b1 = Article.objects.get(slug="blog-post-1")
        self.assertIsInstance(b1, BlogPost)

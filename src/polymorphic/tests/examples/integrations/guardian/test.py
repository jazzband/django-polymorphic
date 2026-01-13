from unittest import skipUnless
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.test import TestCase

try:
    import guardian  # noqa: F401

    GUARDIAN_INSTALLED = True
except ImportError:
    GUARDIAN_INSTALLED = False

from ..models import Article, BlogPost, NewsArticle
from ....models import PlainD
from polymorphic.contrib.guardian import get_polymorphic_base_content_type


User = get_user_model()


@skipUnless(GUARDIAN_INSTALLED, "django-guardian is not installed")
class GuardianIntegrationTests(TestCase):
    """
    Tests for django-guardian integration with polymorphic models.

    These tests verify that get_polymorphic_base_content_type returns the correct
    base content type for polymorphic models, which is essential for django-guardian
    to work correctly with polymorphic inheritance.

    When configured with GUARDIAN_GET_CONTENT_TYPE pointing to this function,
    django-guardian will assign permissions to the base polymorphic model rather
    than the specific child model, ensuring consistent permission handling across
    the polymorphic hierarchy.
    """

    def setUp(self):
        """Create test objects."""
        self.user = User.objects.create_user(username="testuser", password="testpass")
        self.blog_post = BlogPost.objects.create(
            title="Test Blog", content="Blog content", author="Blog Author"
        )
        self.news_article = NewsArticle.objects.create(
            title="Test News", content="News content", source="News Source"
        )

    def test_non_polymorphic_model(self):
        """Test that non-polymorphic models return their own content type."""
        plain_d = PlainD.objects.create(field1="Plain D", field2="Plain D")
        ctype = get_polymorphic_base_content_type(plain_d)

        expected_ctype = ContentType.objects.get_for_model(PlainD)
        self.assertEqual(ctype, expected_ctype)
        self.assertEqual(ctype.model, "plaind")

    def test_get_polymorphic_base_content_type_for_child_model(self):
        """Test that get_polymorphic_base_content_type returns base type for child models."""
        # Get content type for BlogPost instance
        blog_ctype = get_polymorphic_base_content_type(self.blog_post)

        # Should return Article content type, not BlogPost
        article_ctype = ContentType.objects.get_for_model(Article, for_concrete_model=False)
        self.assertEqual(blog_ctype, article_ctype)
        self.assertNotEqual(blog_ctype.model, "blogpost")
        self.assertEqual(blog_ctype.model, "article")

    def test_get_polymorphic_base_content_type_for_different_child_models(self):
        """Test that different child models return the same base content type."""
        blog_ctype = get_polymorphic_base_content_type(self.blog_post)
        news_ctype = get_polymorphic_base_content_type(self.news_article)

        # Both should return the same Article content type
        self.assertEqual(blog_ctype, news_ctype)
        self.assertEqual(blog_ctype.model, "article")

    def test_get_polymorphic_base_content_type_for_base_model(self):
        """Test that base polymorphic models return their own content type."""
        article = Article.objects.create(title="Plain Article", content="Plain content")
        article_ctype = get_polymorphic_base_content_type(article)

        expected_ctype = ContentType.objects.get_for_model(Article, for_concrete_model=False)
        self.assertEqual(article_ctype, expected_ctype)
        self.assertEqual(article_ctype.model, "article")

    def test_get_polymorphic_base_content_type_for_non_polymorphic_model(self):
        """Test that non-polymorphic models return their own content type."""
        user_ctype = get_polymorphic_base_content_type(self.user)

        expected_ctype = ContentType.objects.get_for_model(User)
        self.assertEqual(user_ctype, expected_ctype)

    def test_get_polymorphic_base_content_type_with_model_class(self):
        """Test that the function works with model classes, not just instances."""
        # Test with a model class instead of instance
        blog_class_ctype = get_polymorphic_base_content_type(BlogPost)

        article_ctype = ContentType.objects.get_for_model(Article, for_concrete_model=False)
        self.assertEqual(blog_class_ctype, article_ctype)

    def test_content_type_consistency_across_inheritance_chain(self):
        """Test that content type is consistent across the inheritance chain."""
        # Create multiple levels if they exist
        blog_ctype = get_polymorphic_base_content_type(self.blog_post)
        news_ctype = get_polymorphic_base_content_type(self.news_article)

        # All should point to the same base Article type
        article_ctype = ContentType.objects.get_for_model(Article, for_concrete_model=False)
        self.assertEqual(blog_ctype, article_ctype)
        self.assertEqual(news_ctype, article_ctype)

    def test_get_polymorphic_base_content_type_with_instance_and_class(self):
        """Test that the function works consistently with instances and classes."""
        # Get content type from instance
        instance_ctype = get_polymorphic_base_content_type(self.blog_post)

        # Get content type from class
        class_ctype = get_polymorphic_base_content_type(BlogPost)

        # Both should return the same Article content type
        self.assertEqual(instance_ctype, class_ctype)
        self.assertEqual(instance_ctype.model, "article")

    def test_get_polymorphic_base_content_type_returns_content_type_object(self):
        """Test that the function returns a ContentType instance."""
        self.assertIsInstance(get_polymorphic_base_content_type(self.blog_post), ContentType)

    def test_guardian_permissions_use_base_model_namespace(self):
        """
        Test that guardian permissions are assigned to base model when configured.

        This test verifies that when GUARDIAN_GET_CONTENT_TYPE is set to use
        get_polymorphic_base_content_type, permissions assigned to child model
        instances (BlogPost, NewsArticle) are stored against the base Article
        content type, creating a single permission namespace for the entire
        polymorphic model hierarchy.
        """
        from guardian.shortcuts import assign_perm, remove_perm
        from guardian.models import UserObjectPermission

        # The setting is configured in settings.py when guardian is installed
        # GUARDIAN_GET_CONTENT_TYPE = "polymorphic.contrib.guardian..."

        # Assign permission to a BlogPost instance
        assign_perm("add_article", self.user, self.blog_post)

        # Get the stored permission object
        perm = UserObjectPermission.objects.filter(
            user=self.user, object_pk=str(self.blog_post.pk)
        ).first()

        # Verify permission was created
        self.assertIsNotNone(perm, "Permission should be created")

        # The critical assertion: permission should use Article content type,
        # NOT BlogPost content type
        article_ctype = ContentType.objects.get_for_model(Article, for_concrete_model=False)
        self.assertEqual(
            perm.content_type,
            article_ctype,
            "Permission should be stored against Article, not BlogPost",
        )

        # Verify the permission codename is correct
        self.assertEqual(perm.permission.codename, "add_article")

        # Now assign permission to a NewsArticle instance
        assign_perm("change_article", self.user, self.news_article)

        news_perm = UserObjectPermission.objects.filter(
            user=self.user, object_pk=str(self.news_article.pk)
        ).first()

        # NewsArticle permission should ALSO use Article content type
        self.assertEqual(
            news_perm.content_type,
            article_ctype,
            "NewsArticle permission should also use Article content type",
        )

        # All permissions for this polymorphic tree should share the same
        # content type, creating a unified permission namespace
        all_perms = UserObjectPermission.objects.filter(user=self.user)
        content_types = set(p.content_type for p in all_perms)

        self.assertEqual(
            len(content_types),
            1,
            "All permissions should use the same Article content type",
        )
        self.assertEqual(
            content_types.pop(),
            article_ctype,
            "The shared content type should be Article",
        )

        # Clean up
        remove_perm("add_article", self.user, self.blog_post)
        remove_perm("change_article", self.user, self.news_article)

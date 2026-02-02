from unittest import skipUnless
from django.test import TestCase
from django.urls import reverse
from playwright.sync_api import expect

try:
    from reversion import revisions
    from reversion.models import Version

    REVERSION_INSTALLED = True
except ImportError:
    REVERSION_INSTALLED = False
    revisions = None
    Version = None

from ..models import Article, BlogPost, NewsArticle
from polymorphic.tests.utils import _GenericUITest


@skipUnless(REVERSION_INSTALLED, "django-reversion is not installed")
class ReversionIntegrationTests(TestCase):
    """
    Tests for django-reversion integration with polymorphic models.

    These tests verify that:
    1. Polymorphic models can be versioned
    2. The follow parameter correctly tracks parent model changes
    3. Revisions are created and can be retrieved
    """

    def test_blogpost_versioning(self):
        """Test that BlogPost instances are properly versioned."""
        # Create a blog post with reversion
        with revisions.create_revision():
            blog_post = BlogPost.objects.create(
                title="First Post",
                content="This is my first blog post.",
                author="John Doe",
            )
            revisions.set_comment("Initial version")

        # Verify a version was created
        versions = Version.objects.get_for_object(blog_post)
        self.assertEqual(versions.count(), 1)
        self.assertEqual(versions[0].revision.comment, "Initial version")

        # Update the blog post
        with revisions.create_revision():
            blog_post.title = "Updated Post"
            blog_post.content = "This is my updated blog post."
            blog_post.save()
            revisions.set_comment("Updated title and content")

        # Verify we now have two versions
        versions = Version.objects.get_for_object(blog_post)
        self.assertEqual(versions.count(), 2)

        # Verify we can retrieve the old version
        old_version = versions[1]
        old_data = old_version.field_dict
        self.assertEqual(old_data["title"], "First Post")
        self.assertEqual(old_data["content"], "This is my first blog post.")

    def test_newsarticle_versioning(self):
        """Test that NewsArticle instances are properly versioned."""
        # Create a news article with reversion
        with revisions.create_revision():
            news_article = NewsArticle.objects.create(
                title="Breaking News",
                content="Important news story.",
                source="Daily News",
            )
            revisions.set_comment("Published article")

        # Verify a version was created
        versions = Version.objects.get_for_object(news_article)
        self.assertEqual(versions.count(), 1)

        # Update the news article
        with revisions.create_revision():
            news_article.content = "Updated news story with more details."
            news_article.save()
            revisions.set_comment("Added more details")

        # Verify we now have two versions
        versions = Version.objects.get_for_object(news_article)
        self.assertEqual(versions.count(), 2)

    def test_polymorphic_queryset_with_versioned_objects(self):
        """Test that polymorphic queries work correctly with versioned objects."""
        # Create instances of both child models
        with revisions.create_revision():
            BlogPost.objects.create(
                title="Blog Post",
                content="Blog content",
                author="Jane Smith",
            )
            NewsArticle.objects.create(
                title="News Article",
                content="News content",
                source="News Corp",
            )

        # Query using the polymorphic base model
        articles = Article.objects.all()
        self.assertEqual(articles.count(), 2)

        # Verify polymorphic behavior
        self.assertIsInstance(articles[0], (BlogPost, NewsArticle))
        self.assertIsInstance(articles[1], (BlogPost, NewsArticle))

        # Verify both have versions
        for article in articles:
            versions = Version.objects.get_for_object(article)
            self.assertGreaterEqual(versions.count(), 1)

    def test_revert_to_previous_version(self):
        """Test that we can revert an object to a previous version."""
        # Create initial version
        with revisions.create_revision():
            blog_post = BlogPost.objects.create(
                title="Original Title",
                content="Original content",
                author="Author One",
            )

        # Make several updates
        with revisions.create_revision():
            blog_post.title = "Second Title"
            blog_post.save()

        with revisions.create_revision():
            blog_post.title = "Third Title"
            blog_post.author = "Author Two"
            blog_post.save()

        # Verify current state
        blog_post.refresh_from_db()
        self.assertEqual(blog_post.title, "Third Title")
        self.assertEqual(blog_post.author, "Author Two")

        # Revert to first version
        versions = Version.objects.get_for_object(blog_post)
        first_version = versions[
            2
        ]  # Versions are in reverse chronological order
        first_version.revision.revert()

        # Verify reverted state
        blog_post.refresh_from_db()
        self.assertEqual(blog_post.title, "Original Title")
        self.assertEqual(blog_post.author, "Author One")

    def test_manual_reversion_workflow(self):
        """Test complete manual reversion workflow without admin interface."""
        # Create a blog post with initial version
        with revisions.create_revision():
            blog_post = BlogPost.objects.create(
                title="Manual Test Post",
                content="Initial content for manual testing.",
                author="Test Author",
            )
            revisions.set_user(None)
            revisions.set_comment("Manual creation")

        original_id = blog_post.id

        # Make first update
        with revisions.create_revision():
            blog_post.title = "Updated Manual Test Post"
            blog_post.content = "First update to content."
            blog_post.save()
            revisions.set_comment("First manual update")

        # Make second update
        with revisions.create_revision():
            blog_post.author = "Updated Author"
            blog_post.content = "Second update to content."
            blog_post.save()
            revisions.set_comment("Second manual update")

        # Verify we have 3 versions
        versions = Version.objects.get_for_object(blog_post)
        self.assertEqual(versions.count(), 3)

        # Test getting version data
        latest_version = versions[0]
        self.assertEqual(latest_version.field_dict["author"], "Updated Author")
        self.assertEqual(
            latest_version.field_dict["content"],
            "Second update to content.",
        )

        middle_version = versions[1]
        self.assertEqual(
            middle_version.field_dict["title"], "Updated Manual Test Post"
        )
        self.assertEqual(
            middle_version.field_dict["content"],
            "First update to content.",
        )

        original_version = versions[2]
        self.assertEqual(
            original_version.field_dict["title"], "Manual Test Post"
        )
        self.assertEqual(original_version.field_dict["author"], "Test Author")

        # Test reverting to middle version manually
        middle_version.revision.revert()
        blog_post.refresh_from_db()
        self.assertEqual(blog_post.title, "Updated Manual Test Post")
        self.assertEqual(blog_post.content, "First update to content.")
        self.assertEqual(
            blog_post.author, "Test Author"
        )  # Should be from original

        # Test accessing revision metadata
        revision = middle_version.revision
        self.assertEqual(revision.comment, "First manual update")

        # Test that polymorphic type is preserved across reversion
        self.assertIsInstance(blog_post, BlogPost)
        self.assertEqual(blog_post.id, original_id)

    def test_manual_newsarticle_reversion_with_deletion(self):
        """Test manual reversion including object deletion and recovery."""
        # Create a news article
        with revisions.create_revision():
            news = NewsArticle.objects.create(
                title="Breaking News",
                content="Important breaking news.",
                source="Test News Network",
            )
            revisions.set_comment("Initial news article")

        news_id = news.id

        # Update the article
        with revisions.create_revision():
            news.content = "Updated breaking news with more details."
            news.source = "Updated News Network"
            news.save()
            revisions.set_comment("Updated news details")

        # Get versions before deletion
        versions = Version.objects.get_for_object(news)
        self.assertEqual(versions.count(), 2)
        original_version = versions[1]

        # Delete the object
        with revisions.create_revision():
            news.delete()
            revisions.set_comment("Deleted news article")

        # Verify object is deleted
        self.assertFalse(NewsArticle.objects.filter(id=news_id).exists())

        # Manually recover from deletion by reverting to a previous version
        original_version.revision.revert()

        # Verify object is restored
        recovered_news = NewsArticle.objects.get(id=news_id)
        self.assertEqual(recovered_news.title, "Breaking News")
        self.assertEqual(recovered_news.content, "Important breaking news.")
        self.assertEqual(recovered_news.source, "Test News Network")
        self.assertIsInstance(recovered_news, NewsArticle)

    def test_manual_batch_reversion(self):
        """Test reverting multiple polymorphic objects in a single revision."""
        # Create multiple objects in one revision
        with revisions.create_revision():
            blog1 = BlogPost.objects.create(
                title="Blog 1", content="Content 1", author="Author 1"
            )
            blog2 = BlogPost.objects.create(
                title="Blog 2", content="Content 2", author="Author 2"
            )
            news = NewsArticle.objects.create(
                title="News 1", content="News content", source="Source 1"
            )
            revisions.set_comment("Batch creation")

        # Update all objects in another revision
        with revisions.create_revision():
            blog1.title = "Updated Blog 1"
            blog1.save()
            blog2.title = "Updated Blog 2"
            blog2.save()
            news.title = "Updated News 1"
            news.save()
            revisions.set_comment("Batch update")

        # Verify updated state
        blog1.refresh_from_db()
        blog2.refresh_from_db()
        news.refresh_from_db()
        self.assertEqual(blog1.title, "Updated Blog 1")
        self.assertEqual(blog2.title, "Updated Blog 2")
        self.assertEqual(news.title, "Updated News 1")

        # Get the original revision (should contain all three objects)
        from reversion.models import Revision

        original_revision = Revision.objects.order_by("date_created")[0]
        self.assertEqual(original_revision.comment, "Batch creation")

        # Revert the entire revision
        original_revision.revert()

        # Verify all objects reverted
        blog1.refresh_from_db()
        blog2.refresh_from_db()
        news.refresh_from_db()
        self.assertEqual(blog1.title, "Blog 1")
        self.assertEqual(blog2.title, "Blog 2")
        self.assertEqual(news.title, "News 1")


@skipUnless(REVERSION_INSTALLED, "django-reversion is not installed")
class ReversionAdminUITests(_GenericUITest):
    """Test reversion functionality through the admin interface."""

    def test_blogpost_admin_reversion(self):
        """Test BlogPost admin integration: creating, updating, versioning, and reverting through UI."""
        # Navigate to BlogPost add page
        add_url = self.add_url(BlogPost)
        self.page.goto(add_url)

        # Create initial BlogPost
        self.page.fill("input[name='title']", "Admin Test Post")
        self.page.fill("textarea[name='content']", "Initial admin content")
        self.page.fill("input[name='author']", "Admin Author")

        # Save the object
        with self.page.expect_navigation(timeout=30000):
            self.page.click("input[name='_save']")

        # Verify BlogPost was created
        blog_post = BlogPost.objects.get(title="Admin Test Post")
        self.assertEqual(blog_post.author, "Admin Author")
        self.assertEqual(blog_post.content, "Initial admin content")

        # Verify we have 1 version (created by admin)
        versions = Version.objects.get_for_object(blog_post)
        self.assertEqual(versions.count(), 1)
        first_version = versions[0]
        self.assertEqual(first_version.field_dict["title"], "Admin Test Post")
        self.assertEqual(first_version.field_dict["author"], "Admin Author")

        # Navigate to change page and update the BlogPost
        change_url = self.change_url(BlogPost, blog_post.pk)
        self.page.goto(change_url)

        self.page.fill("input[name='title']", "Updated Admin Test Post")
        self.page.fill("textarea[name='content']", "Updated admin content")
        self.page.fill("input[name='author']", "Updated Admin Author")

        with self.page.expect_navigation(timeout=30000):
            self.page.click("input[name='_save']")

        # Verify update
        blog_post.refresh_from_db()
        self.assertEqual(blog_post.title, "Updated Admin Test Post")
        self.assertEqual(blog_post.author, "Updated Admin Author")

        # Verify we now have 2 versions (admin creates version on each save)
        versions = Version.objects.get_for_object(blog_post)
        self.assertEqual(versions.count(), 2)
        latest_version = versions[0]
        self.assertEqual(
            latest_version.field_dict["title"], "Updated Admin Test Post"
        )
        self.assertEqual(
            latest_version.field_dict["author"], "Updated Admin Author"
        )

        # Navigate to history page and verify it's accessible
        history_url = f"{self.live_server_url}{reverse('admin:integrations_blogpost_history', args=[blog_post.pk])}"
        self.page.goto(history_url)

        # Verify we can see the history page
        expect(self.page.locator("#content h1")).to_contain_text(
            "Change history"
        )

        # Verify history table shows version information
        history_table = self.page.locator(
            "table#change-history, div#change-history"
        )
        expect(history_table).to_be_visible()

        # Use the UI to revert: Click on the oldest version's date/time link
        # The history table typically has links in each row - we want the last row (oldest)
        history_links = self.page.locator("table#change-history a").all()
        self.assertGreater(len(history_links), 1, "Should have history links")

        # Click on the last link (oldest version) to view that revision
        with self.page.expect_navigation(timeout=30000):
            history_links[0].click()

        # We're now on the specific version's history page (history/<version_id>/)
        current_url = self.page.url
        self.assertIn(
            "/history/",
            current_url,
            f"Should be on history detail page, got: {current_url}",
        )

        # Wait for page to fully load
        self.page.wait_for_load_state("domcontentloaded", timeout=10000)

        # The page should show the old version's data
        page_content = self.page.content()
        self.assertIn(
            "Admin Test Post",
            page_content,
            "Should see original title on the version page",
        )

        # Find and click the submit button to revert
        submit_button = self.page.locator("input[type='submit']").first

        with self.page.expect_navigation(timeout=30000):
            submit_button.click()

        # Verify the object was reverted
        blog_post.refresh_from_db()
        self.assertEqual(blog_post.title, "Admin Test Post")
        self.assertEqual(blog_post.author, "Admin Author")
        self.assertIsInstance(blog_post, BlogPost)

    def test_article_admin_reversion(self):
        """Test Article (polymorphic parent) admin versioning and reversion through UI."""
        # Create an article first via API, then test admin updates
        with revisions.create_revision():
            article = BlogPost.objects.create(
                title="Parent Article Test",
                content="Parent article content",
                author="Parent Author",
            )

        # Verify version created
        versions = Version.objects.get_for_object(article)
        self.assertEqual(versions.count(), 1)

        # Update through parent Article admin interface
        change_url = self.change_url(Article, article.pk)
        self.page.goto(change_url)

        # Verify we're on the change page for the parent admin
        expect(self.page.locator("#content h1")).to_contain_text("Change")

        self.page.fill("input[name='title']", "Updated Parent Article")
        self.page.fill("textarea[name='content']", "Updated parent content")

        with self.page.expect_navigation(timeout=30000):
            self.page.click("input[name='_save']")

        # Verify update
        article.refresh_from_db()
        self.assertEqual(article.title, "Updated Parent Article")

        # Verify we now have 2 versions (1 from API, 1 from admin)
        versions = Version.objects.get_for_object(article)
        self.assertEqual(versions.count(), 2)
        self.assertEqual(
            versions[0].field_dict["title"], "Updated Parent Article"
        )
        self.assertEqual(versions[1].field_dict["title"], "Parent Article Test")

        # Navigate to history page through parent admin
        history_url = f"{self.live_server_url}{reverse('admin:integrations_article_history', args=[article.pk])}"
        self.page.goto(history_url)
        expect(self.page.locator("#content h1")).to_contain_text(
            "Change history"
        )

        # Use the UI to revert: Click on the oldest version
        history_links = self.page.locator("table#change-history a").all()
        self.assertGreater(len(history_links), 1)

        with self.page.expect_navigation(timeout=30000):
            history_links[0].click()

        # Wait for page to load
        self.page.wait_for_load_state("domcontentloaded", timeout=10000)

        # Verify we're on the revert page
        page_content = self.page.content()
        self.assertIn("Revert", page_content, "Should be on a revert page")

        # Click the submit button to revert
        submit_button = self.page.locator("input[type='submit']").first

        with self.page.expect_navigation(timeout=30000):
            submit_button.click()

        # Verify the object was reverted
        article.refresh_from_db()
        self.assertEqual(article.title, "Parent Article Test")
        self.assertEqual(article.content, "Parent article content")
        self.assertIsInstance(article, BlogPost)

    def test_newsarticle_admin_reversion(self):
        """Test NewsArticle admin versioning and reversion through UI."""
        # Navigate to NewsArticle add page
        add_url = self.add_url(NewsArticle)
        self.page.goto(add_url)

        # Create NewsArticle
        self.page.fill("input[name='title']", "Breaking Admin News")
        self.page.fill("textarea[name='content']", "Admin news content")
        self.page.fill("input[name='source']", "Admin News Network")

        with self.page.expect_navigation(timeout=30000):
            self.page.click("input[name='_save']")

        # Verify creation
        news = NewsArticle.objects.get(title="Breaking Admin News")
        self.assertEqual(news.source, "Admin News Network")

        # Verify version created
        versions = Version.objects.get_for_object(news)
        self.assertEqual(versions.count(), 1)

        # Update
        change_url = self.change_url(NewsArticle, news.pk)
        self.page.goto(change_url)

        self.page.fill("input[name='title']", "Updated Breaking News")
        self.page.fill("input[name='source']", "Updated Network")

        with self.page.expect_navigation(timeout=30000):
            self.page.click("input[name='_save']")

        news.refresh_from_db()
        self.assertEqual(news.title, "Updated Breaking News")

        # Verify we have 2 versions from admin operations
        versions = Version.objects.get_for_object(news)
        self.assertEqual(versions.count(), 2)
        self.assertEqual(
            versions[0].field_dict["title"], "Updated Breaking News"
        )
        self.assertEqual(versions[1].field_dict["title"], "Breaking Admin News")

        # Verify history page is accessible
        history_url = f"{self.live_server_url}{reverse('admin:integrations_newsarticle_history', args=[news.pk])}"
        self.page.goto(history_url)
        expect(self.page.locator("#content h1")).to_contain_text(
            "Change history"
        )

        # Use the UI to revert: Click on the oldest version
        history_links = self.page.locator("table#change-history a").all()
        self.assertGreater(len(history_links), 1)

        with self.page.expect_navigation(timeout=30000):
            history_links[0].click()

        # Wait for page to load
        self.page.wait_for_load_state("domcontentloaded", timeout=10000)

        # Verify we're on the revert page
        page_content = self.page.content()
        self.assertIn("Revert", page_content, "Should be on a revert page")

        # Try to revert through UI - click the save button
        submit_buttons = self.page.locator("input[type='submit']").all()

        with self.page.expect_navigation(timeout=30000):
            submit_buttons[0].click()

        # Check if reversion worked
        news.refresh_from_db()
        # Reversion worked! Verify values
        self.assertEqual(news.source, "Admin News Network")
        self.assertIsInstance(news, NewsArticle)

        # Verify a new version was created for the revert operation
        versions_after_revert = Version.objects.get_for_object(news)
        self.assertEqual(versions_after_revert.count(), 3)

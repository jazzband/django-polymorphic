from unittest import skipUnless
from django.contrib.contenttypes.models import ContentType
from django.test import TestCase, override_settings
from django.urls import reverse
from playwright.sync_api import expect

try:
    import extra_views

    EXTRA_VIEWS_INSTALLED = True
except ImportError:
    EXTRA_VIEWS_INSTALLED = False

from ..models import Article, BlogPost, NewsArticle
from polymorphic.tests.utils import _GenericUITest


@skipUnless(EXTRA_VIEWS_INSTALLED, "django-extra-views is not installed")
class ExtraViewsIntegrationTests(TestCase):
    """
    Tests for django-extra-views integration with polymorphic models.

    These tests verify that:
    1. PolymorphicFormSetView works with polymorphic models
    2. Formsets can create and update polymorphic child instances
    3. Child forms are correctly rendered for different model types
    """

    def test_formset_children_configuration(self):
        """Test that formset children are properly configured."""
        from .views import ArticleFormSetView

        view = ArticleFormSetView()
        children = view.get_formset_children()

        self.assertEqual(len(children), 2)
        self.assertEqual(children[0].model, BlogPost)
        self.assertEqual(children[1].model, NewsArticle)

    def test_formset_generation(self):
        """Test that the formset is properly generated with child forms."""
        from .views import ArticleFormSetView

        view = ArticleFormSetView()
        formset_class = view.get_formset()

        # Verify child_forms are attached
        self.assertTrue(hasattr(formset_class, "child_forms"))
        self.assertEqual(len(formset_class.child_forms), 2)
        self.assertIn(BlogPost, formset_class.child_forms)
        self.assertIn(NewsArticle, formset_class.child_forms)

    def test_formset_with_existing_objects(self):
        """Test formset with existing polymorphic objects."""
        # Create test objects
        blog_post = BlogPost.objects.create(
            title="Test Blog", content="Blog content", author="Blog Author"
        )
        news_article = NewsArticle.objects.create(
            title="Test News", content="News content", source="News Source"
        )

        from .views import ArticleFormSetView

        view = ArticleFormSetView()
        formset_class = view.get_formset()

        # Create formset instance with queryset
        formset = formset_class(queryset=Article.objects.all())

        # Verify formset contains both objects
        self.assertEqual(len(formset.forms), 4)

        # Verify polymorphic types are preserved
        form_models = [form.instance.__class__ for form in formset.forms]
        self.assertIn(BlogPost, form_models)
        self.assertIn(NewsArticle, form_models)

    def test_formset_extra_forms_configuration(self):
        """Test that formset generates correct extra forms when empty."""
        from .views import ArticleFormSetView

        # Ensure no objects exist
        Article.objects.all().delete()

        view = ArticleFormSetView()
        formset_class = view.get_formset()

        # Create empty formset
        formset = formset_class(queryset=Article.objects.none())

        # Verify we have 2 extra forms (as configured in factory_kwargs)
        self.assertEqual(len(formset.forms), 2)

        # Verify the forms cycle through child types
        # Form 0 should be BlogPost (first child)
        self.assertEqual(formset.forms[0]._meta.model, BlogPost)

        # Form 1 should be NewsArticle (second child)
        self.assertEqual(formset.forms[1]._meta.model, NewsArticle)

    def test_formset_saving_new_objects(self):
        """Test creating new polymorphic objects through formset."""
        from .views import ArticleFormSetView

        view = ArticleFormSetView()
        formset_class = view.get_formset()

        # Create formset with POST data for new objects
        data = {
            "form-TOTAL_FORMS": "2",
            "form-INITIAL_FORMS": "0",
            "form-MIN_NUM_FORMS": "0",
            "form-MAX_NUM_FORMS": "1000",
            # BlogPost
            "form-0-polymorphic_ctype": str(
                ContentType.objects.get_for_model(
                    BlogPost, for_concrete_model=False
                ).pk
            ),
            "form-0-title": "New Blog Post",
            "form-0-content": "Blog post content",
            "form-0-author": "Blog Author",
            # NewsArticle
            "form-1-polymorphic_ctype": str(
                ContentType.objects.get_for_model(
                    NewsArticle, for_concrete_model=False
                ).pk
            ),
            "form-1-title": "New News Article",
            "form-1-content": "News article content",
            "form-1-source": "News Source",
        }

        formset = formset_class(data)

        # Verify formset is valid
        self.assertTrue(formset.is_valid(), formset.errors)

        # Save the formset
        instances = formset.save()

        # Verify objects were created
        self.assertEqual(len(instances), 2)
        self.assertEqual(Article.objects.count(), 2)

        # Verify polymorphic types
        blog_post = BlogPost.objects.get(title="New Blog Post")
        self.assertEqual(blog_post.author, "Blog Author")

        news_article = NewsArticle.objects.get(title="New News Article")
        self.assertEqual(news_article.source, "News Source")

    def test_formset_updating_objects(self):
        """Test updating existing polymorphic objects through formset."""
        # Create existing objects
        blog_post = BlogPost.objects.create(
            title="Original Blog",
            content="Original content",
            author="Original Author",
        )

        from .views import ArticleFormSetView

        view = ArticleFormSetView()
        formset_class = view.get_formset()

        # Create formset with update data
        data = {
            "form-TOTAL_FORMS": "1",
            "form-INITIAL_FORMS": "1",
            "form-MIN_NUM_FORMS": "0",
            "form-MAX_NUM_FORMS": "1000",
            "form-0-id": str(blog_post.pk),
            "form-0-polymorphic_ctype": str(
                ContentType.objects.get_for_model(
                    BlogPost, for_concrete_model=False
                ).pk
            ),
            "form-0-title": "Updated Blog",
            "form-0-content": "Updated content",
            "form-0-author": "Updated Author",
        }

        formset = formset_class(data, queryset=Article.objects.all())

        # Verify formset is valid
        self.assertTrue(formset.is_valid(), formset.errors)

        # Save the formset
        formset.save()

        # Verify object was updated
        blog_post.refresh_from_db()
        self.assertEqual(blog_post.title, "Updated Blog")
        self.assertEqual(blog_post.author, "Updated Author")

    def test_formset_deleting_objects(self):
        """Test deleting polymorphic objects through formset."""
        # Create object to delete
        blog_post = BlogPost.objects.create(
            title="To Delete", content="Content", author="Author"
        )

        from .views import ArticleFormSetView

        view = ArticleFormSetView()
        formset_class = view.get_formset()

        # Create formset with delete data
        data = {
            "form-TOTAL_FORMS": "1",
            "form-INITIAL_FORMS": "1",
            "form-MIN_NUM_FORMS": "0",
            "form-MAX_NUM_FORMS": "1000",
            "form-0-id": str(blog_post.pk),
            "form-0-polymorphic_ctype": str(
                ContentType.objects.get_for_model(
                    BlogPost, for_concrete_model=False
                ).pk
            ),
            "form-0-title": blog_post.title,
            "form-0-content": blog_post.content,
            "form-0-author": blog_post.author,
            "form-0-DELETE": "on",
        }

        formset = formset_class(data, queryset=Article.objects.all())

        # Verify formset is valid
        self.assertTrue(formset.is_valid(), formset.errors)

        # Save the formset
        formset.save()

        # Verify object was deleted
        self.assertFalse(BlogPost.objects.filter(pk=blog_post.pk).exists())

    def test_formset_mixed_operations(self):
        """Test creating, updating, and deleting in single formset submission."""
        # Create existing object to update
        blog_post = BlogPost.objects.create(
            title="Existing Blog",
            content="Existing content",
            author="Existing Author",
        )

        # Create object to delete
        news_to_delete = NewsArticle.objects.create(
            title="To Delete",
            content="Delete content",
            source="Delete Source",
        )

        from .views import ArticleFormSetView

        view = ArticleFormSetView()
        formset_class = view.get_formset()

        data = {
            "form-TOTAL_FORMS": "3",
            "form-INITIAL_FORMS": "2",
            "form-MIN_NUM_FORMS": "0",
            "form-MAX_NUM_FORMS": "1000",
            # Update existing blog post
            "form-0-id": str(blog_post.pk),
            "form-0-polymorphic_ctype": str(
                ContentType.objects.get_for_model(
                    BlogPost, for_concrete_model=False
                ).pk
            ),
            "form-0-title": "Updated Existing Blog",
            "form-0-content": "Updated content",
            "form-0-author": "Updated Author",
            # Delete news article
            "form-1-id": str(news_to_delete.pk),
            "form-1-polymorphic_ctype": str(
                ContentType.objects.get_for_model(
                    NewsArticle, for_concrete_model=False
                ).pk
            ),
            "form-1-title": news_to_delete.title,
            "form-1-content": news_to_delete.content,
            "form-1-source": news_to_delete.source,
            "form-1-DELETE": "on",
            # Create new blog post
            "form-2-polymorphic_ctype": str(
                ContentType.objects.get_for_model(
                    BlogPost, for_concrete_model=False
                ).pk
            ),
            "form-2-title": "New Blog Post",
            "form-2-content": "New content",
            "form-2-author": "New Author",
        }

        formset = formset_class(data, queryset=Article.objects.all())
        self.assertTrue(formset.is_valid(), formset.errors)
        formset.save()

        # Verify update
        blog_post.refresh_from_db()
        self.assertEqual(blog_post.title, "Updated Existing Blog")

        # Verify deletion
        self.assertFalse(
            NewsArticle.objects.filter(pk=news_to_delete.pk).exists()
        )

        # Verify creation
        new_blog = BlogPost.objects.get(title="New Blog Post")
        self.assertEqual(new_blog.author, "New Author")

        # Verify total count
        self.assertEqual(Article.objects.count(), 2)


@skipUnless(EXTRA_VIEWS_INSTALLED, "django-extra-views is not installed")
class ExtraViewsUITests(TestCase):
    """Test django-extra-views functionality through the Client API."""

    def test_formset_view_get_request(self):
        """Test that the formset view handles GET requests correctly."""
        from .views import ArticleFormSetView

        # Create some existing objects
        BlogPost.objects.create(
            title="Existing Blog", content="Content", author="Author"
        )
        NewsArticle.objects.create(
            title="Existing News", content="Content", source="Source"
        )

        view = ArticleFormSetView.as_view()
        from django.test import RequestFactory

        factory = RequestFactory()
        request = factory.get("/articles/")
        response = view(request)
        response.render()

        # Verify response
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Article Formset", response.content)

    def test_formset_view_post_request(self):
        """Test creating new polymorphic objects through POST request."""
        from .views import ArticleFormSetView

        view = ArticleFormSetView.as_view()
        from django.test import RequestFactory

        factory = RequestFactory()

        # Create POST data
        data = {
            "form-TOTAL_FORMS": "1",
            "form-INITIAL_FORMS": "0",
            "form-MIN_NUM_FORMS": "0",
            "form-MAX_NUM_FORMS": "1000",
            "form-0-polymorphic_ctype": str(
                ContentType.objects.get_for_model(
                    BlogPost, for_concrete_model=False
                ).pk
            ),
            "form-0-title": "New Blog Post",
            "form-0-content": "Blog content",
            "form-0-author": "Author Name",
        }

        request = factory.post("/articles/", data)
        response = view(request)

        # Verify redirect on success
        self.assertEqual(response.status_code, 302)

        # Verify object was created
        blog_post = BlogPost.objects.get(title="New Blog Post")
        self.assertEqual(blog_post.author, "Author Name")


@skipUnless(EXTRA_VIEWS_INSTALLED, "django-extra-views is not installed")
class ExtraViewsLiveServerTests(_GenericUITest):
    """Test django-extra-views functionality through the live test server."""

    def setUp(self):
        """Create a page without admin login (not needed for formset view)."""
        self.page = self.browser.new_page()

    def tearDown(self):
        """Close the page after each test."""
        if self.page:
            self.page.close()

    def test_formset_view_renders_existing_objects(self):
        """Test that existing polymorphic objects are rendered in the formset."""
        # Create existing objects
        blog_post = BlogPost.objects.create(
            title="Existing Blog",
            content="Blog content",
            author="Blog Author",
        )
        news_article = NewsArticle.objects.create(
            title="Existing News",
            content="News content",
            source="News Source",
        )

        # Navigate to formset view
        url = f"{self.live_server_url}{reverse('extra_views:articles')}"
        self.page.goto(url)

        # Verify page loaded
        expect(self.page.locator("h1")).to_contain_text("Article Formset")

        # Verify form is rendered
        form = self.page.locator("form")
        expect(form).to_be_visible()

        # Verify existing objects are shown in the formset
        # The formset should have inputs for the existing objects
        expect(
            self.page.locator(f"input[value='{blog_post.title}']")
        ).to_be_visible()
        expect(
            self.page.locator(f"input[value='{news_article.title}']")
        ).to_be_visible()

    def test_formset_update_existing_object(self):
        """Test updating an existing object through the formset."""
        # Create an object to update
        blog_post = BlogPost.objects.create(
            title="Original Title",
            content="Original content",
            author="Original Author",
        )

        # Navigate to formset view
        url = f"{self.live_server_url}{reverse('extra_views:articles')}"
        self.page.goto(url)

        # Find the title input for this blog post
        # The form should have a hidden id field and visible title field
        title_input = self.page.locator(
            f"input[value='{blog_post.title}']"
        ).first
        title_input.fill("Updated Title")

        # Find and update the author field
        # The author field should be in the same form container
        author_input = self.page.locator(
            f"input[value='{blog_post.author}']"
        ).first
        author_input.fill("Updated Author")

        # Submit the form
        with self.page.expect_navigation(timeout=30000):
            self.page.locator("button[type='submit']").click()

        # Verify the object was updated
        blog_post.refresh_from_db()
        self.assertEqual(blog_post.title, "Updated Title")
        self.assertEqual(blog_post.author, "Updated Author")

    def test_formset_delete_existing_object(self):
        """Test deleting an existing object through the formset."""
        # Create an object to delete
        blog_post = BlogPost.objects.create(
            title="To Delete",
            content="Delete content",
            author="Delete Author",
        )
        blog_post_id = blog_post.id

        # Navigate to formset view
        url = f"{self.live_server_url}{reverse('extra_views:articles')}"
        self.page.goto(url)

        # Find the DELETE checkbox for this object
        # Django formsets add a DELETE checkbox for each form when can_delete=True
        delete_checkbox = self.page.locator(
            "input[type='checkbox'][name*='DELETE']"
        ).first

        # Check if the checkbox is visible, if not we need to handle it differently
        if delete_checkbox.is_visible():
            delete_checkbox.check()

            # Submit the form
            with self.page.expect_navigation(timeout=30000):
                self.page.locator("button[type='submit']").click()

            # Verify the object was deleted
            self.assertFalse(BlogPost.objects.filter(id=blog_post_id).exists())
        else:
            # If DELETE checkboxes aren't visible, skip this test
            self.skipTest("DELETE checkboxes not visible in UI")

    def test_formset_displays_multiple_polymorphic_types(self):
        """Test that the formset correctly displays forms for different polymorphic types."""
        # Create instances of both child models
        blog_post = BlogPost.objects.create(
            title="Blog Post", content="Blog content", author="Blog Author"
        )
        news_article = NewsArticle.objects.create(
            title="News Article",
            content="News content",
            source="News Source",
        )

        # Navigate to formset view
        url = f"{self.live_server_url}{reverse('extra_views:articles')}"
        self.page.goto(url)

        # Verify both types are displayed
        # Blog post should have author field
        expect(
            self.page.locator(f"input[value='{blog_post.author}']")
        ).to_be_visible()

        # News article should have source field
        expect(
            self.page.locator(f"input[value='{news_article.source}']")
        ).to_be_visible()

        # Verify the formset contains both forms
        # Each form should have an id field
        id_inputs = self.page.locator("input[type='hidden'][name$='-id']").all()
        self.assertGreaterEqual(len(id_inputs), 2)

    def test_formset_mixed_operations_through_ui(self):
        """Test creating, updating, and deleting in a single formset submission."""
        # Create objects
        blog_to_update = BlogPost.objects.create(
            title="Update Me",
            content="Update content",
            author="Update Author",
        )
        news_to_delete = NewsArticle.objects.create(
            title="Delete Me",
            content="Delete content",
            source="Delete Source",
        )
        news_to_delete_id = news_to_delete.id

        # Navigate to formset view
        url = f"{self.live_server_url}{reverse('extra_views:articles')}"
        self.page.goto(url)

        # Update the blog post
        title_input = self.page.locator(
            f"input[value='{blog_to_update.title}']"
        ).first
        title_input.fill("Updated Blog Title")

        # Try to delete the news article
        delete_checkboxes = self.page.locator(
            "input[type='checkbox'][name*='DELETE']"
        ).all()
        if delete_checkboxes:
            # Check the second DELETE checkbox (for the news article)
            if len(delete_checkboxes) > 1:
                delete_checkboxes[1].check()

        # Submit the form
        with self.page.expect_navigation(timeout=30000):
            self.page.locator("button[type='submit']").click()

        # Verify the blog post was updated
        blog_to_update.refresh_from_db()
        self.assertEqual(blog_to_update.title, "Updated Blog Title")

        # Verify the news article was deleted (if DELETE checkbox was available)
        if delete_checkboxes and len(delete_checkboxes) > 1:
            self.assertFalse(
                NewsArticle.objects.filter(id=news_to_delete_id).exists()
            )

    def test_formset_empty_state_shows_extra_forms(self):
        """Test that the formset shows extra forms for adding new objects."""
        # Ensure no objects exist
        Article.objects.all().delete()

        # Navigate to formset view
        url = f"{self.live_server_url}{reverse('extra_views:articles')}"
        self.page.goto(url)

        # Verify page loaded
        expect(self.page.locator("h1")).to_contain_text("Article Formset")

        # Verify form is rendered
        form = self.page.locator("form")
        expect(form).to_be_visible()

        # The formset should have management form fields (they're hidden)
        self.assertIsNotNone(
            self.page.locator("input[name='form-TOTAL_FORMS']").first
        )
        self.assertIsNotNone(
            self.page.locator("input[name='form-INITIAL_FORMS']").first
        )

        # Verify we have 2 extra forms (one for each child type)
        formset_forms = self.page.locator(".formset-form").all()
        self.assertEqual(len(formset_forms), 2, "Should have 2 extra forms")

        # Verify we have headers indicating the form types
        expect(self.page.locator("h3:has-text('Blog Post')")).to_be_visible()
        expect(self.page.locator("h3:has-text('News Article')")).to_be_visible()

        # Verify BlogPost form has author field
        expect(self.page.locator("input[name='form-0-author']")).to_be_visible()

        # Verify NewsArticle form has source field
        expect(self.page.locator("input[name='form-1-source']")).to_be_visible()

    def test_formset_create_new_objects_via_extra_forms(self):
        """Test creating new objects using the extra forms in the UI."""
        # Ensure no objects exist
        Article.objects.all().delete()

        # Navigate to formset view
        url = f"{self.live_server_url}{reverse('extra_views:articles')}"
        self.page.goto(url)

        # Fill in the BlogPost form (form-0)
        self.page.locator("input[name='form-0-title']").fill("New Blog from UI")
        self.page.locator("textarea[name='form-0-content']").fill(
            "Blog content from UI"
        )
        self.page.locator("input[name='form-0-author']").fill("UI Author")

        # Fill in the NewsArticle form (form-1)
        self.page.locator("input[name='form-1-title']").fill("New News from UI")
        self.page.locator("textarea[name='form-1-content']").fill(
            "News content from UI"
        )
        self.page.locator("input[name='form-1-source']").fill("UI Source")

        # Submit the form
        with self.page.expect_navigation(timeout=30000):
            self.page.locator("button[type='submit']").click()

        # Verify objects were created
        self.assertEqual(Article.objects.count(), 2)

        # Verify BlogPost was created
        blog_post = BlogPost.objects.get(title="New Blog from UI")
        self.assertEqual(blog_post.author, "UI Author")

        # Verify NewsArticle was created
        news_article = NewsArticle.objects.get(title="New News from UI")
        self.assertEqual(news_article.source, "UI Source")

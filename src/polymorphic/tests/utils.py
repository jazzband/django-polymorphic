import os
import shutil
from pathlib import Path

from django.core.management import call_command
from django_test_migrations.migrator import Migrator
from django.contrib.auth import get_user_model
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.urls import reverse
from django.apps import apps

from playwright.sync_api import sync_playwright, expect
from polymorphic import tests


class GeneratedMigrationsPerClassMixin:
    """
    Generates migrations at class setup, applies them, and rolls them back at teardown.

    Configure:
      - apps_to_migrate = ["my_app", ...]
      - database = "default" (optional)
    """

    apps_to_migrate: list[str] = []
    database: str = "default"
    settings: str = os.environ.get("DJANGO_SETTINGS_MODULE", "polymorphic.tests.settings")

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        if not cls.apps_to_migrate:
            raise RuntimeError("Set apps_to_migrate = ['your_app', ...]")

        for app_label in cls.apps_to_migrate:
            call_command(
                "makemigrations",
                app_label,
                interactive=False,
                verbosity=0,
            )

        # 2) Apply all migrations (up to latest) using django-test-migrations
        cls.migrator = Migrator(database=cls.database)

        cls._applied_states = {}
        for app_label in cls.apps_to_migrate:
            latest = cls._find_latest_migration_name(app_label)
            # apply_initial_migration applies all migrations up to and including `latest`
            cls._applied_states[app_label] = cls.migrator.apply_initial_migration(
                (app_label, latest)
            )

    @classmethod
    def tearDownClass(cls):
        try:
            # Roll everything back / cleanup:
            if hasattr(cls, "migrator"):
                cls.migrator.reset()
        finally:
            # remove files
            for app_label in cls.apps_to_migrate:
                app_config = apps.get_app_config(app_label)  # app *label*
                mig_dir = Path(app_config.path) / "migrations"

                for mig_file in mig_dir.glob("*.py"):
                    if mig_file.name != "__init__.py" and mig_file.name[0:4].isdigit():
                        os.remove(mig_file)

                # also remove __pycache__ if exists
                pycache_dir = mig_dir / "__pycache__"
                if pycache_dir.exists() and pycache_dir.is_dir():
                    shutil.rmtree(pycache_dir)

            super().tearDownClass()

    @classmethod
    def _find_latest_migration_name(cls, app_label: str) -> str:
        """
        Returns "000X_..." latest migration filename (without .py).
        """
        app_config = apps.get_app_config(app_label)  # app *label*
        mig_dir = Path(app_config.path) / "migrations"

        candidates = sorted(
            p for p in mig_dir.glob("*.py") if p.name != "__init__.py" and p.name[0:4].isdigit()
        )
        if not candidates:
            raise RuntimeError(f"No migrations generated for {app_label}")
        return candidates[-1].stem


class _GenericUITest(StaticLiveServerTestCase):
    """Generic admin form test using Playwright."""

    HEADLESS = tests.HEADLESS

    admin_username = "admin"
    admin_password = "password"
    admin = None

    def admin_url(self):
        return f"{self.live_server_url}{reverse('admin:index')}"

    def add_url(self, model):
        path = reverse(f"admin:{model._meta.label_lower.replace('.', '_')}_add")
        return f"{self.live_server_url}{path}"

    def change_url(self, model, id):
        path = reverse(
            f"admin:{model._meta.label_lower.replace('.', '_')}_change",
            args=[id],
        )
        return f"{self.live_server_url}{path}"

    def list_url(self, model):
        path = reverse(f"admin:{model._meta.label_lower.replace('.', '_')}_changelist")
        return f"{self.live_server_url}{path}"

    def get_object_ids(self, model):
        self.page.goto(self.list_url(model))
        return self.page.eval_on_selector_all(
            "input[name='_selected_action']", "elements => elements.map(e => e.value)"
        )

    @classmethod
    def setUpClass(cls):
        """Set up the test class with a live server and Playwright instance."""
        os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "1"
        super().setUpClass()
        try:
            cls.playwright = sync_playwright().start()
            cls.browser = cls.playwright.chromium.launch(headless=cls.HEADLESS)
        except Exception as e:
            if "asyncio loop" in str(e) or "executable" in str(e).lower():
                raise RuntimeError(
                    "Playwright failed to start. This often happens if browser drivers are missing. "
                    "Please run 'just install-playwright' to install them."
                ) from e
            raise

    @classmethod
    def tearDownClass(cls):
        """Clean up Playwright instance after tests."""
        cls.browser.close()
        cls.playwright.stop()
        super().tearDownClass()
        del os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"]

    def setUp(self):
        """Create an admin user before running tests."""
        self.admin = get_user_model().objects.create_superuser(
            username=self.admin_username, email="admin@example.com", password=self.admin_password
        )
        self.page = self.browser.new_page()
        # Log in to the Django admin
        self.page.goto(f"{self.live_server_url}/admin/login/")
        self.page.fill("input[name='username']", self.admin_username)
        self.page.fill("input[name='password']", self.admin_password)
        self.page.click("input[type='submit']")

        # Ensure login is successful
        expect(self.page).to_have_url(f"{self.live_server_url}/admin/")

    def tearDown(self):
        if self.page:
            self.page.close()

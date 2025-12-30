import os
import shutil
from pathlib import Path
import io

from django.core.management import call_command

from django_test_migrations.migrator import Migrator
from django.apps import apps


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

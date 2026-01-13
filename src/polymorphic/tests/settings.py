import os

DEBUG = False

rdbms = os.environ.get("RDBMS", "sqlite")

PYTEST_DB_NAME = os.environ.get("PYTEST_DB_NAME", None)

DEFAULT_DBS = f"{PYTEST_DB_NAME or 'test1'},test2"

if rdbms == "sqlite":  # pragma: no cover
    sqlite_dbs = os.environ.get(
        "SQLITE_DATABASES", f"{PYTEST_DB_NAME or ':memory:'},:memory:"
    ).split(",")
    DATABASES = {
        "default": {"ENGINE": "django.db.backends.sqlite3", "NAME": sqlite_dbs[0]},
        "secondary": {"ENGINE": "django.db.backends.sqlite3", "NAME": sqlite_dbs[1]},
    }
elif rdbms == "postgres":  # pragma: no cover
    creds = {
        "USER": os.environ.get("POSTGRES_USER", "postgres"),
        "PASSWORD": os.environ.get("POSTGRES_PASSWORD", ""),
        "HOST": os.environ.get("POSTGRES_HOST", ""),
        "PORT": os.environ.get("POSTGRES_PORT", ""),
    }
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": PYTEST_DB_NAME or "test1",
            **creds,
        },
        "secondary": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": "test2",
            **creds,
        },
    }
elif rdbms == "mysql":  # pragma: no cover
    dbs = os.environ.get("MYSQL_MULTIPLE_DATABASES", DEFAULT_DBS).split(",")
    creds = {
        "USER": os.environ.get("MYSQL_USER", "root"),
        "PASSWORD": os.environ.get("MYSQL_PASSWORD", "root"),
        "HOST": os.environ.get("MYSQL_HOST", "127.0.0.1"),
        "PORT": os.environ.get("MYSQL_PORT", "3306"),
    }
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.mysql",
            "NAME": dbs[0],
            **creds,
        },
        "secondary": {
            "ENGINE": "django.db.backends.mysql",
            "NAME": dbs[1],
            **creds,
        },
    }
elif rdbms == "mariadb":  # pragma: no cover
    dbs = os.environ.get("MYSQL_MULTIPLE_DATABASES", DEFAULT_DBS).split(",")
    creds = {
        "USER": os.environ.get("MYSQL_USER", "root"),
        "PASSWORD": os.environ.get("MYSQL_ROOT_PASSWORD", "root"),
        "HOST": os.environ.get("MYSQL_HOST", "127.0.0.1"),
        "PORT": os.environ.get("MYSQL_PORT", "3306"),
    }
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.mysql",
            "NAME": dbs[0],
            **creds,
        },
        "secondary": {
            "ENGINE": "django.db.backends.mysql",
            "NAME": dbs[1],
            **creds,
        },
    }
elif rdbms == "oracle":  # pragma: no cover
    dbs = os.environ.get("ORACLE_DATABASES", DEFAULT_DBS).split(",")
    ports = os.environ.get("ORACLE_PORTS", "1521,1522").split(",")
    creds = {
        "USER": os.environ.get("ORACLE_USER", "system"),
        "PASSWORD": os.environ.get("ORACLE_PASSWORD", "password"),
    }
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.oracle",
            "NAME": f"{os.environ.get('ORACLE_HOST', 'localhost')}:{ports[0]}/{dbs[0]}",
            **creds,
        }
    }
    if len(dbs) > 1:
        DATABASES["secondary"] = {
            "ENGINE": "django.db.backends.oracle",
            "NAME": f"{os.environ.get('ORACLE_HOST', 'localhost')}:{ports[1]}/{dbs[1]}",
            **creds,
        }
DEFAULT_AUTO_FIELD = "django.db.models.AutoField"
INSTALLED_APPS = [
    "polymorphic.tests.examples.integrations",
    "polymorphic.tests",
    "polymorphic.tests.deletion",
    "polymorphic.tests.other",
    "polymorphic.tests.test_migrations",
    "polymorphic.tests.examples.views",
    "polymorphic",
    "django.contrib.staticfiles",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.messages",
    "django.contrib.sessions",
    "django.contrib.sites",
    "django.contrib.admin",
]

# Add reversion if installed
try:
    import reversion  # noqa: F401

    INSTALLED_APPS.insert(0, "reversion")
    INSTALLED_APPS.insert(0, "polymorphic.tests.examples.integrations.reversion")
except ImportError:
    pass

# Add extra_views if installed
try:
    import extra_views  # noqa: F401

    INSTALLED_APPS.insert(0, "polymorphic.tests.examples.integrations.extra_views")
except ImportError:
    pass


MIDDLEWARE = (
    "django.middleware.common.CommonMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
)
SITE_ID = 3
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": (),
        "OPTIONS": {
            "loaders": (
                "django.template.loaders.filesystem.Loader",
                "django.template.loaders.app_directories.Loader",
            ),
            "context_processors": (
                "django.template.context_processors.debug",
                "django.template.context_processors.i18n",
                "django.template.context_processors.media",
                "django.template.context_processors.request",
                "django.template.context_processors.static",
                "django.contrib.messages.context_processors.messages",
                "django.contrib.auth.context_processors.auth",
            ),
        },
    }
]
POLYMORPHIC_TEST_SWAPPABLE = "polymorphic.swappedmodel"
SECRET_KEY = "supersecret"
STATIC_URL = "/static/"

ALLOWED_HOSTS = ["*"]

ROOT_URLCONF = "polymorphic.tests.urls"

USE_TZ = False

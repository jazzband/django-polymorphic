import dj_database_url

DEBUG = False
DATABASES = {
    "default": dj_database_url.config(
        env="PRIMARY_DATABASE",
        default="sqlite://:memory:",
    ),
    "secondary": dj_database_url.config(
        env="SECONDARY_DATABASE",
        default="sqlite://:memory:",
    ),
}
DEFAULT_AUTO_FIELD = "django.db.models.AutoField"
INSTALLED_APPS = (
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.messages",
    "django.contrib.sessions",
    "django.contrib.sites",
    "django.contrib.admin",
    "polymorphic",
    "polymorphic.tests",
)
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
ROOT_URLCONF = None
SECRET_KEY = "supersecret"

#!/usr/bin/env python
import os
import sys

from django.conf import settings, global_settings as default_settings
from django.core.management import execute_from_command_line
import django


# Give feedback on used versions
sys.stderr.write('Using Python version {0} from {1}\n'.format(
    sys.version[:5], sys.executable)
)
sys.stderr.write('Using Django version {0} from {1}\n'.format(
    django.get_version(),
    os.path.dirname(os.path.abspath(django.__file__)))
)

if not settings.configured:
    settings.configure(
        DEBUG=True,
        TEMPLATE_DEBUG=True,
        DATABASES={
            'default': {
                'ENGINE': 'django.db.backends.sqlite3',
                'NAME': ':memory:'
            }
        },
        TEMPLATE_LOADERS=(
            'django.template.loaders.app_directories.Loader',
        ),
        TEMPLATE_CONTEXT_PROCESSORS=(
            # list() is only needed for older versions of django where this is
            # a tuple:
            list(default_settings.TEMPLATE_CONTEXT_PROCESSORS) + [
                'django.core.context_processors.request',
            ]
        ),
        TEST_RUNNER=(
            'django.test.runner.DiscoverRunner' if django.VERSION >= (1, 7)
            else 'django.test.simple.DjangoTestSuiteRunner'
        ),
        INSTALLED_APPS=(
            'django.contrib.auth',
            'django.contrib.contenttypes',
            'django.contrib.messages',
            'django.contrib.sites',
            'django.contrib.admin',
            'polymorphic',
        ),
        MIDDLEWARE_CLASSES=(),
        SITE_ID=3,
    )


def runtests():
    argv = sys.argv[:1] + ['test', 'polymorphic', '--traceback'] + sys.argv[1:]
    execute_from_command_line(argv)

if __name__ == '__main__':
    runtests()

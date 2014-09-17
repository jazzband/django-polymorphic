#!/usr/bin/env python
from django.conf import settings, global_settings as default_settings
from django.core.management import call_command
from os.path import dirname, realpath
import django
import sys
import os


# Give feedback on used versions
sys.stderr.write('Using Python version {0} from {1}\n'.format(sys.version[:5], sys.executable))
sys.stderr.write('Using Django version {0} from {1}\n'.format(
    django.get_version(),
    os.path.dirname(os.path.abspath(django.__file__)))
)


# Detect location and available modules
module_root = dirname(realpath(__file__))

test_runner = 'django.test.runner.DiscoverRunner'
if django.VERSION[:2] < (1, 6):
    test_runner = 'django.test.simple.DjangoTestSuiteRunner'

# Inline settings file
settings.configure(
    DEBUG = False,  # will be False anyway by DjangoTestRunner.
    TEMPLATE_DEBUG = False,
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': ':memory:'
        }
    },
    TEMPLATE_LOADERS = (
        'django.template.loaders.app_directories.Loader',
    ),
    TEMPLATE_CONTEXT_PROCESSORS = default_settings.TEMPLATE_CONTEXT_PROCESSORS + (
        'django.core.context_processors.request',
    ),
    INSTALLED_APPS = (
        'django.contrib.auth',
        'django.contrib.contenttypes',
        'django.contrib.messages',
        'django.contrib.sites',
        'django.contrib.admin',
        'polymorphic',
    ),
    SITE_ID = 3,
    TEST_RUNNER = test_runner,
    MIDDLEWARE_CLASSES = (),
)

if django.VERSION[:2] > (1, 6):
    django.setup()
    call_command('migrate', verbosity=1, interactive=False)
else:
    call_command('syncdb', verbosity=1, interactive=False)


# ---- app start
verbosity = 2 if '-v' in sys.argv else 1

from django.test.utils import get_runner
TestRunner = get_runner(settings)  # DjangoTestSuiteRunner
runner = TestRunner(verbosity=verbosity, interactive=True, failfast=False)
failures = runner.run_tests(['polymorphic'])

if failures:
    sys.exit(bool(failures))

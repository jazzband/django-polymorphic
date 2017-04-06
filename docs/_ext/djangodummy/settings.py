# Settings file to allow parsing API documentation of Django modules,
# and provide defaults to use in the documentation.
#
# This file is placed in a subdirectory,
# so the docs root won't be detected by find_packages()

# Display sane URLs in the docs:
STATIC_URL = '/static/'

# Avoid error for missing the secret key
SECRET_KEY = 'docs'

INSTALLED_APPS = [
    'django.contrib.contenttypes',
]

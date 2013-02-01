#!/usr/bin/env python

# Prepend project subdirectory 'libraries-local' to sys.path.
# This allows us to use/test any version of Django
# (e.g. Django 1.2 subversion) or any other packages/libraries.
import os
import sys
project_path = os.path.dirname(os.path.abspath(__file__))
libs_local_path = os.path.join(project_path, 'libraries-local')
if libs_local_path not in sys.path:
    sys.path.insert(1, libs_local_path)

sys.stderr.write("using Python version: %s\n" % sys.version[:5])

import django
sys.stderr.write("using Django version: %s, from %s\n" % (
        django.get_version(),
        os.path.dirname(os.path.abspath(django.__file__))))

# vanilla Django manage.py from here on:

from django.core.management import execute_manager
try:
    import settings  # Assumed to be in the same directory.
except ImportError:
    import sys
    sys.stderr.write("Error: Can't find the file 'settings.py' in the directory containing %r. It appears you've customized things.\nYou'll have to run django-admin.py, passing it your settings module.\n(If the file settings.py does indeed exist, it's causing an ImportError somehow.)\n" % __file__)
    sys.exit(1)

if __name__ == "__main__":
    execute_manager(settings)

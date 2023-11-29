#!/usr/bin/env python
import os
import sys

from setuptools import setup

# When creating the sdist, make sure the django.mo file also exists:
if "sdist" in sys.argv or "develop" in sys.argv:
    os.chdir("polymorphic")
    try:
        from django.core import management

        management.call_command("compilemessages", stdout=sys.stderr, verbosity=1)
    except ImportError:
        if "sdist" in sys.argv:
            raise
    finally:
        os.chdir("..")

setup()

#!/usr/bin/env python
import os
import sys

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "example.settings")

    # Import polymorphic from this folder.
    SRC_ROOT = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
    sys.path.insert(0, SRC_ROOT)

    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)

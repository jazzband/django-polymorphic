import sys

from hatchling.builders.hooks.plugin.interface import BuildHookInterface


class CustomBuildHook(BuildHookInterface):
    """
    Hatch build hook to run Django's compilemessages command
    during the build process. This is necessary to ensure that
    translation files are compiled and included in the build output.

    See https://hatch.pypa.io/latest/plugins/build-hook/custom/
    """

    def initialize(self, version, build_data):
        from django.core import management

        management.call_command("compilemessages", stdout=sys.stderr, verbosity=1)

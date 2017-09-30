# -*- coding: utf-8 -*-
"""
Seamless Polymorphic Inheritance for Django Models

Copyright:
This code and affiliated files are (C) by Bert Constantin and individual contributors.
Please see LICENSE and AUTHORS for more information.
"""

import pkg_resources

try:
    __version__ = pkg_resources.require("django-polymorphic")[0].version
except pkg_resources.DistributionNotFound:
    __version__ = None  # for RTD among others


# -*- coding: utf-8 -*-
"""
Seamless Polymorphic Inheritance for Django Models

Copyright:
This code and affiliated files are (C) by Bert Constantin and individual contributors.
Please see LICENSE and AUTHORS for more information.
"""

from polymorphic_model import PolymorphicModel
from manager import PolymorphicManager
from query import PolymorphicQuerySet
from showfields import ShowFields, ShowFieldsAndTypes


VERSION = (0, 5, 0, 'beta')

def get_version():
    version = '%s.%s' % VERSION[0:2]
    if VERSION[2]:
        version += '.%s' % VERSION[2]
    if VERSION[3]:
        version += ' %s' % VERSION[3]
    return version
"""
polymorphic_dumpdata is just a slightly modified version
of Django's dumpdata. In the long term, patching Django's
dumpdata definitely is a better solution.

Use the Django 1.1 or 1.2 variant of dumpdata, depending of the
Django version used.
"""

import django

if django.VERSION[:2]==(1,1):
    from polymorphic_dumpdata_11 import Command

elif django.VERSION[:2]==(1,2):
    from polymorphic_dumpdata_12 import Command

else:
    assert False, 'Django version not supported'

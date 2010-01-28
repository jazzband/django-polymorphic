
import django

if django.VERSION[:2]==(1,1):
    from polymorphic_dumpdata_11 import Command

elif django.VERSION[:2]==(1,2):
    from polymorphic_dumpdata_12 import Command

else:
    assert False, 'Django version not supported'

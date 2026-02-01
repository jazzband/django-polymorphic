from polymorphic.managers import PolymorphicManager
from polymorphic.tests.models import ModelWithMyManagerNoDefault, Model2A


# Mypy should understand that the 'objects' manager is correctly typed
objs: PolymorphicManager[Model2A | ModelWithMyManagerNoDefault] = (
    ModelWithMyManagerNoDefault.objects
)
# just to use 'objs' so no unused var warning occurs
_ = objs.filter(field4="test")

from .managers import PolymorphicManager as PolymorphicManager
from .query import PolymorphicQuerySet as PolymorphicQuerySet
from _typeshed import Incomplete
from django.db.models.base import ModelBase

POLYMORPHIC_SPECIAL_Q_KWORDS: Incomplete
DUMPDATA_COMMAND: Incomplete

class ManagerInheritanceWarning(RuntimeWarning): ...

class PolymorphicModelBase(ModelBase):
    def __new__(cls, model_name, bases, attrs, **kwargs): ...
    @classmethod
    def validate_model_manager(cls, manager, model_name, manager_name): ...
    @property
    def base_objects(self): ...

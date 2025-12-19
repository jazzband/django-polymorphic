from pathlib import Path

from django.db.models.base import ModelBase

from .managers import PolymorphicManager as PolymorphicManager
from .query import PolymorphicQuerySet as PolymorphicQuerySet

POLYMORPHIC_SPECIAL_Q_KWORDS: set[str]
DUMPDATA_COMMAND: Path

class ManagerInheritanceWarning(RuntimeWarning): ...

class PolymorphicModelBase(ModelBase):
    def __new__(cls, model_name, bases, attrs, **kwargs): ...
    @classmethod
    def validate_model_manager(
        cls, manager: PolymorphicManager, model_name: str, manager_name: str
    ): ...
    @property
    def base_objects(self) -> PolymorphicManager: ...

from typing import Any

from django.db.models.base import ModelBase

from .managers import PolymorphicManager as PolymorphicManager
from .query import PolymorphicQuerySet as PolymorphicQuerySet

POLYMORPHIC_SPECIAL_Q_KWORDS: set[str]
DUMPDATA_COMMAND: str

class ManagerInheritanceWarning(RuntimeWarning): ...

class PolymorphicModelBase(ModelBase):
    def __new__(
        cls, model_name: str, bases: tuple[type, ...], attrs: dict[str, Any], **kwargs: Any
    ): ...
    @classmethod
    def validate_model_manager(
        cls, manager: PolymorphicManager[Any], model_name: str, manager_name: str
    ): ...
    @property
    def base_objects(self) -> PolymorphicManager[Any]: ...

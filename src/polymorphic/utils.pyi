from typing import Any, TypeVar

from django.db.models import Model

from polymorphic.base import PolymorphicModelBase as PolymorphicModelBase
from polymorphic.models import PolymorphicModel as PolymorphicModel

_M = TypeVar("_M", bound=Model)

def reset_polymorphic_ctype(*models: type[Model], **filters: Any) -> None: ...
def sort_by_subclass(*classes: type[_M]) -> list[type[_M]]: ...
def get_base_polymorphic_model(
    ChildModel: type[Model], allow_abstract: bool = False
) -> type[Model] | None: ...

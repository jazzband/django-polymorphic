"""
ModelAdmin code to display polymorphic models.

The admin consists of a parent admin (which shows in the admin with a list),
and a child admin (which is used internally to show the edit/delete dialog).
"""
from .parentadmin import PolymorphicParentModelAdmin
from .childadmin import PolymorphicChildModelAdmin
from .forms import PolymorphicModelChoiceForm
from .filters import PolymorphicChildModelFilter

__all__ = (
    'PolymorphicModelChoiceForm', 'PolymorphicParentModelAdmin',
    'PolymorphicChildModelAdmin', 'PolymorphicChildModelFilter'
)

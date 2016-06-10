"""
ModelAdmin code to display polymorphic models.

The admin consists of a parent admin (which shows in the admin with a list),
and a child admin (which is used internally to show the edit/delete dialog).
"""
# Admins for the regular models
from .parentadmin import PolymorphicParentModelAdmin
from .childadmin import PolymorphicChildModelAdmin

# Utils
from .forms import PolymorphicModelChoiceForm
from .filters import PolymorphicChildModelFilter

# Inlines
from .inlines import (
    PolymorphicParentInlineModelAdmin,
    PolymorphicChildInlineModelAdmin,
)

# Helpers for the inlines
from .helpers import (
    InlinePolymorphicAdminForm,
    InlinePolymorphicAdminFormSet,
    PolymorphicInlineSupportMixin,  # mixin for the regular model admin!
)

# Expose generic admin features too. There is no need to split those
# as the admin already relies on contenttypes.
from .generic import (
    PolymorphicParentGenericInlineModelAdmin,
    PolymorphicChildGenericInlineModelAdmin,
)

__all__ = (
    'PolymorphicParentModelAdmin',
    'PolymorphicChildModelAdmin',
    'PolymorphicModelChoiceForm',
    'PolymorphicChildModelFilter',
    'InlinePolymorphicAdminForm',
    'InlinePolymorphicAdminFormSet',
    'PolymorphicInlineSupportMixin',
    'PolymorphicParentInlineModelAdmin',
    'PolymorphicChildInlineModelAdmin',
    'PolymorphicParentGenericInlineModelAdmin',
    'PolymorphicChildGenericInlineModelAdmin',
)

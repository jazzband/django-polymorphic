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
    PolymorphicInlineModelAdmin,  # base class
    StackedPolymorphicInline,  # stacked inline
)

# Helpers for the inlines
from .helpers import (
    PolymorphicInlineAdminForm,
    PolymorphicInlineAdminFormSet,
    PolymorphicInlineSupportMixin,  # mixin for the regular model admin!
)

# Expose generic admin features too. There is no need to split those
# as the admin already relies on contenttypes.
from .generic import (
    GenericPolymorphicInlineModelAdmin,  # base class
    GenericStackedPolymorphicInline,  # stacked inline
)

__all__ = (
    'PolymorphicParentModelAdmin',
    'PolymorphicChildModelAdmin',
    'PolymorphicModelChoiceForm',
    'PolymorphicChildModelFilter',
    'PolymorphicInlineAdminForm',
    'PolymorphicInlineAdminFormSet',
    'PolymorphicInlineSupportMixin',
    'PolymorphicInlineModelAdmin',
    'StackedPolymorphicInline',
    'GenericPolymorphicInlineModelAdmin',
    'GenericStackedPolymorphicInline',
)

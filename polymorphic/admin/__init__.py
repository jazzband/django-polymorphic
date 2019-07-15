"""
ModelAdmin code to display polymorphic models.

The admin consists of a parent admin (which shows in the admin with a list),
and a child admin (which is used internally to show the edit/delete dialog).
"""
# Admins for the regular models
from .parentadmin import PolymorphicParentModelAdmin  # noqa
from .childadmin import PolymorphicChildModelAdmin
from .filters import PolymorphicChildModelFilter

# Utils
from .forms import PolymorphicModelChoiceForm

# Expose generic admin features too. There is no need to split those
# as the admin already relies on contenttypes.
from .generic import GenericPolymorphicInlineModelAdmin  # base class
from .generic import GenericStackedPolymorphicInline  # stacked inline

# Helpers for the inlines
from .helpers import PolymorphicInlineSupportMixin  # mixin for the regular model admin!
from .helpers import PolymorphicInlineAdminForm, PolymorphicInlineAdminFormSet

# Inlines
from .inlines import PolymorphicInlineModelAdmin  # base class
from .inlines import StackedPolymorphicInline  # stacked inline

__all__ = (
    "PolymorphicParentModelAdmin",
    "PolymorphicChildModelAdmin",
    "PolymorphicModelChoiceForm",
    "PolymorphicChildModelFilter",
    "PolymorphicInlineAdminForm",
    "PolymorphicInlineAdminFormSet",
    "PolymorphicInlineSupportMixin",
    "PolymorphicInlineModelAdmin",
    "StackedPolymorphicInline",
    "GenericPolymorphicInlineModelAdmin",
    "GenericStackedPolymorphicInline",
)

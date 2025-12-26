"""
Widgets for polymorphic admin.
"""

from django.contrib.admin.widgets import ForeignKeyRawIdWidget
from django.contrib.contenttypes.models import ContentType


class PolymorphicForeignKeyRawIdWidget(ForeignKeyRawIdWidget):
    """
    A raw ID widget that automatically filters the popup change list by content type.

    When used with polymorphic models, this widget adds a 'polymorphic_ctype' parameter
    to the popup URL, which filters the queryset to show only instances of the specific
    child model type.

    Example usage in a child admin::

        from polymorphic.admin import PolymorphicChildModelAdmin, PolymorphicForeignKeyRawIdWidget

        class ChildAAdmin(PolymorphicChildModelAdmin):
            base_model = ParentModel
            raw_id_fields = ['related_child_b']

            def formfield_for_foreignkey(self, db_field, request, **kwargs):
                if db_field.name in self.raw_id_fields:
                    kwargs['widget'] = PolymorphicForeignKeyRawIdWidget(
                        db_field.remote_field, self.admin_site
                    )
                return super().formfield_for_foreignkey(db_field, request, **kwargs)
    """

    def url_parameters(self):
        """
        Add polymorphic_ctype parameter to the popup URL if the related model is polymorphic.
        """
        # Handle None rel case before calling super
        if not self.rel:
            return {}

        params = super().url_parameters()

        # Get the content type for the related model
        ctype_id = self._get_polymorphic_ctype()
        if ctype_id:
            params["polymorphic_ctype"] = ctype_id

        return params

    def _get_polymorphic_ctype(self):
        """
        Get the content type ID for the related model if it's polymorphic.

        Returns:
            int or None: The content type ID if the model is polymorphic, None otherwise.
        """
        if not self.rel:
            return None

        related_model = self.rel.model

        # Check if the model has polymorphic_ctype field (indicating it's polymorphic)
        if not hasattr(related_model, "polymorphic_ctype"):
            return None

        # Get the content type for this specific model
        try:
            ctype = ContentType.objects.get_for_model(related_model, for_concrete_model=False)
            return ctype.id
        except Exception:
            # If anything goes wrong, just don't add the parameter
            return None

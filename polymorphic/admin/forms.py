from django import forms
from django.contrib.admin.widgets import AdminRadioSelect
from django.utils.translation import ugettext_lazy as _


class PolymorphicModelChoiceForm(forms.Form):
    """
    The default form for the ``add_type_form``. Can be overwritten and replaced.
    """
    #: Define the label for the radiofield
    type_label = _('Type')

    ct_id = forms.ChoiceField(label=type_label, widget=AdminRadioSelect(attrs={'class': 'radiolist'}))

    def __init__(self, *args, **kwargs):
        # Allow to easily redefine the label (a commonly expected usecase)
        super(PolymorphicModelChoiceForm, self).__init__(*args, **kwargs)
        self.fields['ct_id'].label = self.type_label

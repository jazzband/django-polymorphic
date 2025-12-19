from _typeshed import Incomplete
from django import forms

class PolymorphicModelChoiceForm(forms.Form):
    type_label: Incomplete
    ct_id: Incomplete
    def __init__(self, *args, **kwargs) -> None: ...

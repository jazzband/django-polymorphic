from _typeshed import Incomplete
from django_stubs import forms

class PolymorphicModelChoiceForm(forms.Form):
    type_label: str
    ct_id: Incomplete
    def __init__(self, *args, **kwargs) -> None: ...

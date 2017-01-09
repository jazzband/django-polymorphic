polymorphic.formsets
====================

.. automodule:: polymorphic.formsets


Model formsets
--------------

.. autofunction:: polymorphic.formsets.polymorphic_modelformset_factory

.. autoclass:: polymorphic.formsets.PolymorphicFormSetChild


Inline formsets
---------------

.. autofunction:: polymorphic.formsets.polymorphic_inlineformset_factory


Generic formsets
----------------

.. autofunction:: polymorphic.formsets.generic_polymorphic_inlineformset_factory


Low-level features
------------------

The internal machinery can be used to extend the formset classes. This includes:

.. autofunction:: polymorphic.formsets.polymorphic_child_forms_factory

.. autoclass:: polymorphic.formsets.BasePolymorphicModelFormSet
    :show-inheritance:

.. autoclass:: polymorphic.formsets.BasePolymorphicInlineFormSet
    :show-inheritance:

.. autoclass:: polymorphic.formsets.BaseGenericPolymorphicInlineFormSet
    :show-inheritance:

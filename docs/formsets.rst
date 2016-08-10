Formsets
========

Polymorphic models can be used in formsets.

Use the :func:`polymorphic.formsets.polymorphic_inlineformset_factory` function to generate the formset.
As extra parameter, the factory needs to know how to display the child models.
Provide a list of :class:`polymorphic.formsets.PolymorphicFormSetChild` objects for this

.. code-block:: python

    from polymorphic.formsets import polymorphic_child_forms_factory

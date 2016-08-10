Formsets
========

.. versionadded:: 1.0

Polymorphic models can be used in formsets.

The implementation is almost identical to the regular Django formsets.
As extra parameter, the factory needs to know how to display the child models.
Provide a list of :class:`~polymorphic.formsets.PolymorphicFormSetChild` objects for this.

.. code-block:: python

    from polymorphic.formsets import polymorphic_modelformset_factory, PolymorphicFormSetChild

    ModelAFormSet = polymorphic_modelformset_factory(ModelA, formset_children=(
        PolymorphicFormSetChild(ModelB),
        PolymorphicFormSetChild(ModelC),
    ))

The formset can be used just like all other formsets:

.. code-block:: python

    if request.method == "POST":
        formset = ModelAFormSet(request.POST, request.FILES, queryset=ModelA.objects.all())
        if formset.is_valid():
            formset.save()
    else:
        formset = ModelAFormSet(queryset=ModelA.objects.all())

Like standard Django formsets, there are 3 factory methods available:

* :func:`~polymorphic.formsets.polymorphic_modelformset_factory` - create a regular model formset.
* :func:`~polymorphic.formsets.polymorphic_inlineformset_factory` - create a inline model formset.
* :func:`~polymorphic.formsets.generic_polymorphic_inlineformset_factory` - create an inline formset for a generic foreign key.

Each one uses a different base class:

* :class:`~polymorphic.formsets.BasePolymorphicModelFormSet`
* :class:`~polymorphic.formsets.BasePolymorphicInlineFormSet`
* :class:`~polymorphic.formsets.BaseGenericPolymorphicInlineFormSet`

When needed, the base class can be overwritten and provided to the factory via the ``formset`` parameter.

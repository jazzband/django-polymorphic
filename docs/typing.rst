Type Hints
==========

.. versionadded:: 4.11

:pypi:`django-polymorphic` is now fully typed, and ships with type hints for all public
APIs. Typing is checked with :pypi:`mypy` and :pypi:`pyright` in the CI pipeline.

The utility and power of the Django ORM derives from its dynamism but this makes static typing
more difficult. There are *no additional runtime dependencies* but **to use the packaged type hint
classes and descriptors, you must install the following in your type checking context**:

* :pypi:`django-stubs` (required)
* :pypi:`django-stubs-ext` (optional)

.. tip::

    The most useful type hints to add to your own code will make it so your type checking system
    knows which model types your :class:`~polymorphic.managers.PolymorphicManager` and
    :class:`~polymorphic.managers.PolymorphicQuerySet` objects might return.

Correct type hints for polymorphic managers and querysets cannot be automatically inferred - you
will have to add them explicitly if you want them:

.. _typing_managers:

Managers
--------

You can type your managers like this. It might not always be the case that you can add hints for all
child model types, especially if they are included in dependent apps. You can alleviate some of this
complexity with forward type references but strict typing may not always be appropriate.

.. literalinclude:: ../src/polymorphic/tests/examples/type_hints/managers/models.py
    :language: python
    :linenos:


.. code-block:: python

    ParentModel.objects.all()  # type: PolymorphicQuerySet[ParentModel | Child1 | Child2]
    ParentModel.objects.instance_of(Child1)  # type: PolymorphicQuerySet[Child1]
    Child1.objects.non_polymorphic()  # type: QuerySet[Child1]

.. _typing_foreign_key:

Foreign Key
-----------

:pypi:`django-polymorphic` includes several :ref:`type hint descriptors <type_hint_descriptors>`.
You can use them to type your forward and reverse relationship fields. For foreign key relationships
we provide :class:`~polymorphic.managers.PolymorphicForwardManyToOneDescriptor` and
:class:`~polymorphic.managers.PolymorphicReverseManyToOneDescriptor`:

.. literalinclude:: ../src/polymorphic/tests/examples/type_hints/fk/models.py
    :language: python
    :linenos:

.. code-block:: python

    RelatedModel().parent: Optional[ParentModel | Child1 | Child2]
    RelatedModel().children.all(): PolymorphicQuerySet[ParentModel | Child1 | Child2]

.. _typing_one_to_one:

One to One
----------
For foreign key relationships
we provide :class:`~polymorphic.managers.PolymorphicForwardOneToOneDescriptor` and
:class:`~polymorphic.managers.PolymorphicReverseOneToOneDescriptor`:

.. literalinclude:: ../src/polymorphic/tests/examples/type_hints/one2one/models.py
    :language: python
    :linenos:

.. code-block:: python

    RelatedModel().parent_forward: ParentModel | Child1 | Child2 | None
    RelatedModel().parent_reverse: ParentModel | Child1 | Child2

.. _typing_many_to_many:

Many to Many
------------

You can use the same :class:`~polymorphic.managers.PolymorphicManyToManyDescriptor` for
both forward and reverse :class:`~django.db.models.ManyToManyField` relationships.

The following example shows two :class:`~django.db.models.ManyToManyField` relationships:

1. :class:`~polymorphic.models.PolymorphicModel` -> :class:`~django.db.models.Model`
   (with a custom through model)
2. :class:`~django.db.models.Model` -> :class:`~polymorphic.models.PolymorphicModel`
   (with the default through model)

For the custom through model you will need to annotate using the :ref:`foreign key descriptors
<typing_foreign_key>` as well.

.. literalinclude:: ../src/polymorphic/tests/examples/type_hints/m2m/models.py
    :language: python
    :linenos:

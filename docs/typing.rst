Type Hints
==========

.. versionadded:: 4.11

:pypi:`django-polymorphic` is now fully typed, and ships with type hints for all public
APIs. Typing is checked against :pypi:`mypy` and :pypi:`pyright` in the CI pipeline.

The utility and power of the Django ORM derives from its dynamism. This however makes static type
checking more difficult. To use the type hints effectively, it is recommended to use
:pypi:`django-stubs` and :pypi:`django-stubs-ext` which provides type hints for the Django ORM
itself.`

.. tip::

    The most useful type hints to add to your own code will make it so your type checking system
    knows which model types your :class:`~polymorphic.managers.PolymorphicManager` and
    :class:`~polymorphic.managers.PolymorphicQuerySet` objects might return.

Correct type hints for polymorphic managers and querysets cannot be automatically inferred - you
will have to add them explicitly if you want them:

.. literalinclude:: ../src/polymorphic/tests/examples/type_hints/models.py
    :language: python
    :linenos:

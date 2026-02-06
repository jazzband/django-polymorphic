.. _integrations:

Integrations
============

When integrating polymorphic models into third party apps you have three primary options:

0. Hope it just works (it might!).
1. Ensure the querysets the third party apps see are
   :meth:`not polymorphic <polymorphic.query.PolymorphicQuerySet.non_polymorphic>`.
2. Override or extend relevant third party app code to work with polymorphic querysets.

If it does not just work, option 1 is usually the easiest. We provide some integrations in
:mod:`polymorphic.contrib` for popular third party apps and provide guidance for others below.

This page does not exhaustively cover all integrations. If you feel your integration need is
very common you may consider opening a PR to either provide support in code or documentation here.

This page covers supported and tested integration advice. For all other integration advice please
refer to `our integrations discussion page
<https://github.com/jazzband/django-polymorphic/discussions/categories/integrations>`_.

For the integration examples on this page, we use the following polymorphic model hierarchy:

.. literalinclude:: ../../src/polymorphic/tests/examples/integrations/models.py
    :language: python
    :linenos:


.. _django-django-guardian-support:

:pypi:`django-guardian`
-----------------------

.. versionadded:: 1.0.2

No special modifications are required to integrate with :pypi:`django-guardian`. However, if you
would like all object level permissions to be managed at the base model level, rather than have
unique permissions for each polymorphic subclass, then you can use the helper function
:func:`polymorphic.contrib.guardian.get_polymorphic_base_content_type` to unify the permissions
for your entire polymorphic model tree into a single namespace a the base level:

.. code-block:: python

    GUARDIAN_GET_CONTENT_TYPE = \
        "polymorphic.contrib.guardian.get_polymorphic_base_content_type"

This option requires :pypi:`django-guardian` >= 1.4.6. Details about how this option works are
available in the `django-guardian documentation
<https://django-guardian.readthedocs.io/en/stable/configuration>`_.

.. _django-extra-views-support:

:pypi:`django-extra-views`
--------------------------

.. versionadded:: 1.1

The :mod:`polymorphic.contrib.extra_views` package provides classes to display polymorphic formsets
using the classes from :pypi:`django-extra-views`. See the documentation of:

* :class:`~polymorphic.contrib.extra_views.PolymorphicFormSetView`
* :class:`~polymorphic.contrib.extra_views.PolymorphicInlineFormSetView`
* :class:`~polymorphic.contrib.extra_views.PolymorphicInlineFormSet`

.. tip::

    The complete working code for this example can be found `in the extra_views integration test
    <https://github.com/jazzband/django-polymorphic/tree/HEAD/src/polymorphic/tests/examples/integrations/extra_views>`_.


Example View
~~~~~~~~~~~~

Here's how to create a view using :class:`~polymorphic.contrib.extra_views.PolymorphicFormSetView`
to handle polymorphic formsets:

.. literalinclude:: ../../src/polymorphic/tests/examples/integrations/extra_views/views.py
    :language: python
    :linenos:


URL Configuration
~~~~~~~~~~~~~~~~~

Configure the URL patterns to route to your formset view:

.. literalinclude:: ../../src/polymorphic/tests/examples/integrations/extra_views/urls.py
    :language: python
    :linenos:


Template
~~~~~~~~

The template for rendering the formset:

.. literalinclude:: ../../src/polymorphic/tests/examples/integrations/extra_views/templates/extra_views/article_formset.html
    :language: html+django

``model_name`` is a template tag implemented like so:

.. literalinclude:: ../../src/polymorphic/tests/examples/integrations/extra_views/templatetags/extra_views_tags.py
    :language: python
    :lines: 6-

.. _django-reversion-support:

:pypi:`django-reversion`
------------------------

Support for :pypi:`django-reversion` works as expected with polymorphic models. We just need to
do two things:

1. Inherit our admin classes from both :class:`~polymorphic.admin.PolymorphicParentModelAdmin` /
   :class:`~polymorphic.admin.PolymorphicChildModelAdmin` and
   :ref:`VersionAdmin <django-reversion:versionadmin>`.
2. Override the ``admin/polymorphic/object_history.html`` template.

.. tip::

    The complete working code for this example can be found `in the reversion integration test
    <https://github.com/jazzband/django-polymorphic/tree/HEAD/src/polymorphic/tests/examples/integrations/reversion>`_.


Admin Configuration
~~~~~~~~~~~~~~~~~~~

The admin configuration combines :class:`~polymorphic.admin.PolymorphicParentModelAdmin` and
:class:`~polymorphic.admin.PolymorphicChildModelAdmin` with
:ref:`VersionAdmin <django-reversion:versionadmin>`:

.. literalinclude:: ../../src/polymorphic/tests/examples/integrations/reversion/admin.py
    :language: python
    :linenos:


Custom Template
~~~~~~~~~~~~~~~

Since both :class:`~polymorphic.admin.PolymorphicParentModelAdmin` and
:ref:`VersionAdmin <django-reversion:versionadmin>`. define ``object_history.html`` template, you
need to create a custom template that combines both:

.. literalinclude:: ../../src/polymorphic/tests/examples/integrations/reversion/templates/admin/polymorphic/object_history.html
    :language: html+django

This makes sure both the reversion template is used, and the breadcrumb is corrected for the
polymorphic model using the :templatetag:`breadcrumb_scope`
tag.

.. _model-bakery:

:pypi:`model-bakery`
--------------------

:pypi:`model-bakery` does not work without without special configuration for polymorphic models
because it overrides the :attr:`~polymorphic.models.PolymorphicModel.polymorphic_ctype` field.
The best option to make it work in all cases is to `supply a custom Baker
<https://model-bakery.readthedocs.io/en/latest/how_bakery_behaves.html#customizing-baker>`_ class
that fills in all fields except :attr:`~polymorphic.models.PolymorphicModel.polymorphic_ctype`:

.. code-block:: python
    :linenos:
    :caption: yoursite/tests/baker.py

    from polymorphic.models import PolymorphicModel
    from model_bakery import baker


    class PolymorphicAwareBaker(baker.Baker):
        """
        Our custom model baker ignores the polymorphic_ctype field on all polymorphic
        models - this allows the base class to set it correctly.
        See https://github.com/python/pythondotorg/issues/2567
        """

        def get_fields(self):
            fields = super().get_fields()
            if issubclass(self.model, PolymorphicModel):
                fields = {
                    field
                    for field in fields
                    if field.name != "polymorphic_ctype"
                }
            return fields


Then in your test settings file:

.. code-block:: python

    BAKER_CUSTOM_CLASS = "yoursite.tests.baker.PolymorphicAwareBaker"

You may also simply pass the correct :class:`~django.contrib.contenttypes.models.ContentType`
instance to the :attr:`~polymorphic.models.PolymorphicModel.polymorphic_ctype` field when creating
polymorphic model instances with ``make()``


Other Integrations
------------------

.. toctree::
   :maxdepth: 1
   :titlesonly:

   drf

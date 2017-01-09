"""
Template tags to use in the admin.

The ``{% breadcrumb_scope ... %}`` tag makes sure the ``{{ opts }}`` and ``{{ app_label }}``
values are temporary based on the provided ``{{ base_opts }}``.
This allows fixing the breadcrumb in admin templates:

.. code-block:: html+django

    {% extends "admin/change_form.html" %}
    {% load polymorphic_admin_tags %}

    {% block breadcrumbs %}
      {% breadcrumb_scope base_opts %}{{ block.super }}{% endbreadcrumb_scope %}
    {% endblock %}
"""

.. _views:

Class Based Views
=================

While :pypi:`django-polymorphic` provides full admin integration, you might want to build front-end
views that allow users to create polymorphic objects. Since a single URL cannot easily handle
different form fields for different models, the best approach is a two-step process:

1.  **Step 1:** Let the user choose the desired type.
2.  **Step 2:** Display the form for that specific type.

.. tip::

    The code for this example can be found `here
    <https://github.com/jazzband/django-polymorphic/tree/HEAD/src/polymorphic/tests/examples/views>`_.

This example uses model labels (e.g., ``app.ModelName``) to identify the selected type. Assume we
have the following models:

.. literalinclude:: ../src/polymorphic/tests/examples/views/models.py
    :language: python
    :linenos: 

Step 1: Selecting the Type
--------------------------

Create a form that allows users select the desired model type. You can use a simple choice field
for this.

.. literalinclude:: ../src/polymorphic/tests/examples/views/views.py
    :language: python
    :lines: 1-45
    :linenos:

Your template ``project_type_select.html``, might look like this:

.. literalinclude:: ../src/polymorphic/tests/examples/views/templates/project_type_select.html
    :language: html

Step 2: Displaying the Form
---------------------------

The creation view needs to dynamically select the correct form class based on the chosen model label.

.. literalinclude:: ../src/polymorphic/tests/examples/views/views.py
    :language: python
    :lines: 47-
    :linenos:


In your template ``project_form.html``, make sure to preserve the ``model`` parameter:

.. literalinclude:: ../src/polymorphic/tests/examples/views/templates/project_form.html
    :language: html


And our urls might look like this:

.. literalinclude:: ../src/polymorphic/tests/examples/views/urls.py
    :linenos:

Using ``extra_views``
---------------------

If you are using :pypi:`django-extra-views`, :pypi:`django-polymorphic` provides mixins to help with formsets.
See :mod:`polymorphic.contrib.extra_views` for more details.

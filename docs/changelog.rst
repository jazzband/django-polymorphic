Changelog
==========


Version 0.6
-----------

* Admin integration has been simplified.  It became less hacky and therefore
  fixed lots of issues.
* Admin integration of a foreign key to a child polymorphic model is fully
  working.
* Full django-grappelli compatibility.
* **Changed** ``PolymorphicParentModelAdmin.child_models`` is now a tuple
  of Models.  Before it was a tuple of (Model, ModelAdmin) tuples.
* **Changed** Child models now have to be registered to the admin site.

If you already use the admin integration, you therefore have to:

* Change

  .. code-block:: python

      child_models = ((ModelA, ModelAChildAdmin), (ModelB, ModelBChildAdmin))

  to

  .. code-block:: python

      child_models = (ModelA, ModelB)

* Register the child models in the classical way:

  .. code-block:: python

      admin.site.register(ModelA, ModelAChildAdmin)
      admin.site.register(ModelB, ModelBChildAdmin)

See :ref:`the admin example <admin-example>` for more details.


Version 0.5.4 (in development)
------------------------------

* Fix ``.non_polymorphic()`` to returns a clone of the queryset, instead of effecting the existing queryset.


Version 0.5.3 (2013-09-17)
--------------------------

* Fix TypeError when ``base_form`` was not defined.
* Fix passing ``/admin/app/model/id/XYZ`` urls to the correct admin backend.
  There is no need to include a ``?ct_id=..`` field, as the ID already provides enough information.


Version 0.5.2 (2013-09-05)
--------------------------

* Fix Grappelli_ breadcrumb support in the views.
* Fix unwanted ``___`` handling in the ORM when a field name starts with an underscore;
  this detects you meant ``relatedfield__ _underscorefield`` instead of ``ClassName___field``.
* Fix missing permission check in the "add type" view. This was caught however in the next step.
* Fix admin validation errors related to additional non-model form fields.


Version 0.5.1 (2013-07-05)
--------------------------

* Add Django 1.6 support.
* Fix Grappelli_ theme support in the "Add type" view.


Version 0.5 (2013-04-20)
------------------------

* Add Python 3.2 and 3.3 support
* Fix errors with ContentType objects that don't refer to an existing model.


Version 0.4.2 (2013-04-10)
--------------------------

* Used proper ``__version__`` marker.


Version 0.4.1 (2013-04-10)
--------------------------

* Add Django 1.5 and 1.6 support
* Add proxy model support
* Add default admin ``list_filter`` for polymorphic model type.
* Fix queryset support of related objects.
* Performed an overall cleanup of the project
* **Deprecated** the ``queryset_class`` argument of the ``PolymorphicManager`` constructor, use the class attribute instead.
* **Dropped** Django 1.1, 1.2 and 1.3 support


Version 0.4 (2013-03-25)
------------------------

* Update example project for Django 1.4
* Added tox and Travis configuration


Version 0.3.1 (2013-02-28)
--------------------------

* SQL optimization, avoid query in pre_save_polymorphic()


Version 0.3 (2013-02-28)
------------------------

Many changes to the codebase happened, but no new version was released to pypi for years.
0.3 contains fixes submitted by many contributors, huge thanks to everyone!

* Added a polymorphic admin interface.
* PEP8 and code cleanups by various authors


Version 0.2 (2011-04-27)
------------------------

The 0.2 release serves as legacy release.
It supports Django 1.1 up till 1.4 and Python 2.4 up till 2.7.

For a detailed list of it's changes, see the :doc:`archived changelog <changelog_archive>`.

.. _Grappelli: http://grappelliproject.com/

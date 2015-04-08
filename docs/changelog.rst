Changelog
==========

Version 0.7 (2015-04-08)
------------------------

* Added Django 1.8 support
* Added support for custom primary key defined using ``mybase_ptr = models.OneToOneField(BaseClass, parent_link=True, related_name="...")``.
* Fixed Python 3 issue in the admin
* Fixed ``_default_manager`` to be consistent with Django, it's now assigned directly instead of using ``add_to_class()``
* Fixed 500 error for admin URLs without a '/', e.g. ``admin/app/parentmodel/id``.
* Fixed preserved filter for Django admin in delete views
* Removed test noise for diamond inheritance problem (which Django 1.7 detects)


Version 0.6.1 (2014-12-30)
--------------------------

* Remove Django 1.7 warnings
* Fix Django 1.4/1.5 queryset calls on related objects for unknown methods.
  The ``RelatedManager`` code overrides ``get_query_set()`` while ``__getattr__()`` used the new-style ``get_queryset()``.
* Fix validate_model_fields(), caused errors when metaclass raises errors


Version 0.6 (2014-10-14)
------------------------

* Added Django 1.7 support.
* Added permission check for all child types.
* **BACKWARDS INCOMPATIBILITY:** the ``get_child_type_choices()`` method receives 2 arguments now (request, action).
  If you have overwritten this method in your code, make sure the method signature is updated accordingly.


Version 0.5.6 (2014-07-21)
--------------------------

* Added ``pk_regex`` to the ``PolymorphicParentModelAdmin`` to support non-integer primary keys.
* Fixed passing ``?ct_id=`` to the add view for Django 1.6 (fixes compatibility with django-parler_).


Version 0.5.5 (2014-04-29)
--------------------------

* Fixed ``get_real_instance_class()`` for proxy models (broke in 0.5.4).


Version 0.5.4 (2014-04-09)
--------------------------

* Fix ``.non_polymorphic()`` to returns a clone of the queryset, instead of effecting the existing queryset.
* Fix missing ``alters_data = True`` annotations on the overwritten ``save()`` methods.
* Fix infinite recursion bug in the admin with Django 1.6+
* Added detection of bad ``ContentType`` table data.


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
.. _django-parler: https://github.com/edoburu/django-parler

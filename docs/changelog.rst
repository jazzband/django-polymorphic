Changelog
=========

Version 1.3.1 (2018-04-16)
--------------------------

Backported various fixes from 2.x to support older Django versions:

* Added ``PolymorphicTypeUndefined`` exception for incomplete imported models.
  When a data migration or import creates an polymorphic model,
  the ``polymorphic_ctype_id`` field should be filled in manually too.
  The ``polymorphic.utils.reset_polymorphic_ctype`` function can be used for that.
* Added ``PolymorphicTypeInvalid`` exception when database was incorrectly imported.
* Added ``polymorphic.utils.get_base_polymorphic_model()`` to find the base model for types.
* Using ``base_model`` on the polymorphic admins is no longer required, as this can be autodetected.
* Fixed manager errors for swappable models.
* Fixed ``deleteText`` of ``|as_script_options`` template filter.
* Fixed ``.filter(applabel__ModelName___field=...)`` lookups.
* Fixed proxy model support in formsets.
* Fixed error with .defer and child models that use the same parent.
* Fixed error message when ``polymorphic_ctype_id`` is null.
* Fixed fieldsets recursion in the admin.
* Improved ``polymorphic.utils.reset_polymorphic_ctype()`` to accept models in random ordering.


Version 1.3 (2017-08-01)
------------------------

* **BACKWARDS INCOMPATIBILITY:** Dropped Django 1.4, 1.5, 1.6, 1.7, 1.9 and Python 2.6 support.
  Only official Django releases (1.8, 1.10, 1.11) are supported now.
* Allow expressions to pass unchanged in ``.order_by()``
* Fixed Django 1.11 accessor checks (to support subclasses of ``ForwardManyToOneDescriptor``, like ``ForwardOneToOneDescriptor``)
* Fixed polib syntax error messages in translations.


Version 1.2 (2017-05-01)
------------------------

* Django 1.11 support.
* Fixed ``PolymorphicInlineModelAdmin`` to explictly exclude ``polymorphic_ctype``.
* Fixed Python 3 TypeError in the admin when preserving the query string.
* Fixed Python 3 issue due to ``force_unicode()`` usage instead of ``force_text()``.
* Fixed ``z-index`` attribute for admin menu appearance.


Version 1.1 (2017-02-03)
------------------------

* Added class based formset views in ``polymorphic/contrib/extra_views``.
* Added helper function ``polymorphic.utils.reset_polymorphic_ctype()``.
  This eases the migration old existing models to polymorphic.
* Fixed Python 2.6 issue.
* Fixed Django 1.6 support.


Version 1.0.2 (2016-10-14)
--------------------------

* Added helper function for django-guardian_; add
  ``GUARDIAN_GET_CONTENT_TYPE = 'polymorphic.contrib.guardian.get_polymorphic_base_content_type'``
  to the project settings to let guardian handles inherited models properly.
* Fixed ``polymorphic_modelformset_factory()`` usage.
* Fixed Python 3 bug for inline formsets.
* Fixed CSS for Grappelli, so model choice menu properly overlaps.
* Fixed ``ParentAdminNotRegistered`` exception for models that are registered via a proxy model instead of the real base model.


Version 1.0.1 (2016-09-11)
--------------------------

* Fixed compatibility with manager changes in Django 1.10.1


Version 1.0 (2016-09-02)
------------------------

* Added Django 1.10 support.
* Added **admin inline** support for polymorphic models.
* Added **formset** support for polymorphic models.
* Added support for polymorphic queryset limiting effects on *proxy models*.
* Added support for multiple databases with the ``.using()`` method and ``using=..`` keyword argument.
* Fixed modifying passed ``Q()`` objects in place.

.. note::
   This version provides a new method for registering the admin models.
   While the old method is still supported, we recommend to upgrade your code.
   The new registration style improves the compatibility in the Django admin.

   * Register each ``PolymorphicChildModelAdmin`` with the admin site too.
   * The ``child_models`` attribute of the ``PolymorphicParentModelAdmin`` should be a flat list of all child models.
     The ``(model, admin)`` tuple is obsolete.

   Also note that proxy models will now limit the queryset too.


Fixed since 1.0b1 (2016-08-10)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* Fix formset empty-form display when there are form errors.
* Fix formset empty-form hiding for Grappelli_.
* Fixed packing ``admin/polymorphic/edit_inline/stacked.html`` in the wheel format.


Version 0.9.2 (2016-05-04)
--------------------------

* Fix error when using ``date_hierarchy`` field in the admin
* Fixed Django 1.10 warning in admin add-type view.


Version 0.9.1 (2016-02-18)
--------------------------

* Fixed support for ``PolymorphicManager.from_queryset()`` for custom query sets.
* Fixed Django 1.7 ``changeform_view()`` redirection to the child admin site.
  This fixes custom admin code that uses these views, such as django-reversion_'s ``revision_view()`` / ``recover_view()``.
* Fixed ``.only('pk')`` field support.
* Fixed ``object_history_template`` breadcrumb.
  **NOTE:** when using django-reversion_ / django-reversion-compare_, make sure to implement
  a ``admin/polymorphic/object_history.html`` template in your project that extends
  from ``reversion/object_history.html`` or ``reversion-compare/object_history.html`` respectively.


Version 0.9 (2016-02-17)
------------------------

* Added ``.only()`` and ``.defer()`` support.
* Added support for Django 1.8 complex expressions in ``.annotate()`` / ``.aggregate()``.
* Fix Django 1.9 handling of custom URLs.
  The new change-URL redirect overlapped any custom URLs defined in the child admin.
* Fix Django 1.9 support in the admin.
* Fix setting an extra custom manager without overriding the ``_default_manager``.
* Fix missing ``history_view()`` redirection to the child admin, which is important for django-reversion_ support.
  See the documentation for hints for :ref:`django-reversion-compare support <django-reversion-compare-support>`.


Version 0.8.1 (2015-12-29)
--------------------------

* Fixed support for reverse relations for ``relname___field`` when the field starts with an ``_`` character.
  Otherwise, the query will be interpreted as subclass lookup (``ClassName___field``).


Version 0.8 (2015-12-28)
------------------------

* Added Django 1.9 compatibility.
* Renamed ``polymorphic.manager`` => ``polymorphic.managers`` for consistentcy.
* **BACKWARDS INCOMPATIBILITY:** The import paths have changed to support Django 1.9.
  Instead of ``from polymorphic import X``,
  you'll have to import from the proper package. For example:

.. code-block:: python

    from polymorphic.models import PolymorphicModel
    from polymorphic.managers import PolymorphicManager, PolymorphicQuerySet
    from polymorphic.showfields import ShowFieldContent, ShowFieldType, ShowFieldTypeAndContent

* **BACKWARDS INCOMPATIBILITY:** Removed ``__version__.py`` in favor of a standard ``__version__`` in ``polymorphic/__init__.py``.
* **BACKWARDS INCOMPATIBILITY:** Removed automatic proxying of method calls to the queryset class.
  Use the standard Django methods instead:

.. code-block:: python

    # In model code:
    objects = PolymorphicQuerySet.as_manager()

    # For manager code:
    MyCustomManager = PolymorphicManager.from_queryset(MyCustomQuerySet)



Version 0.7.2 (2015-10-01)
--------------------------

* Added ``queryset.as_manager()`` support for Django 1.7/1.8
* Optimize model access for non-dumpdata usage; avoid ``__getattribute__()`` call each time to access the manager.
* Fixed 500 error when using invalid PK's in the admin URL, return 404 instead.
* Fixed possible issues when using an custom ``AdminSite`` class for the parent object.
* Fixed Pickle exception when polymorphic model is cached.


Version 0.7.1 (2015-04-30)
--------------------------

* Fixed Django 1.8 support for related field widgets.


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
.. _django-guardian: https://github.com/django-guardian/django-guardian
.. _django-parler: https://github.com/django-parler/django-parler
.. _django-reversion: https://github.com/etianen/django-reversion
.. _django-reversion-compare: https://github.com/jedie/django-reversion-compare

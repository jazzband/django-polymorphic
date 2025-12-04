Changelog
=========

v4.2.0 (2025-12-04)
-------------------

* Fixed `The objects which were transmogrified aren't initialized correctly if they implement __init__ method. <https://github.com/jazzband/django-polymorphic/issues/615>`_
* Implemented `Defer to chunk_size parameter on .iterators for fetching get_real_instances() <https://github.com/jazzband/django-polymorphic/pull/672>`_
* Fixed `Show full admin context (breadcrumb and logout nav) in model type selection admin form <https://github.com/jazzband/django-polymorphic/pull/580>`_
* Fixed `Issue with Autocomplete Fields in StackedPolymorphicInline.Child Inline <https://github.com/jazzband/django-polymorphic/issues/546>`_
* Support Python 3.14 and Django 6.0, drop support for EOL python 3.9, Django 3.2, 4.0, 4.1 and 5.0.
* `Modernized package management with new build, test, docs tooling and improved CI 
  <https://github.com/jazzband/django-polymorphic/issues/651>`_.

v4.1.0 (2025-05-20)
-------------------

* `Fixed a bug on Django 5 <https://github.com/jazzband/django-polymorphic/pull/621>`_ where
  `aggregation queries could result in None-type errors <https://github.com/jazzband/django-polymorphic/issues/616>`_
* `Use css variables in the admin css <https://github.com/jazzband/django-polymorphic/pull/622>`_

v4.0.0 (2025-05-20)
-------------------

**There were no breaking changes in this major release**

*This was the first release under* `Jazzband <https://jazzband.co/>`_.

There were many updates modernizing the package and incorporating Jazzband standards:

* Updates to documentation
* Formatting and linting with ruff
* Moving to GHA from Travis CI
* Switch to pytest

Changes that touched the core package code were:

* Remove `legacy Django/python version checks <https://github.com/jazzband/django-polymorphic/pull/567>`_
* Replace `string formats with f-strings <https://github.com/jazzband/django-polymorphic/pull/566>`_
* Removed `deprecated usage of package_resources <https://github.com/jazzband/django-polymorphic/pull/541>`_
    - as of Python 3.12 package_resources was removed. To get prior releases to work on >3.12 you
      would also need to install `setuptools <https://pypi.org/project/setuptools/>`_.
* Fixed `multi field lines do not render in the admin <https://github.com/jazzband/django-polymorphic/pull/539>`_
* Fixed `dark mode rendering in the polymorphic admin <https://github.com/jazzband/django-polymorphic/pull/508>`_

v3.1.0 (2021-11-18)
-------------------

* Added support for Django 4.0.
* Fixed crash when the admin "add type" view has no choices; will show a permission denied.
* Fixed missing ``locale`` folder in sdist.
* Fixed missing ``QuerySet.bulk_create(.., ignore_conflicts=True)`` parameter support.
* Fixed ``FilteredRelation`` support.
* Fixed supporting class keyword arguments in model definitions for ``__init_subclass__()``.
* Fixed including ``polymorphic.tests.migrations`` in the sdist.
* Fixed non-polymorphic parent handling, which has no ``_base_objects``.
* Fixed missing ``widgets`` support for ``modelform_factory()``.
* Fixed ``has_changed`` handling for ``polymorphic_ctype_id`` due to implicit str to int
  conversions.
* Fixed ``Q`` object handling when lists are used (e.g. in django-advanced-filters_).
* Fixed Django Admin support when using a script-prefix.

Many thanks to everyone providing clear pull requests!


v3.0.0 (2020-08-21)
-------------------

* Support for Django 3.X
* Dropped support for python 2.X
* A lot of various fixes and improvements by various authors. Thanks a lot!


v2.1.2 (2019-07-15)
-------------------

* Fix ``PolymorphicInlineModelAdmin`` media jQuery include for Django 2.0+


v2.1.1 (2019-07-15)
-------------------

* Fixed admin import error due to ``isort`` changes.


v2.1 (2019-07-15)
-----------------

* Added Django 2.2 support.
* Changed ``.non_polymorphic()``, to use a different iterable class that completely circumvent
  polymorphic.
* Changed SQL for ``instance_of`` filter: use ``IN`` statement instead of ``OR`` clauses.
* Changed queryset iteration to implement ``prefetch_related()`` support.
* Fixed Django 3.0 alpha compatibility.
* Fixed compatibility with current django-extra-views_ in ``polymorphic.contrib.extra_views``.
* Fixed ``prefetch_related()`` support on polymorphic M2M relations.
* Fixed model subclass ``___`` selector for abstract/proxy models.
* Fixed model subclass ``___`` selector for models with a custom
  ``OneToOneField(parent_link=True)``.
* Fixed unwanted results on calling ``queryset.get_real_instances([])``.
* Fixed unwanted ``TypeError`` exception when ``PolymorphicTypeInvalid`` should have raised.
* Fixed hiding the add-button of polymorphic lines in the Django admin.
* Reformatted all files with black


v2.0.3 (2018-08-24)
-------------------

* Fixed admin crash for Django 2.1 with missing ``use_required_attribute``.


v2.0.2 (2018-02-05)
-------------------

* Fixed manager inheritance behavior for Django 1.11, by automatically enabling
  ``Meta.manager_inheritance_from_future`` if it's not defined. This restores the manager
  inheritance behavior that *django-polymorphic 1.3* provided for Django 1.x projects.
* Fixed internal ``base_objects`` usage.


v2.0.1 (2018-02-05)
-------------------

* Fixed manager inheritance detection for Django 1.11.

  It's recommended to use ``Meta.manager_inheritance_from_future`` so Django 1.x code also inherit
  the ``PolymorphicManager`` in all subclasses. Django 2.0 already does this by default.

* Deprecated the ``base_objects`` manager. Use ``objects.non_polymorphic()`` instead.
* Optimized detection for dumpdata behavior, avoiding the performance hit of ``__getattribute__()``.
* Fixed test management commands


v2.0.0 (2018-01-22)
-------------------

* **BACKWARDS INCOMPATIBILITY:** Dropped Django 1.8 and 1.10 support.
* **BACKWARDS INCOMPATIBILITY:** Removed old deprecated code from 1.0, thus:

 * Import managers from ``polymorphic.managers`` (plural), not ``polymorphic.manager``.
 * Register child models to the admin as well using ``@admin.register()`` or
   ``admin.site.register()``, as this is no longer done automatically.

* Added Django 2.0 support.

Also backported into 1.3.1:

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
* Fix fieldsets handling in the admin (``declared_fieldsets`` is removed since Django 1.9)


v1.3.1 (2018-04-16)
-------------------

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
* Fix fieldsets handling in the admin (``declared_fieldsets`` is removed since Django 1.9)


v1.3.0 (2017-08-01)
-------------------

* **BACKWARDS INCOMPATIBILITY:** Dropped Django 1.4, 1.5, 1.6, 1.7, 1.9 and Python 2.6 support.
  Only official Django releases (1.8, 1.10, 1.11) are supported now.
* Allow expressions to pass unchanged in ``.order_by()``
* Fixed Django 1.11 accessor checks (to support subclasses of ``ForwardManyToOneDescriptor``, like
  ``ForwardOneToOneDescriptor``)
* Fixed polib syntax error messages in translations.


v1.2.0 (2017-05-01)
-------------------

* Django 1.11 support.
* Fixed ``PolymorphicInlineModelAdmin`` to explictly exclude ``polymorphic_ctype``.
* Fixed Python 3 TypeError in the admin when preserving the query string.
* Fixed Python 3 issue due to ``force_unicode()`` usage instead of ``force_text()``.
* Fixed ``z-index`` attribute for admin menu appearance.


v1.1.0 (2017-02-03)
-------------------

* Added class based formset views in ``polymorphic/contrib/extra_views``.
* Added helper function ``polymorphic.utils.reset_polymorphic_ctype()``.
  This eases the migration old existing models to polymorphic.
* Fixed Python 2.6 issue.
* Fixed Django 1.6 support.


v1.0.2 (2016-10-14)
-------------------

* Added helper function for django-guardian_; add
  ``GUARDIAN_GET_CONTENT_TYPE = 'polymorphic.contrib.guardian.get_polymorphic_base_content_type'``
  to the project settings to let guardian handles inherited models properly.
* Fixed ``polymorphic_modelformset_factory()`` usage.
* Fixed Python 3 bug for inline formsets.
* Fixed CSS for Grappelli, so model choice menu properly overlaps.
* Fixed ``ParentAdminNotRegistered`` exception for models that are registered via a proxy model
  instead of the real base model.


v1.0.1 (2016-09-11)
-------------------

* Fixed compatibility with manager changes in Django 1.10.1


v1.0.0 (2016-09-02)
-------------------

* Added Django 1.10 support.
* Added **admin inline** support for polymorphic models.
* Added **formset** support for polymorphic models.
* Added support for polymorphic queryset limiting effects on *proxy models*.
* Added support for multiple databases with the ``.using()`` method and ``using=..`` keyword
  argument.
* Fixed modifying passed ``Q()`` objects in place.

.. note::
   This version provides a new method for registering the admin models.
   While the old method is still supported, we recommend to upgrade your code.
   The new registration style improves the compatibility in the Django admin.

   * Register each ``PolymorphicChildModelAdmin`` with the admin site too.
   * The ``child_models`` attribute of the ``PolymorphicParentModelAdmin`` should be a flat list of
     all child models. The ``(model, admin)`` tuple is obsolete.

   Also note that proxy models will now limit the queryset too.


Fixed since 1.0b1 (2016-08-10)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* Fix formset empty-form display when there are form errors.
* Fix formset empty-form hiding for Grappelli_.
* Fixed packing ``admin/polymorphic/edit_inline/stacked.html`` in the wheel format.


v0.9.2 (2016-05-04)
-------------------

* Fix error when using ``date_hierarchy`` field in the admin
* Fixed Django 1.10 warning in admin add-type view.


v0.9.1 (2016-02-18)
-------------------

* Fixed support for ``PolymorphicManager.from_queryset()`` for custom query sets.
* Fixed Django 1.7 ``changeform_view()`` redirection to the child admin site. This fixes custom
  admin code that uses these views, such as django-reversion_'s ``revision_view()`` /
  ``recover_view()``.
* Fixed ``.only('pk')`` field support.
* Fixed ``object_history_template`` breadcrumb.
  **NOTE:** when using django-reversion_ / django-reversion-compare_, make sure to implement
  a ``admin/polymorphic/object_history.html`` template in your project that extends
  from ``reversion/object_history.html`` or ``reversion-compare/object_history.html`` respectively.


v0.9.0 (2016-02-17)
-------------------

* Added ``.only()`` and ``.defer()`` support.
* Added support for Django 1.8 complex expressions in ``.annotate()`` / ``.aggregate()``.
* Fix Django 1.9 handling of custom URLs.
  The new change-URL redirect overlapped any custom URLs defined in the child admin.
* Fix Django 1.9 support in the admin.
* Fix setting an extra custom manager without overriding the ``_default_manager``.
* Fix missing ``history_view()`` redirection to the child admin, which is important for
  django-reversion_ support. See the documentation for hints for
  :ref:`django-reversion-compare support <django-reversion-compare-support>`.


v0.8.1 (2015-12-29)
-------------------

* Fixed support for reverse relations for ``relname___field`` when the field starts with an ``_``
  character. Otherwise, the query will be interpreted as subclass lookup (``ClassName___field``).


v0.8.0 (2015-12-28)
-------------------

* Added Django 1.9 compatibility.
* Renamed ``polymorphic.manager`` => ``polymorphic.managers`` for consistentcy.
* **BACKWARDS INCOMPATIBILITY:** The import paths have changed to support Django 1.9.
  Instead of ``from polymorphic import X``,
  you'll have to import from the proper package. For example:

.. code-block:: python

    from polymorphic.models import PolymorphicModel
    from polymorphic.managers import PolymorphicManager, PolymorphicQuerySet
    from polymorphic.showfields import ShowFieldContent, ShowFieldType, ShowFieldTypeAndContent

* **BACKWARDS INCOMPATIBILITY:** Removed ``__version__.py`` in favor of a standard ``__version__``
  in ``polymorphic/__init__.py``.
* **BACKWARDS INCOMPATIBILITY:** Removed automatic proxying of method calls to the queryset class.
  Use the standard Django methods instead:

.. code-block:: python

    # In model code:
    objects = PolymorphicQuerySet.as_manager()

    # For manager code:
    MyCustomManager = PolymorphicManager.from_queryset(MyCustomQuerySet)



v0.7.2 (2015-10-01)
-------------------

* Added ``queryset.as_manager()`` support for Django 1.7/1.8
* Optimize model access for non-dumpdata usage; avoid ``__getattribute__()`` call each time to
  access the manager.
* Fixed 500 error when using invalid PK's in the admin URL, return 404 instead.
* Fixed possible issues when using an custom ``AdminSite`` class for the parent object.
* Fixed Pickle exception when polymorphic model is cached.


v0.7.1 (2015-04-30)
-------------------

* Fixed Django 1.8 support for related field widgets.


v0.7.0 (2015-04-08)
-------------------

* Added Django 1.8 support
* Added support for custom primary key defined using
  ``mybase_ptr = models.OneToOneField(BaseClass, parent_link=True, related_name="...")``.
* Fixed Python 3 issue in the admin
* Fixed ``_default_manager`` to be consistent with Django, it's now assigned directly instead of
  using ``add_to_class()``
* Fixed 500 error for admin URLs without a '/', e.g. ``admin/app/parentmodel/id``.
* Fixed preserved filter for Django admin in delete views
* Removed test noise for diamond inheritance problem (which Django 1.7 detects)


v0.6.1 (2014-12-30)
-------------------

* Remove Django 1.7 warnings
* Fix Django 1.4/1.5 queryset calls on related objects for unknown methods. The ``RelatedManager``
  code overrides ``get_query_set()`` while ``__getattr__()`` used the new-style ``get_queryset()``.
* Fix validate_model_fields(), caused errors when metaclass raises errors


v0.6.0 (2014-10-14)
-------------------

* Added Django 1.7 support.
* Added permission check for all child types.
* **BACKWARDS INCOMPATIBILITY:** the ``get_child_type_choices()`` method receives 2 arguments now
  (request, action). If you have overwritten this method in your code, make sure the method
  signature is updated accordingly.


v0.5.6 (2014-07-21)
-------------------

* Added ``pk_regex`` to the ``PolymorphicParentModelAdmin`` to support non-integer primary keys.
* Fixed passing ``?ct_id=`` to the add view for Django 1.6 (fixes compatibility with
  django-parler_).


v0.5.5 (2014-04-29)
-------------------

* Fixed ``get_real_instance_class()`` for proxy models (broke in 0.5.4).


v0.5.4 (2014-04-09)
-------------------

* Fix ``.non_polymorphic()`` to returns a clone of the queryset, instead of effecting the existing
  queryset.
* Fix missing ``alters_data = True`` annotations on the overwritten ``save()`` methods.
* Fix infinite recursion bug in the admin with Django 1.6+
* Added detection of bad ``ContentType`` table data.


v0.5.3 (2013-09-17)
-------------------

* Fix TypeError when ``base_form`` was not defined.
* Fix passing ``/admin/app/model/id/XYZ`` urls to the correct admin backend.
  There is no need to include a ``?ct_id=..`` field, as the ID already provides enough information.


v0.5.2 (2013-09-05)
-------------------

* Fix Grappelli_ breadcrumb support in the views.
* Fix unwanted ``___`` handling in the ORM when a field name starts with an underscore;
  this detects you meant ``relatedfield__ _underscorefield`` instead of ``ClassName___field``.
* Fix missing permission check in the "add type" view. This was caught however in the next step.
* Fix admin validation errors related to additional non-model form fields.


v0.5.1 (2013-07-05)
-------------------

* Add Django 1.6 support.
* Fix Grappelli_ theme support in the "Add type" view.


v0.5.0 (2013-04-20)
-------------------

* Add Python 3.2 and 3.3 support
* Fix errors with ContentType objects that don't refer to an existing model.


v0.4.2 (2013-04-10)
-------------------

* Used proper ``__version__`` marker.


v0.4.1 (2013-04-10)
-------------------

* Add Django 1.5 and 1.6 support
* Add proxy model support
* Add default admin ``list_filter`` for polymorphic model type.
* Fix queryset support of related objects.
* Performed an overall cleanup of the project
* **Deprecated** the ``queryset_class`` argument of the ``PolymorphicManager`` constructor, use the
  class attribute instead.
* **Dropped** Django 1.1, 1.2 and 1.3 support


v0.4.0 (2013-03-25)
-------------------

* Update example project for Django 1.4
* Added tox and Travis configuration


v0.3.1 (2013-02-28)
-------------------

* SQL optimization, avoid query in pre_save_polymorphic()


v0.3.0 (2013-02-28)
-------------------

Many changes to the codebase happened, but no new version was released to pypi for years.
0.3 contains fixes submitted by many contributors, huge thanks to everyone!

* Added a polymorphic admin interface.
* PEP8 and code cleanups by various authors


v0.2.0 (2011-04-27)
-------------------

The 0.2 release serves as legacy release.
It supports Django 1.1 up till 1.4 and Python 2.4 up till 2.7.

.. _Grappelli: http://grappelliproject.com/
.. _django-advanced-filters: https://github.com/modlinltd/django-advanced-filters
.. _django-extra-views: https://github.com/AndrewIngram/django-extra-views
.. _django-guardian: https://github.com/django-guardian/django-guardian
.. _django-parler: https://github.com/django-parler/django-parler
.. _django-reversion: https://github.com/etianen/django-reversion
.. _django-reversion-compare: https://github.com/jedie/django-reversion-compare


V1.0 Release Candidate 1 (2011-01-24)
-------------------------------------

* Fixed GitHub issue 15 (query result incomplete with inheritance).
  Thanks to John Debs for reporting and the test case.


Renaming, refactoring, new maintainer (2011-12-20)
--------------------------------------------------

Since the original author disappeared from the internet, we undertook to
maintain and upgrade this piece of software.

The latest "legacy" tag should be V1.0-RC-1. Anything above that should be
considered experimental and unstable until further notice (there be dragons).

New features, bug fixes and other improvements will be added to trunk from now on.


V1.0 Beta 2 (2010-11-11)
------------------------

Beta 2 accumulated somewhat more changes than intended, and also
has been delayed by DBMS benchmark testing I wanted to do on model
inheritance. These benchmarks show that there are considerable
problems with concrete model inheritance and contemporary DBM systems.
The results will be forthcoming on the google discussion forum.

Please also see: http://www.jacobian.org/writing/concrete-inheritance/

The API should be stable now with Beta 2, so it's just about potential
bugfixes from now on regarding V1.0.

Beta 2 is still intended for testing and development environments and not
for production. No complaints have been heard regarding Beta 1 however,
and Beta 1 is used on a few production sites by some enterprising users.

There will be a release candidate for V1.0 in the very near future.

New Features and changes
~~~~~~~~~~~~~~~~~~~~~~~~

*   API CHANGE: ``.extra()`` has been re-implemented. Now it's polymorphic by
    default and works (nearly) without restrictions (please see docs). This is a (very)
    incompatible API change regarding previous versions of django_polymorphic.
    Support for the ``polymorphic`` keyword parameter has been removed.
    You can get back the non-polymorphic behaviour by using
    ``ModelA.objects.non_polymorphic().extra(...)``.

*   API CHANGE: ``ShowFieldContent`` and ``ShowFieldTypeAndContent`` now
    use a slightly different output format. If this causes too much trouble for
    your test cases, you can get the old behaviour back (mostly) by adding
    ``polymorphic_showfield_old_format = True`` to your model definitions.
    ``ShowField...`` now also produces more informative output for custom
    primary keys.

*   ``.non_polymorphic()`` queryset member function added. This is preferable to
    using ``.base_objects...``, as it just makes the resulting queryset non-polymorphic
    and does not change anything else in the behaviour of the manager used (while
    ``.base_objects`` is just a different manager).

*   ``.get_real_instances()``: implementation modified to allow the following
    more simple and intuitive use::

    >>> qs = ModelA.objects.all().non_polymorphic()
    >>> qs.get_real_instances()

    which is equivalent to::

    >>> ModelA.objects.all()

*   added member function:
    ``normal_q_object = ModelA.translate_polymorphic_Q_object(enhanced_q_object)``

*   misc changes/improvements

Bugfixes
~~~~~~~~

*   Custom fields could cause problems when used as the primary key.
    In inherited models, Django's automatic ".pk" field does not always work
    correctly for such custom fields: "some_object.pk" and "some_object.id"
    return different results (which they shouldn't, as pk should always be just
    an alias for the primary key field). It's unclear yet if the problem lies in
    Django or the affected custom fields. Regardless, the problem resulting
    from this has been fixed with a small workaround.
    "python manage.py test polymorphic" also tests and reports on this problem now.
    Thanks to Mathieu Steele for reporting and the test case.

V1.0 Beta 1 (2010-10-18)
------------------------

This release is mostly a cleanup and maintenance release that also
improves a number of minor things and fixes one (non-critical) bug.

Some pending API changes and corrections have been folded into this release
in order to make the upcoming V1.0 API as stable as possible.

This release is also about getting feedback from you in case you don't
approve of any of these changes or would like to get additional
API fixes into V1.0.

The release contains a considerable amount of changes in some of the more
critical parts of the software. It's intended for testing and development
environments and not for production environments. For these, it's best to
wait a few weeks for the proper V1.0 release, to allow some time for any
potential problems to show up (if they exist).

If you encounter any such problems, please post them in the discussion group
or open an issue on GitHub or BitBucket (or send me an email).

There also have been a number of minor API changes.
Please see the README for more information.

New Features
~~~~~~~~~~~~

*   official Django 1.3 alpha compatibility

*   ``PolymorphicModel.__getattribute__`` hack removed.
    This improves performance considerably as python's __getattribute__
    generally causes a pretty large processing overhead. It's gone now.

*   the ``polymorphic_dumpdata`` management command is not needed anymore
    and has been disabled, as the regular Django dumpdata command now automatically
    works correctly with polymorphic models (for all supported versions of Django).

*   ``.get_real_instances()`` has been elevated to an official part of the API::

        real_objects = ModelA.objects.get_real_instances(base_objects_list_or_queryset)

    allows you to turn a queryset or list of base objects into a list of the real instances.
    This is useful if e.g. you use ``ModelA.base_objects.extra(...)`` and then want to
    transform the result to its polymorphic equivalent.

*   ``translate_polymorphic_Q_object``  (see DOCS)

*   improved testing

*   Changelog added: CHANGES.rst/html

Bugfixes
~~~~~~~~

*   Removed requirement for primary key to be an IntegerField.
    Thanks to Mathieu Steele and Malthe Borch.

API Changes
~~~~~~~~~~~

**polymorphic_dumpdata**

The management command ``polymorphic_dumpdata`` is not needed anymore
and has been disabled, as the regular Django dumpdata command now automatically
works correctly with polymorphic models (for all supported versions of Django).

**Output of Queryset or Object Printing**

In order to improve compatibility with vanilla Django, printing quersets
(__repr__ and __unicode__) does not use django_polymorphic's pretty printing
by default anymore. To get the old behaviour when printing querysets,
you need to replace your model definition:

>>> class Project(PolymorphicModel):

by:

>>> class Project(PolymorphicModel, ShowFieldType):

The mixin classes for pretty output have been renamed:

    ``ShowFieldTypes, ShowFields, ShowFieldsAndTypes``

are now:

    ``ShowFieldType, ShowFieldContent and ShowFieldTypeAndContent``

(the old ones still exist for compatibility)

**Running the Test suite with Django 1.3**

Django 1.3 requires ``python manage.py test polymorphic`` instead of
just ``python manage.py test``.


Beta Release (2010-2-22)
------------------------

IMPORTANT: API Changed (import path changed), and Installation Note

The django_polymorphic source code has been restructured
and as a result needs to be installed like a normal Django App
- either via copying the "polymorphic" directory into your
Django project or by running setup.py. Adding 'polymorphic'
to INSTALLED_APPS in settings.py is still optional, however.

The file `polymorphic.py` cannot be used as a standalone
extension module anymore, as is has been split into a number
of smaller files.

Importing works slightly different now: All relevant symbols are
imported directly from 'polymorphic' instead from
'polymorphic.models'::

    # new way
    from polymorphic import PolymorphicModel, ...

    # old way, doesn't work anymore
    from polymorphic.models import PolymorphicModel, ...

+ minor API addition: 'from polymorphic import VERSION, get_version'

New Features
~~~~~~~~~~~~

Python 2.4 compatibility, contributed by Charles Leifer. Thanks!

Bugfixes
~~~~~~~~

Fix: The exception "...has no attribute 'sub_and_superclass_dict'"
could be raised. (This occurred if a subclass defined __init__
and accessed class members before calling the superclass __init__).
Thanks to Mattias Brändström.

Fix: There could be name conflicts if
field_name == model_name.lower() or similar.
Now it is possible to give a field the same name as the class
(like with normal Django models).
(Found through the example provided by Mattias Brändström)


Beta Release (2010-2-4)
-----------------------

New features (and documentation)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

queryset order_by method added

queryset aggregate() and extra() methods implemented

queryset annotate() method implemented

queryset values(), values_list(), distinct() documented; defer(),
only() allowed (but not yet supported)

setup.py added. Thanks to Andrew Ingram.

More about these additions in the docs:
http://bserve.webhop.org/wiki/django_polymorphic/doc

Bugfixes
~~~~~~~~

*   fix remaining potential accessor name clashes (but this only works
    with Django 1.2+, for 1.1 no changes). Thanks to Andrew Ingram.

*   fix use of 'id' model field, replaced with 'pk'.

*   fix select_related bug for objects from derived classes (till now
    sel.-r. was just ignored)

"Restrictions & Caveats" updated
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

*   Django 1.1 only - the names of polymorphic models must be unique
    in the whole project, even if they are in two different apps.
    This results from a restriction in the Django 1.1 "related_name"
    option (fixed in Django 1.2).

*   Django 1.1 only - when ContentType is used in models, Django's
    seralisation or fixtures cannot be used. This issue seems to be
    resolved for Django 1.2 (changeset 11863: Fixed #7052, Added
    support for natural keys in serialization).


Beta Release (2010-1-30)
------------------------

Fixed ContentType related field accessor clash (an error emitted
by model validation) by adding related_name to the ContentType
ForeignKey. This happened if your polymorphc model used a ContentType
ForeignKey. Thanks to Andrew Ingram.


Beta Release (2010-1-29)
------------------------

Restructured django_polymorphic into a regular Django add-on
application. This is needed for the management commands, and
also seems to be a generally good idea for future enhancements
as well (and it makes sure the tests are always included).

The ``poly`` app - until now being used for test purposes only
- has been renamed to ``polymorphic``. See DOCS.rst
("installation/testing") for more info.


Beta Release (2010-1-28)
------------------------

Added the polymorphic_dumpdata management command (github issue 4),
for creating fixtures, this should be used instead of
the normal Django dumpdata command.
Thanks to Charles Leifer.

Important: Using ContentType together with dumpdata generally
needs Django 1.2 (important as any polymorphic model uses
ContentType).

Beta Release (2010-1-26)
------------------------

IMPORTANT - database schema change (more info in change log).
I hope I got this change in early enough before anyone started
to use polymorphic.py in earnest. Sorry for any inconvenience.
This should be the final DB schema now.

Django's ContentType is now used instead of app-label and model-name
This is a cleaner and more efficient solution
Thanks to Ilya Semenov for the suggestion.

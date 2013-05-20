Changelog
==========

Version 0.5 (dev)
--------------------------

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

Contributing
============

You can contribute to *django-polymorphic* to forking the code on GitHub:

  https://github.com/django-polymorphic/django-polymorphic


Running tests
-------------

We require features to be backed by a unit test.
This way, we can test *django-polymorphic* against new Django versions.
To run the included test suite, execute::

    ./runtests.py

To test support for multiple Python and Django versions, run tox from the repository root::

    pip install tox
    tox

The Python versions need to be installed at your system.
On Linux, download the versions at http://www.python.org/download/releases/.
On MacOS X, use Homebrew_ to install other Python versions.

We currently support Python 2.6, 2.7, 3.2 and 3.3.


Example project
----------------

The repository contains a complete Django project that may be used for tests or experiments,
without any installation needed.

The management command ``pcmd.py`` in the app ``pexp`` can be used for quick tests
or experiments - modify this file (pexp/management/commands/pcmd.py) to your liking.


Supported Django versions
-------------------------

The current release should be usable with the supported releases of Django;
the current stable release and the previous release. Supporting older Django
versions is a nice-to-have feature, but not mandatory.

In case you need to use *django-polymorphic* with older Django versions,
consider installing a previous version.

.. _Homebrew: http://mxcl.github.io/homebrew/

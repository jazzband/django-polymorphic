# django-polymorphic

[![License: BSD](https://img.shields.io/badge/License-BSD-blue.svg)](https://opensource.org/license/bsd-3-clause)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![PyPI version](https://badge.fury.io/py/django-polymorphic.svg)](https://pypi.python.org/pypi/django-polymorphic/)
[![PyPI pyversions](https://img.shields.io/pypi/pyversions/django-polymorphic.svg)](https://pypi.python.org/pypi/django-polymorphic/)
[![PyPI djversions](https://img.shields.io/pypi/djversions/django-polymorphic.svg)](https://pypi.org/project/django-polymorphic/)
[![PyPI status](https://img.shields.io/pypi/status/django-polymorphic.svg)](https://pypi.python.org/pypi/django-polymorphic)
[![Documentation Status](https://readthedocs.org/projects/django-polymorphic/badge/?version=latest)](http://django-polymorphic.readthedocs.io/?badge=latest/)
[![Code Cov](https://img.shields.io/codecov/c/github/jazzband/django-polymorphic/master.svg)](https://codecov.io/github/jazzband/django-polymorphic?branch=master)
[![Test Status](https://github.com/jazzband/django-polymorphic/actions/workflows/test.yml/badge.svg?branch=master)](https://github.com/jazzband/django-polymorphic/actions/workflows/test.yml?query=branch:master)
[![Lint Status](https://github.com/jazzband/django-polymorphic/actions/workflows/lint.yml/badge.svg?branch=master)](https://github.com/jazzband/django-polymorphic/actions/workflows/lint.yml?query=branch:master)
[![Published on Django Packages](https://img.shields.io/badge/Published%20on-Django%20Packages-0c3c26)](https://djangopackages.org/packages/p/django-polymorphic/)
[![Jazzband](https://jazzband.co/static/img/badge.svg)](https://jazzband.co/)

---------------------------------------------------------------------------------------------------

[![Postgres](https://img.shields.io/badge/Postgres-12%2B-blue)](https://www.postgresql.org/)
[![MySQL](https://img.shields.io/badge/MySQL-8.0%2B-blue)](https://www.mysql.com/)
[![MariaDB](https://img.shields.io/badge/MariaDB-10.4%2B-blue)](https://mariadb.org/)
[![SQLite](https://img.shields.io/badge/SQLite-3.8%2B-blue)](https://www.sqlite.org/)
[![Oracle](https://img.shields.io/badge/Oracle-21c%2B-blue)](https://www.oracle.com/database/)

---------------------------------------------------------------------------------------------------

## Polymorphic Models for Django

[django-polymorphic](https://pypi.python.org/pypi/django-polymorphic) simplifies using inherited models in [Django](https://djangoproject.com) projects. When a query is made at the base model, the inherited model classes are returned.

When we store models that inherit from a ``Project`` model...

```python

    >>> Project.objects.create(topic="Department Party")
    >>> ArtProject.objects.create(topic="Painting with Tim", artist="T. Turner")
    >>> ResearchProject.objects.create(topic="Swallow Aerodynamics", supervisor="Dr. Winter")
```

...and want to retrieve all our projects, the subclassed models are returned!

```python

    >>> Project.objects.all()
    [ <Project:         id 1, topic "Department Party">,
      <ArtProject:      id 2, topic "Painting with Tim", artist "T. Turner">,
      <ResearchProject: id 3, topic "Swallow Aerodynamics", supervisor "Dr. Winter"> ]
```

Using vanilla Django, we get the base class objects, which is rarely what we wanted:

```python

    >>> Project.objects.all()
    [ <Project: id 1, topic "Department Party">,
      <Project: id 2, topic "Painting with Tim">,
      <Project: id 3, topic "Swallow Aerodynamics"> ]
```

This also works when the polymorphic model is accessed via
ForeignKeys, ManyToManyFields or OneToOneFields.

### Features

* Full admin integration.
* ORM integration:

  * support for ForeignKey, ManyToManyField, OneToOneField descriptors.
  * Filtering/ordering of inherited models (``ArtProject___artist``).
  * Filtering model types: ``instance_of(...)`` and ``not_instance_of(...)``
  * Combining querysets of different models (``qs3 = qs1 | qs2``)
  * Support for custom user-defined managers.
* Uses the minimum amount of queries needed to fetch the inherited models.
* Disabling polymorphic behavior when needed.


**Note:** While [django-polymorphic](https://pypi.python.org/pypi/django-polymorphic) makes subclassed models easy to use in Django, we still encourage to use them with caution. Each subclassed model will require Django to perform an ``INNER JOIN`` to fetch the model fields from the database. While taking this in mind, there are valid reasons for using subclassed models. That's what this library is designed for!

For more information, see the [documentation at Read the Docs](https://django-polymorphic.readthedocs.io).

### Installation

```bash
    $ pip install django-polymorphic
```

```python
INSTALLED_APPS = [
  ...
  "django.contrib.contenttypes",  # we rely on the contenttypes framework
  "polymorphic"
]
```

## License

[django-polymorphic](https://pypi.python.org/pypi/django-polymorphic) uses the same license as Django (BSD-like).

.. _performance:

Performance Considerations
==========================

Usually, when Django users create their own polymorphic ad-hoc solution
without a tool like *django-polymorphic*, this usually results in a variation of ::

    result_objects = [ o.get_real_instance() for o in BaseModel.objects.filter(...) ]

which has very bad performance, as it introduces one additional
SQL query for every object in the result which is not of class ``BaseModel``.
Compared to these solutions, *django-polymorphic* has the advantage
that it only needs 1 SQL query *per object type*, and not *per object*.

The current implementation does not use any custom SQL or Django DB layer
internals - it is purely based on the standard Django ORM. Specifically, the query::

    result_objects = list( ModelA.objects.filter(...) )

performs one SQL query to retrieve ``ModelA`` objects and one additional
query for each unique derived class occurring in result_objects.
The best case for retrieving 100 objects is 1 SQL query if all are
class ``ModelA``. If 50 objects are ``ModelA`` and 50 are ``ModelB``, then
two queries are executed. The pathological worst case is 101 db queries if
result_objects contains 100 different object types (with all of them
subclasses of ``ModelA``).

ContentType retrieval
---------------------

When fetching the :class:`~django.contrib.contenttypes.models.ContentType` class,
it's tempting to read the ``object.polymorphic_ctype`` field directly.
However, this performs an additional query via the :class:`~django.db.models.ForeignKey` object
to fetch the :class:`~django.contrib.contenttypes.models.ContentType`.
Instead, use:

.. code-block:: python

    from django.contrib.contenttypes.models import ContentType

    ctype = ContentType.objects.get_for_id(object.polymorphic_ctype_id)

This uses the :meth:`~django.contrib.contenttypes.models.ContentTypeManager.get_for_id` function
which caches the results internally.

Database notes
--------------

Current relational DBM systems seem to have general problems with
the SQL queries produced by object relational mappers like the Django
ORM, if these use multi-table inheritance like Django's ORM does.
The "inner joins" in these queries can perform very badly.
This is independent of django_polymorphic and affects all uses of
multi table Model inheritance.

Please also see this `post (and comments) from Jacob Kaplan-Moss
<http://www.jacobian.org/writing/concrete-inheritance/>`_.

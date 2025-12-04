.. _performance:

Performance Considerations
==========================

Usually, when Django users create their own polymorphic ad-hoc solution without a tool like
:pypi:`django-polymorphic`, this usually results in a variation of:

.. code-block:: python

    result_objects = [ o.get_real_instance() for o in BaseModel.objects.filter(...) ]

which has very bad performance, as it introduces one additional SQL query for every object in the
result which is not of class ``BaseModel``. Compared to these solutions, :pypi:`django-polymorphic`
has the advantage that it only needs 1 SQL query *per object type*, and not *per object*.

The current implementation does not use any custom SQL or Django DB layer internals - it is purely
based on the standard Django ORM. Specifically, the query:

.. code-block:: python

    result_objects = list( ModelA.objects.filter(...) )

performs one SQL query to retrieve ``ModelA`` objects and one additional query for each unique
derived class occurring in result_objects. The best case for retrieving 100 objects is 1 SQL query
if all are class ``ModelA``. If 50 objects are ``ModelA`` and 50 are ``ModelB``, then two queries
are executed. The pathological worst case is 101 db queries if result_objects contains 100 different
object types (with all of them subclasses of ``ModelA``).

Iteration: Memory vs DB Round Trips
-----------------------------------

When iterating over large QuerySets, there is a trade-off between memory consumption and number
of round trips to the database. One additional query is needed per model subclass present in the
QuerySet and these queries take the form of ``SELECT ... WHERE pk IN (....)`` with a potentially
large number of IDs in the IN clause. All models in the IN clause will be loaded into memory during
iteration.

To balance this trade-off, by default a maximum of 2000 objects are requested at once. This means
that if your QuerySet contains 10,000 objects of 3 different subclasses, then 16 queries will be
executed: 1 to fetch the base objects, and 5 (10/2 == 5) * 3 more to fetch the subclasses.

The `chunk_size` parameter on :meth:`~django.db.models.query.QuerySet.iterator` can be used to
change the number of objects loaded into memory at once during iteration. For example, to load 5000 objects at once:

.. code-block:: python

    for obj in ModelA.objects.all().iterator(chunk_size=5000):
        process(obj)

.. note::

    ``chunk_size`` on non-polymorphic QuerySets controls the number of rows fetched from the
    database at once, but for polymorphic QuerySets the behavior is more analogous to its behavior
    when :meth:`~django.db.models.query.QuerySet.prefetch_related` is used.

Some database backends limit the number of parameters in a query. For those backends the
``chunk_size`` will be restricted to be no greater than that limit. This limit can be checked in:

.. code-block:: python

    from django.db import connection

    print(connection.features.max_query_params)


You may change the global default fallback ``chunk_size`` by modifying the
:attr:`polymorphic.query.Polymorphic_QuerySet_objects_per_request` attribute. Place code like
this somewhere that will be executed during startup:

.. code-block:: python

    from polymorphic import query

    query.Polymorphic_QuerySet_objects_per_request = 5000


:class:`~django.contrib.contenttypes.models.ContentType` retrieval
------------------------------------------------------------------

When fetching the :class:`~django.contrib.contenttypes.models.ContentType` class, it's tempting to
read the :attr:`~polymorphic.models.PolymorphicModel.polymorphic_ctype` field directly. However,
this performs an additional query via the :class:`~django.db.models.ForeignKey` object to fetch the
:class:`~django.contrib.contenttypes.models.ContentType`. Instead, use:

.. code-block:: python

    from django.contrib.contenttypes.models import ContentType

    ctype = ContentType.objects.get_for_id(object.polymorphic_ctype_id)

This uses the :meth:`~django.contrib.contenttypes.models.ContentTypeManager.get_for_id` function
which caches the results internally.

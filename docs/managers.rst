Managers & Querysets
====================

Using a Custom Manager
----------------------

A nice feature of Django is the possibility to define one's own custom object managers.
This is fully supported with :pypi:`django-polymorphic`. For creating a custom polymorphic
manager class, just derive your manager from :class:`~polymorphic.managers.PolymorphicManager`
instead of :class:`~django.db.models.Manager`. As with vanilla Django, in your model class, you
should explicitly add the default manager first, and then your custom manager:

.. code-block:: python

    from polymorphic.models import PolymorphicModel
    from polymorphic.managers import PolymorphicManager

    class TimeOrderedManager(PolymorphicManager):
        def get_queryset(self):
            qs = super(TimeOrderedManager,self).get_queryset()
            return qs.order_by('-start_date')

        def most_recent(self):
            qs = self.get_queryset()  # get my ordered queryset
            return qs[:10]            # limit => get ten most recent entries

    class Project(PolymorphicModel):
        objects = PolymorphicManager()          # add the default polymorphic manager first
        objects_ordered = TimeOrderedManager()  # then add your own manager
        start_date = DateTimeField()            # project start is this date/time

The first manager defined (:attr:`~django.db.models.Model.objects` in the example) is used by Django
as automatic manager for several purposes, including accessing related objects. It must not filter
objects and it's safest to use the plain :class:`~polymorphic.managers.PolymorphicManager` here.

Manager Inheritance
-------------------

Polymorphic models inherit/propagate all managers from their base models, as long as these are
polymorphic. This means that all managers defined in polymorphic base models continue to work as
expected in models inheriting from this base model:

.. code-block:: python

    from polymorphic.models import PolymorphicModel
    from polymorphic.managers import PolymorphicManager

    class TimeOrderedManager(PolymorphicManager):
        def get_queryset(self):
            qs = super(TimeOrderedManager,self).get_queryset()
            return qs.order_by('-start_date')

        def most_recent(self):
            qs = self.get_queryset()  # get my ordered queryset
            return qs[:10]            # limit => get ten most recent entries

    class Project(PolymorphicModel):
        objects = PolymorphicManager()          # add the default polymorphic manager first
        objects_ordered = TimeOrderedManager()  # then add your own manager
        start_date = DateTimeField()            # project start is this date/time

    class ArtProject(Project):  # inherit from Project, inheriting its fields and managers
        artist = models.CharField(max_length=30)

ArtProject inherited the managers ``objects`` and ``objects_ordered`` from Project.

``ArtProject.objects_ordered.all()`` will return all art projects ordered regarding their start time
and ``ArtProject.objects_ordered.most_recent()`` will return the ten most recent art projects.

Using a Custom Queryset Class
-----------------------------

The :class:`~polymorphic.managers.PolymorphicManager` class accepts one initialization argument,
which is the queryset class the manager should use. Just as with vanilla Django, you may define your
own custom queryset classes. Just use :class:`~polymorphic.managers.PolymorphicQuerySet` instead of
Django's :class:`~django.db.models.query.QuerySet` as the base class:

.. code-block:: python

        from polymorphic.models import PolymorphicModel
        from polymorphic.managers import PolymorphicManager
        from polymorphic.query import PolymorphicQuerySet

        class MyQuerySet(PolymorphicQuerySet):
            def my_queryset_method(self):
                ...

        class MyModel(PolymorphicModel):
            my_objects = PolymorphicManager.from_queryset(MyQuerySet)()
            ...

If you do not wish to extend from a custom :class:`~polymorphic.managers.PolymorphicManager` you
may also prefer the :meth:`~polymorphic.managers.PolymorphicQuerySet.as_manager`
shortcut:

.. code-block:: python

    from polymorphic.models import PolymorphicModel
    from polymorphic.query import PolymorphicQuerySet

    class MyQuerySet(PolymorphicQuerySet):
        def my_queryset_method(self):
            ...

    class MyModel(PolymorphicModel):
        my_objects = MyQuerySet.as_manager()
        ...

For further discussion see `this topic on the Q&A page
<https://github.com/jazzband/django-polymorphic/discussions/696#discussioncomment-15223661>`_.


Natural Key Serialization
-------------------------

When using Django's natural key serialization with :django-admin:`dumpdata` and 
:django-admin:`loaddata`, polymorphic models require special handling.

.. important::

    Always use :meth:`~polymorphic.managers.PolymorphicQuerySet.non_polymorphic` in 
    ``get_by_natural_key()`` for polymorphic models. Without this, deserialization fails 
    when loading new objects because polymorphic queries try to fetch incomplete objects.

Example implementation:

.. code-block:: python

    from polymorphic.models import PolymorphicModel
    from polymorphic.managers import PolymorphicManager

    class ArticleManager(PolymorphicManager):
        def get_by_natural_key(self, slug):
            return self.non_polymorphic().get(slug=slug)

    class Article(PolymorphicModel):
        slug = models.SlugField(unique=True)
        title = models.CharField(max_length=200)
        objects = ArticleManager()
        
        def natural_key(self):
            return (self.slug,)

    class BlogPost(Article):
        author = models.CharField(max_length=100)

Usage:

.. code-block:: bash

    # Dump with natural keys
    $ python manage.py dumpdata myapp --natural-primary --natural-foreign > fixtures.json
    
    # Load into another database
    $ python manage.py loaddata fixtures.json

.. note::

    * Child models inherit ``natural_key()`` from the parent - no need to override
    * Always use both ``--natural-primary`` and ``--natural-foreign`` flags with polymorphic models
    * See `issue #517 <https://github.com/jazzband/django-polymorphic/issues/517>`_ for details
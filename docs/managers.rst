Custom Managers, Querysets & Manager Inheritance
================================================

Using a Custom Manager
----------------------

A nice feature of Django is the possibility to define one's own custom object managers.
This is fully supported with django_polymorphic: For creating a custom polymorphic
manager class, just derive your manager from ``PolymorphicManager`` instead of
``models.Manager``. As with vanilla Django, in your model class, you should
explicitly add the default manager first, and then your custom manager::

    from polymorphic.models import PolymorphicModel
    from polymorphic.manager import PolymorphicManager

    class TimeOrderedManager(PolymorphicManager):
        def get_queryset(self):
            qs = super(TimeOrderedManager,self).get_queryset()
            return qs.order_by('-start_date')        # order the queryset

        def most_recent(self):
            qs = self.get_queryset()                 # get my ordered queryset
            return qs[:10]                           # limit => get ten most recent entries

    class Project(PolymorphicModel):
        objects = PolymorphicManager()               # add the default polymorphic manager first
        objects_ordered = TimeOrderedManager()       # then add your own manager
        start_date = DateTimeField()                 # project start is this date/time

The first manager defined ('objects' in the example) is used by
Django as automatic manager for several purposes, including accessing
related objects. It must not filter objects and it's safest to use
the plain ``PolymorphicManager`` here.

Manager Inheritance
-------------------

Polymorphic models inherit/propagate all managers from their
base models, as long as these are polymorphic. This means that all
managers defined in polymorphic base models continue to work as
expected in models inheriting from this base model::

    from polymorphic.models import PolymorphicModel
    from polymorphic.manager import PolymorphicManager

    class TimeOrderedManager(PolymorphicManager):
        def get_queryset(self):
            qs = super(TimeOrderedManager,self).get_queryset()
            return qs.order_by('-start_date')        # order the queryset

        def most_recent(self):
            qs = self.get_queryset()                 # get my ordered queryset
            return qs[:10]                           # limit => get ten most recent entries

    class Project(PolymorphicModel):
        objects = PolymorphicManager()               # add the default polymorphic manager first
        objects_ordered = TimeOrderedManager()       # then add your own manager
        start_date = DateTimeField()                 # project start is this date/time

    class ArtProject(Project):                       # inherit from Project, inheriting its fields and managers
        artist = models.CharField(max_length=30)

ArtProject inherited the managers ``objects`` and ``objects_ordered`` from Project.

``ArtProject.objects_ordered.all()`` will return all art projects ordered
regarding their start time and ``ArtProject.objects_ordered.most_recent()``
will return the ten most recent art projects.
.

Using a Custom Queryset Class
-----------------------------

The ``PolymorphicManager`` class accepts one initialization argument,
which is the queryset class the manager should use. Just as with vanilla Django,
you may define your own custom queryset classes. Just use PolymorphicQuerySet
instead of Django's QuerySet as the base class::

        from polymorphic.models import PolymorphicModel
        from polymorphic.manager import PolymorphicManager
        from polymorphic.query import PolymorphicQuerySet

        class MyQuerySet(PolymorphicQuerySet):
            def my_queryset_method(...):
                ...

        class MyModel(PolymorphicModel):
            my_objects=PolymorphicManager(MyQuerySet)
            ...

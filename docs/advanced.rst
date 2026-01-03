.. _advanced-features:

Advanced Features
=================

In the examples below, these models are being used:

.. code-block:: python

    from django.db import models
    from polymorphic.models import PolymorphicModel

    class ModelA(PolymorphicModel):
        field1 = models.CharField(max_length=10)

    class ModelB(ModelA):
        field2 = models.CharField(max_length=10)

    class ModelC(ModelB):
        field3 = models.CharField(max_length=10)


Filtering for classes (equivalent to python's :func:`isinstance`):
------------------------------------------------------------------

.. code-block:: python

    >>> ModelA.objects.instance_of(ModelB)
    [ <ModelB: id 2, field1 (CharField), field2 (CharField)>,
      <ModelC: id 3, field1 (CharField), field2 (CharField), field3 (CharField)> ]

In general, including or excluding parts of the inheritance tree:

.. code-block:: python

    ModelA.objects.instance_of(ModelB [, ModelC ...])
    ModelA.objects.not_instance_of(ModelB [, ModelC ...])

You can also use this feature in Q-objects (with the same result as above):

.. code-block:: python

    >>> ModelA.objects.filter( Q(instance_of=ModelB) )


Polymorphic filtering (for fields in inherited classes)
-------------------------------------------------------

For example, cherry-picking objects from multiple derived classes anywhere in the inheritance tree,
using Q objects (with the syntax: ``exact model name + three _ + field name``):

.. code-block:: python

    >>> ModelA.objects.filter(  Q(ModelB___field2 = 'B2') | Q(ModelC___field3 = 'C3')  )
    [ <ModelB: id 2, field1 (CharField), field2 (CharField)>,
      <ModelC: id 3, field1 (CharField), field2 (CharField), field3 (CharField)> ]


Combining Querysets
-------------------

Querysets could now be regarded as object containers that allow the
aggregation of different object types, very similar to python
lists - as long as the objects are accessed through the manager of
a common base class:

.. code-block:: python

    >>> Base.objects.instance_of(ModelX) | Base.objects.instance_of(ModelY)

    [ <ModelX: id 1, field_x (CharField)>,
      <ModelY: id 2, field_y (CharField)> ]


ManyToManyField, ForeignKey, OneToOneField
------------------------------------------

Relationship fields referring to polymorphic models work as
expected: like polymorphic querysets they now always return the
referred objects with the same type/class these were created and
saved as.

E.g., if in your model you define:

.. code-block:: python

    field1 = OneToOneField(ModelA)

then field1 may now also refer to objects of type ``ModelB`` or ``ModelC``.

A :class:`~django.db.models.ManyToManyField` example:

.. code-block:: python

    # The model holding the relation may be any kind of model, polymorphic or not
    class RelatingModel(models.Model):
    
        # ManyToMany relation to a polymorphic model
        many2many = models.ManyToManyField('ModelA')

    >>> o=RelatingModel.objects.create()
    >>> o.many2many.add(ModelA.objects.get(id=1))
    >>> o.many2many.add(ModelB.objects.get(id=2))
    >>> o.many2many.add(ModelC.objects.get(id=3))

    >>> o.many2many.all()
    [ <ModelA: id 1, field1 (CharField)>,
      <ModelB: id 2, field1 (CharField), field2 (CharField)>,
      <ModelC: id 3, field1 (CharField), field2 (CharField), field3 (CharField)> ]

Copying Polymorphic objects
---------------------------

**Copying polymorphic models is no different than copying regular multi-table models.** You have
two options:

1. Use :meth:`~django.db.models.query.QuerySet.create` and provide all field values from the
   original instance except the primary key(s).
2. Set the primary key attribute, and parent table pointers at all levels of inheritance to ``None``
   and call :meth:`~django.db.models.Model.save`.

The Django documentation :ref:`offers some discussion on copying <topics/db/queries:copying model instances>`,
including the complexity around related fields and multi-table inheritance.
:pypi:`django-polymorphic` offers a utility function :func:`~polymorphic.utils.prepare_for_copy`
that resets all necessary fields on a model instance to prepare it for copying:

    from polymorphic.utils import prepare_for_copy

    obj = ModelB.objects.first()
    prepare_for_copy(obj)
    obj.save()
    # obj is now a copy of the original ModelB instance


Working with Signals and Fixtures
----------------------------------

When using Django's :django-admin:`loaddata` command with polymorphic models, you may notice that
``post_save`` signal handlers receive instances that appear incomplete - parent class attributes
may be empty and ``pk``/``id`` fields may not match. **This is expected Django behavior** for
multi-table inheritance during deserialization, not a bug in :pypi:`django-polymorphic`.

Understanding the Issue
~~~~~~~~~~~~~~~~~~~~~~~~

During fixture loading, Django deserializes parent and child table rows separately. When a child
model's ``post_save`` signal fires, Django passes a ``raw=True`` parameter to indicate the data
is being loaded from a fixture. At this point, parent attributes may not yet be fully accessible.

For example, with this model hierarchy:

.. code-block:: python

    class Endpoint(PolymorphicModel):
        id = models.UUIDField(primary_key=True, default=uuid.uuid4)
        name = models.CharField(max_length=250)

    class Switch(Endpoint):
        ip_address = models.GenericIPAddressField()

    @receiver(post_save, sender=Switch)
    def switch_saved(sender, instance, created, **kwargs):
        # During loaddata: instance.name may be empty!
        print(f"Switch: {instance.name}")

During ``loaddata``, the signal may fire before ``instance.name`` is populated, even though the
fixture contains the correct data.

Recommended Solution: Check for raw=True
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The standard Django pattern is to check the ``raw`` parameter and skip custom logic during
fixture loading:

.. code-block:: python

    from django.db.models.signals import post_save
    from django.dispatch import receiver

    @receiver(post_save, sender=Switch)
    def switch_saved(sender, instance, created, raw, **kwargs):
        # Skip signal logic during fixture loading
        if raw:
            return
        
        if created:
            # This logic only runs during normal saves, not loaddata
            print(f"New switch created: {instance.name}")
            setup_monitoring(instance)

This is the recommended approach in Django's documentation and prevents issues with incomplete
data during deserialization.

Alternative: Use post_migrate Signal
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If you need to perform setup tasks after loading fixtures, use the ``post_migrate`` signal instead:

.. code-block:: python

    from django.db.models.signals import post_migrate
    from django.dispatch import receiver

    @receiver(post_migrate)
    def setup_switches(sender, **kwargs):
        """Run after migrations and fixtures are loaded"""
        from myapp.models import Switch
        
        for switch in Switch.objects.filter(monitoring_configured=False):
            # Now all attributes are fully loaded
            setup_monitoring(switch)
            switch.monitoring_configured = True
            switch.save()

Best Practices for Fixtures
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

When working with fixtures and polymorphic models:

1. **Always use natural keys** when creating fixtures with :django-admin:`dumpdata`:

   .. code-block:: bash

       python manage.py dumpdata myapp --natural-foreign --natural-primary > fixture.json

   This ensures ``polymorphic_ctype`` references are portable across databases.

2. **Check for raw=True** in signal handlers to avoid accessing incomplete data.

3. **Use post_migrate** for post-fixture setup tasks rather than ``post_save``.

4. **Verify polymorphic_ctype** after loading fixtures if needed:

   .. code-block:: python

       from polymorphic.utils import reset_polymorphic_ctype
       from myapp.models import Endpoint, Switch

       # After loaddata, ensure ctype is correct
       reset_polymorphic_ctype(Endpoint, Switch)

For more details, see `issue #502 <https://github.com/django-polymorphic/django-polymorphic/issues/502>`_.

Using Third Party Models (without modifying them)
-------------------------------------------------

Third party models can be used as polymorphic models without
restrictions by subclassing them. E.g. using a third party
model as the root of a polymorphic inheritance tree:

.. code-block:: python

    from thirdparty import ThirdPartyModel

    class MyThirdPartyBaseModel(PolymorphicModel, ThirdPartyModel):
        pass    # or add fields

Or instead integrating the third party model anywhere into an
existing polymorphic inheritance tree:

.. code-block:: python

    class MyBaseModel(SomePolymorphicModel):
        my_field = models.CharField(max_length=10)

    class MyModelWithThirdParty(MyBaseModel, ThirdPartyModel):
        pass    # or add fields


Non-Polymorphic Queries
-----------------------

If you insert :meth:`~polymorphic.managers.PolymorphicQuerySet.non_polymorphic` anywhere into the
query chain, then :pypi:`django-polymorphic` will simply leave out the final step of retrieving the
real objects, and the manager/queryset will return objects of the type of the base class you used
for the query, like vanilla Django would (``ModelA`` in this example).

.. code-block:: python

    >>> qs=ModelA.objects.non_polymorphic().all()
    >>> qs
    [ <ModelA: id 1, field1 (CharField)>,
      <ModelA: id 2, field1 (CharField)>,
      <ModelA: id 3, field1 (CharField)> ]

There are no other changes in the behaviour of the queryset. For example,
enhancements for ``filter()`` or ``instance_of()`` etc. still work as expected.
If you do the final step yourself, you get the usual polymorphic result:

.. code-block:: python
    
    >>> ModelA.objects.get_real_instances(qs)
    [ <ModelA: id 1, field1 (CharField)>,
      <ModelB: id 2, field1 (CharField), field2 (CharField)>,
      <ModelC: id 3, field1 (CharField), field2 (CharField), field3 (CharField)> ]


About Queryset Methods
----------------------

*   :meth:`~django.db.models.query.QuerySet.annotate` and
    :meth:`~django.db.models.query.QuerySet.aggregate` work just as usual, with the addition that
    the ``ModelX___field`` syntax can be used for the keyword arguments (but not for the non-keyword
    arguments).

*   :meth:`~django.db.models.query.QuerySet.order_by` similarly supports the ``ModelX___field``
    syntax for specifying ordering through a field in a submodel.

*   :meth:`~django.db.models.query.QuerySet.distinct` works as expected. It only regards the fields
    of the base class, but this should never make a difference.

*   :meth:`~django.db.models.query.QuerySet.select_related` works just as usual, but it can not
    (yet) be used to select relations in inherited models (like
    ``ModelA.objects.select_related('ModelC___fieldxy')`` )

*   :meth:`~django.db.models.query.QuerySet.extra` works as expected (it returns polymorphic
    results) but currently has one restriction: The resulting objects are required to have a unique
    primary key within the result set - otherwise an error is thrown (this case could be made to
    work, however it may be mostly unneeded).. The keyword-argument "polymorphic" is no longer
    supported. You can get back the old non-polymorphic behaviour by using
    ``ModelA.objects.non_polymorphic().extra(...)``.

*   :meth:`~polymorphic.managers.PolymorphicQuerySet.get_real_instances` allows you to turn a
    queryset or list  of base model objects efficiently into the real objects.
    For example, you could do ``base_objects_queryset=ModelA.extra(...).non_polymorphic()``
    and then call ``real_objects=base_objects_queryset.get_real_instances()``. Or alternatively
    ``real_objects=ModelA.objects.get_real_instances(base_objects_queryset_or_object_list)``

*   :meth:`~django.db.models.query.QuerySet.values` &
    :meth:`~django.db.models.query.QuerySet.values_list` currently do not return polymorphic
    results. This may change in the future however. If you want to use these methods now, it's best
    if you use ``Model.base_objects.values...`` as this is guaranteed to not change.

*   :meth:`~django.db.models.query.QuerySet.defer` and :meth:`~django.db.models.query.QuerySet.only`
    work as expected. On Django 1.5+ they support the ``ModelX___field`` syntax, but on Django 1.4
    it is only possible to pass fields on the base model into these methods.


Using enhanced Q-objects in any Places
--------------------------------------

The queryset enhancements (e.g. :meth:`~polymorphic.managers.PolymorphicQuerySet.instance_of`)
only work as arguments to the member functions of a polymorphic queryset.  Occasionally it may
be useful to be able to use Q objects with these enhancements in other places. As Django doesn't
understand these enhanced Q objects, you need to transform them manually into normal Q objects
before you can feed them to a Django queryset or function:

.. code-block:: python

    normal_q_object = ModelA.translate_polymorphic_Q_object( Q(instance_of=Model2B) )

This function cannot be used at model creation time however (in models.py), as it may need to access
the ContentTypes database table.


Nicely Displaying Polymorphic Querysets
---------------------------------------

In order to get the output as seen in all examples here, you need to use the
:class:`~polymorphic.showfields.ShowFieldType` class mixin:

.. code-block:: python

    from polymorphic.models import PolymorphicModel
    from polymorphic.showfields import ShowFieldType

    class ModelA(ShowFieldType, PolymorphicModel):
        field1 = models.CharField(max_length=10)

You may also use :class:`~polymorphic.showfields.ShowFieldContent` or
:class:`~polymorphic.showfields.ShowFieldTypeAndContent` to display additional information when
printing querysets (or converting them to text).

When showing field contents, they will be truncated to 20 characters. You can modify this behavior
by setting a class variable in your model like this:

.. code-block:: python

    class ModelA(ShowFieldType, PolymorphicModel):
        polymorphic_showfield_max_field_width = 20
        ...

Similarly, pre-V1.0 output formatting can be re-estated by using
``polymorphic_showfield_old_format = True``.


Create Children from Parents (Downcasting)
------------------------------------------

You can create an instance of a subclass from an existing instance of a superclass using the
:meth:`~polymorphic.managers.PolymorphicManager.create_from_super` method
of the subclass's manager. For example:

.. code-block:: python

    super_instance = ModelA.objects.get(id=1)
    sub_instance = ModelB.objects.create_from_super(super_instance, field2='value2')

The restriction is that ``super_instance`` must be an instance of the direct superclass of
``ModelB``, and any required fields of ``ModelB`` must be provided as keyword arguments. If multiple
levels of subclassing are involved, you must call this method multiple times to "promote" each
level.

Delete Children, Leaving Parents (Upcasting)
--------------------------------------------

The reverse operation of :meth:`~polymorphic.managers.PolymorphicManager.create_from_super` is to
delete the subclass instance while keeping the superclass instance. This can be done using the
``keep_parents=True`` argument to :meth:`~django.db.models.Model.delete`. :pypi:`django-polymorphic`
ensures that the ``polymorphic_ctype`` fields of the superclass instances are updated accordingly
when doing this.

.. _restrictions:

Restrictions & Caveats
----------------------

*   Database Performance regarding concrete Model inheritance in general. Please see
    :ref:`performance`.

*   Queryset methods :meth:`~django.db.models.query.QuerySet.values`,
    :meth:`~django.db.models.query.QuerySet.values_list`, and
    :meth:`~django.db.models.query.QuerySet.select_related` are not yet fully supported (see above).
    :meth:`~django.db.models.query.QuerySet.extra` has one restriction: the resulting objects are
    required to have a unique primary key within the result set.

*   Diamond shaped inheritance: There seems to be a general problem with diamond shaped multiple
    model inheritance with Django models (tested with V1.1 - V1.3). An example
    `is here <http://code.djangoproject.com/ticket/10808>`_. This problem is aggravated when trying
    to enhance :class:`~django.db.models.Model` by subclassing it instead of modifying Django core
    (as we do here with :class:`~polymorphic.models.PolymorphicModel`).

*   The enhanced filter-definitions/Q-objects only work as arguments for the methods of the
    polymorphic querysets. Please see above for ``translate_polymorphic_Q_object``.

*   When using the :django-admin:`dumpdata` management command on polymorphic tables
    (or any table that has a reference to :class:`~django.contrib.contenttypes.models.ContentType`),
    include the :option:`--natural-primary <dumpdata.--natural-primary>` and
    :option:`--natural-foreign <dumpdata.--natural-foreign>` flags in the arguments.
    See :ref:`Working with Signals and Fixtures` for more details on using fixtures with
    polymorphic models.

*   If the ``polymorphic_ctype_id`` on the base table points to the wrong
    :class:`~django.contrib.contenttypes.models.ContentType` (this can happen if you delete child
    rows manually with raw SQL, ``DELETE FROM table``), then polymorphic queries will elide the
    corresponding model objects:
    
    *   ``BaseClass.objects.all()`` will **exclude** these rows (it filters for existing child types).
    *   ``BaseClass.objects.non_polymorphic().all()`` will behave as normal - but polymorphic
        behavior for the affected rows will be undefined - for instance,
        :meth:`~polymorphic.managers.PolymorphicQuerySet.get_real_instances` will raise an
        exception.
    
    Always use ``instance.delete()`` or ``QuerySet.delete()`` to ensure cascading deletion of the
    base row. If you must delete manually, ensure you also delete the corresponding row from the
    base table.

.. old links:
    - http://code.djangoproject.com/wiki/ModelInheritance
    - http://lazypython.blogspot.com/2009/02/second-look-at-inheritance-and.html
    - http://www.djangosnippets.org/snippets/1031/
    - http://www.djangosnippets.org/snippets/1034/
    - http://groups.google.com/group/django-developers/browse_frm/thread/7d40ad373ebfa912/a20fabc661b7035d?lnk=gst&q=model+inheritance+CORBA#a20fabc661b7035d
    - http://groups.google.com/group/django-developers/browse_thread/thread/9bc2aaec0796f4e0/0b92971ffc0aa6f8?lnk=gst&q=inheritance#0b92971ffc0aa6f8
    - http://groups.google.com/group/django-developers/browse_thread/thread/3947c594100c4adb/d8c0af3dacad412d?lnk=gst&q=inheritance#d8c0af3dacad412d
    - http://groups.google.com/group/django-users/browse_thread/thread/52f72cffebb705e/b76c9d8c89a5574f
    - http://peterbraden.co.uk/article/django-inheritance
    - http://www.hopelessgeek.com/2009/11/25/a-hack-for-multi-table-inheritance-in-django
    - http://stackoverflow.com/questions/929029/how-do-i-access-the-child-classes-of-an-object-in-django-without-knowing-the-name/929982#929982
    - http://stackoverflow.com/questions/1581024/django-inheritance-how-to-have-one-method-for-all-subclasses
    - http://groups.google.com/group/django-users/browse_thread/thread/cbdaf2273781ccab/e676a537d735d9ef?lnk=gst&q=polymorphic#e676a537d735d9ef
    - http://groups.google.com/group/django-users/browse_thread/thread/52f72cffebb705e/bc18c18b2e83881e?lnk=gst&q=model+inheritance#bc18c18b2e83881e
    - http://code.djangoproject.com/ticket/10808
    - http://code.djangoproject.com/ticket/7270

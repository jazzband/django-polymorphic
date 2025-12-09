Proxy Models
============

:pypi:`django-polymorphic` has supported :ref:`proxy models <django:proxy-models>` since they were
introduced in Django but the default implementation is unintuitive. If a row is created from the
proxy model the :class:`~django.contrib.contenttypes.models.ContentType` of the proxy class is
recorded. This allows patterns that need to alter behavior based on which class was used to create
the row.

**By default the queryset on proxy models will filter on instance_of(ProxyModel) which will exclude
any rows that were not created from the proxy.**

.. code-block:: python

    from polymorphic.models import PolymorphicModel

    class MyModel(PolymorphicModel):
        ...

    class MyProxy(MyModel):
        class Meta:
            proxy = True

    
    MyModel.objects.create()
    MyProxy.objects.create()

    assert MyModel.objects.count() == 2
    assert MyProxy.objects.count() == 1

This behavior may be unexpected for typical uses of proxy models which involves creating from the
concrete class then accessing from a proxy in the context where you need the modified proxy
interface. There is a
`discussion <https://github.com/jazzband/django-polymorphic/discussions/689>`_ if this should
continue to be the default behavior in version 5+.

Polymorphic Proxy Queries
-------------------------

.. versionadded:: 4.3

If you wish for your proxy model querysets to behave polymorphically by default
(include all rows created by the proxy and concrete models in the class's inheritance tree) then
instead of (or in additon to) :attr:`~django.db.models.Options.proxy` set a
:attr:`Meta.polymorphic_proxy` attribute to True:

.. code-block:: python

    from polymorphic.models import PolymorphicModel

    class MyModel(PolymorphicModel):
        ...

    class MyProxy(MyModel):
        class Meta:
            polymorphc_proxy = True


    MyModel.objects.create()
    MyProxy.objects.create()

    assert MyModel.objects.count() == 2
    assert MyProxy.objects.count() == 2

    for proxy in MyProxy.objects.all():
        assert isinstance(proxy, MyProxy)  # 
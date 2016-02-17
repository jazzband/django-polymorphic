Migrating existing models to polymorphic
========================================

Existing models can be migrated to become polymorphic models.
During the migrating, the ``polymorphic_ctype`` field needs to be filled in.

This can be done in the following steps:

1. Inherit your model from :class:`~polymorphic.models.PolymorphicModel`
2. Create a Django migration file to create the ``polymorphic_ctype_id`` database column.
2. Make sure the proper :class:`~django.contrib.contenttypes.models.ContentType` value is filled in.

Filling the content type value
------------------------------

The following Python code can be used to fill the value of a model:

.. code-block:: python

    from django.contrib.contenttypes.models import ContentType
    from myapp.models import MyModel

    new_ct = ContentType.objects.get_for_model(MyModel)
    MyModel.objects.filter(polymorphic_ctype__isnull=True).update(polymorphic_ctype=new_ct)

The creation and update of the ``polymorphic_ctype_id`` column
can be included in a single Django migration. For example:

.. code-block:: python

    # -*- coding: utf-8 -*-
    from __future__ import unicode_literals
    from django.db import migrations, models


    def forwards_func(apps, schema_editor):
        MyModel = apps.get_model('myapp', 'MyModel')
        ContentType = apps.get_model('contenttypes', 'ContentType')

        new_ct = ContentType.objects.get_for_model(MyModel)
        MyModel.objects.filter(polymorphic_ctype__isnull=True).update(polymorphic_ctype=new_ct)


    def backwards_func(apps, schema_editor):
        pass


    class Migration(migrations.Migration):

        dependencies = [
            ('contenttypes', '0001_initial'),
            ('myapp', '0001_initial'),
        ]

        operations = [
            migrations.AddField(
                model_name='mymodel',
                name='polymorphic_ctype',
                field=models.ForeignKey(related_name='polymorphic_myapp.mymodel_set+', editable=False, to='contenttypes.ContentType', null=True),
            ),
            migrations.RunPython(forwards_func, backwards_func),
        ]

It's recommended to let ``makemigrations`` create the migration file,
and include the ``RunPython`` manually before running the migration.

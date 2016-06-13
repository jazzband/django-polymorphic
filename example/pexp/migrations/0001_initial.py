# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import polymorphic.showfields


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='NormalModelA',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('field1', models.CharField(max_length=10)),
            ],
        ),
        migrations.CreateModel(
            name='Project',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('topic', models.CharField(max_length=30)),
            ],
            options={
                'abstract': False,
            },
            bases=(polymorphic.showfields.ShowFieldContent, models.Model),
        ),
        migrations.CreateModel(
            name='ProxyBase',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=200)),
                ('polymorphic_ctype', models.ForeignKey(related_name='polymorphic_pexp.proxybase_set+', editable=False, to='contenttypes.ContentType', null=True)),
            ],
            options={
                'ordering': ('title',),
            },
        ),
        migrations.CreateModel(
            name='TestModelA',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('field1', models.CharField(max_length=10)),
            ],
            options={
                'abstract': False,
            },
            bases=(polymorphic.showfields.ShowFieldTypeAndContent, models.Model),
        ),
        migrations.CreateModel(
            name='UUIDModelA',
            fields=[
                ('uuid_primary_key', models.UUIDField(serialize=False, primary_key=True)),
                ('field1', models.CharField(max_length=10)),
            ],
            options={
                'abstract': False,
            },
            bases=(polymorphic.showfields.ShowFieldTypeAndContent, models.Model),
        ),
        migrations.CreateModel(
            name='ArtProject',
            fields=[
                ('project_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='pexp.Project')),
                ('artist', models.CharField(max_length=30)),
            ],
            options={
                'abstract': False,
            },
            bases=('pexp.project',),
        ),
        migrations.CreateModel(
            name='NormalModelB',
            fields=[
                ('normalmodela_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='pexp.NormalModelA')),
                ('field2', models.CharField(max_length=10)),
            ],
            bases=('pexp.normalmodela',),
        ),
        migrations.CreateModel(
            name='ResearchProject',
            fields=[
                ('project_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='pexp.Project')),
                ('supervisor', models.CharField(max_length=30)),
            ],
            options={
                'abstract': False,
            },
            bases=('pexp.project',),
        ),
        migrations.CreateModel(
            name='TestModelB',
            fields=[
                ('testmodela_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='pexp.TestModelA')),
                ('field2', models.CharField(max_length=10)),
            ],
            options={
                'abstract': False,
            },
            bases=('pexp.testmodela',),
        ),
        migrations.CreateModel(
            name='UUIDModelB',
            fields=[
                ('uuidmodela_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='pexp.UUIDModelA')),
                ('field2', models.CharField(max_length=10)),
            ],
            options={
                'abstract': False,
            },
            bases=('pexp.uuidmodela',),
        ),
        migrations.AddField(
            model_name='uuidmodela',
            name='polymorphic_ctype',
            field=models.ForeignKey(related_name='polymorphic_pexp.uuidmodela_set+', editable=False, to='contenttypes.ContentType', null=True),
        ),
        migrations.AddField(
            model_name='testmodela',
            name='polymorphic_ctype',
            field=models.ForeignKey(related_name='polymorphic_pexp.testmodela_set+', editable=False, to='contenttypes.ContentType', null=True),
        ),
        migrations.AddField(
            model_name='project',
            name='polymorphic_ctype',
            field=models.ForeignKey(related_name='polymorphic_pexp.project_set+', editable=False, to='contenttypes.ContentType', null=True),
        ),
        migrations.CreateModel(
            name='ProxyA',
            fields=[
            ],
            options={
                'proxy': True,
            },
            bases=('pexp.proxybase',),
        ),
        migrations.CreateModel(
            name='ProxyB',
            fields=[
            ],
            options={
                'proxy': True,
            },
            bases=('pexp.proxybase',),
        ),
        migrations.CreateModel(
            name='NormalModelC',
            fields=[
                ('normalmodelb_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='pexp.NormalModelB')),
                ('field3', models.CharField(max_length=10)),
            ],
            bases=('pexp.normalmodelb',),
        ),
        migrations.CreateModel(
            name='TestModelC',
            fields=[
                ('testmodelb_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='pexp.TestModelB')),
                ('field3', models.CharField(max_length=10)),
                ('field4', models.ManyToManyField(related_name='related_c', to='pexp.TestModelB')),
            ],
            options={
                'abstract': False,
            },
            bases=('pexp.testmodelb',),
        ),
        migrations.CreateModel(
            name='UUIDModelC',
            fields=[
                ('uuidmodelb_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='pexp.UUIDModelB')),
                ('field3', models.CharField(max_length=10)),
            ],
            options={
                'abstract': False,
            },
            bases=('pexp.uuidmodelb',),
        ),
    ]

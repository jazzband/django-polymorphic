# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import polymorphic.showfields
import uuid

try:
    from django.db.models import UUIDField
except ImportError:
    # django<1.8
    from polymorphic.tools_for_tests import UUIDField


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Base',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('field_b', models.CharField(max_length=10)),
            ],
            options={
                'abstract': False,
            },
            bases=(polymorphic.showfields.ShowFieldType, models.Model),
        ),
        migrations.CreateModel(
            name='BlogBase',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=10)),
            ],
            options={
                'abstract': False,
            },
            bases=(polymorphic.showfields.ShowFieldTypeAndContent, models.Model),
        ),
        migrations.CreateModel(
            name='BlogEntry',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('text', models.CharField(max_length=10)),
                ('polymorphic_ctype', models.ForeignKey(related_name='polymorphic_tests.blogentry_set+', editable=False, to='contenttypes.ContentType', null=True)),
            ],
            options={
                'abstract': False,
            },
            bases=(polymorphic.showfields.ShowFieldTypeAndContent, models.Model),
        ),
        migrations.CreateModel(
            name='BlogEntry_limit_choices_to',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('text', models.CharField(max_length=10)),
            ],
            options={
                'abstract': False,
            },
            bases=(polymorphic.showfields.ShowFieldTypeAndContent, models.Model),
        ),
        migrations.CreateModel(
            name='ChildModelWithManager',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='CustomPkBase',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('b', models.CharField(max_length=1)),
            ],
            options={
                'abstract': False,
            },
            bases=(polymorphic.showfields.ShowFieldTypeAndContent, models.Model),
        ),
        migrations.CreateModel(
            name='DateModel',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('date', models.DateTimeField()),
                ('polymorphic_ctype', models.ForeignKey(related_name='polymorphic_tests.datemodel_set+', editable=False, to='contenttypes.ContentType', null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Enhance_Base',
            fields=[
                ('base_id', models.AutoField(serialize=False, primary_key=True)),
                ('field_b', models.CharField(max_length=10)),
            ],
            options={
                'abstract': False,
            },
            bases=(polymorphic.showfields.ShowFieldTypeAndContent, models.Model),
        ),
        migrations.CreateModel(
            name='Enhance_Plain',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('field_p', models.CharField(max_length=10)),
            ],
        ),
        migrations.CreateModel(
            name='InitTestModel',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('bar', models.CharField(max_length=100)),
            ],
            options={
                'abstract': False,
            },
            bases=(polymorphic.showfields.ShowFieldType, models.Model),
        ),
        migrations.CreateModel(
            name='MgrInheritA',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('field1', models.CharField(max_length=10)),
            ],
        ),
        migrations.CreateModel(
            name='Model2A',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('field1', models.CharField(max_length=10)),
            ],
            options={
                'abstract': False,
            },
            bases=(polymorphic.showfields.ShowFieldType, models.Model),
        ),
        migrations.CreateModel(
            name='ModelExtraA',
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
            name='ModelExtraExternal',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('topic', models.CharField(max_length=10)),
            ],
        ),
        migrations.CreateModel(
            name='ModelFieldNameTest',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('modelfieldnametest', models.CharField(max_length=10)),
                ('polymorphic_ctype', models.ForeignKey(related_name='polymorphic_tests.modelfieldnametest_set+', editable=False, to='contenttypes.ContentType', null=True)),
            ],
            options={
                'abstract': False,
            },
            bases=(polymorphic.showfields.ShowFieldType, models.Model),
        ),
        migrations.CreateModel(
            name='ModelShow1',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('field1', models.CharField(max_length=10)),
                ('m2m', models.ManyToManyField(related_name='_modelshow1_m2m_+', to='tests.ModelShow1')),
                ('polymorphic_ctype', models.ForeignKey(related_name='polymorphic_tests.modelshow1_set+', editable=False, to='contenttypes.ContentType', null=True)),
            ],
            options={
                'abstract': False,
            },
            bases=(polymorphic.showfields.ShowFieldType, models.Model),
        ),
        migrations.CreateModel(
            name='ModelShow1_plain',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('field1', models.CharField(max_length=10)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='ModelShow2',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('field1', models.CharField(max_length=10)),
                ('m2m', models.ManyToManyField(related_name='_modelshow2_m2m_+', to='tests.ModelShow2')),
                ('polymorphic_ctype', models.ForeignKey(related_name='polymorphic_tests.modelshow2_set+', editable=False, to='contenttypes.ContentType', null=True)),
            ],
            options={
                'abstract': False,
            },
            bases=(polymorphic.showfields.ShowFieldContent, models.Model),
        ),
        migrations.CreateModel(
            name='ModelShow3',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('field1', models.CharField(max_length=10)),
                ('m2m', models.ManyToManyField(related_name='_modelshow3_m2m_+', to='tests.ModelShow3')),
                ('polymorphic_ctype', models.ForeignKey(related_name='polymorphic_tests.modelshow3_set+', editable=False, to='contenttypes.ContentType', null=True)),
            ],
            options={
                'abstract': False,
            },
            bases=(polymorphic.showfields.ShowFieldTypeAndContent, models.Model),
        ),
        migrations.CreateModel(
            name='ModelUnderRelChild',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('_private2', models.CharField(max_length=10)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='ModelUnderRelParent',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('field1', models.CharField(max_length=10)),
                ('_private', models.CharField(max_length=10)),
                ('polymorphic_ctype', models.ForeignKey(related_name='polymorphic_tests.modelunderrelparent_set+', editable=False, to='contenttypes.ContentType', null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='MROBase1',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('field1', models.CharField(max_length=10)),
            ],
            options={
                'abstract': False,
            },
            bases=(polymorphic.showfields.ShowFieldType, models.Model),
        ),
        migrations.CreateModel(
            name='MROBase3',
            fields=[
                ('base_3_id', models.AutoField(serialize=False, primary_key=True)),
            ],
        ),
        migrations.CreateModel(
            name='One2OneRelatingModel',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('field1', models.CharField(max_length=10)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='ParentModelWithManager',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('polymorphic_ctype', models.ForeignKey(related_name='polymorphic_tests.parentmodelwithmanager_set+', editable=False, to='contenttypes.ContentType', null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='PlainA',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('field1', models.CharField(max_length=10)),
            ],
        ),
        migrations.CreateModel(
            name='PlainChildModelWithManager',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
            ],
        ),
        migrations.CreateModel(
            name='PlainParentModelWithManager',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
            ],
        ),
        migrations.CreateModel(
            name='ProxiedBase',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=10)),
                ('polymorphic_ctype', models.ForeignKey(related_name='polymorphic_tests.proxiedbase_set+', editable=False, to='contenttypes.ContentType', null=True)),
            ],
            options={
                'abstract': False,
            },
            bases=(polymorphic.showfields.ShowFieldTypeAndContent, models.Model),
        ),
        migrations.CreateModel(
            name='ProxyBase',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('some_data', models.CharField(max_length=128)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='RelatedNameClash',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('ctype', models.ForeignKey(editable=False, to='contenttypes.ContentType', null=True)),
                ('polymorphic_ctype', models.ForeignKey(related_name='polymorphic_tests.relatednameclash_set+', editable=False, to='contenttypes.ContentType', null=True)),
            ],
            options={
                'abstract': False,
            },
            bases=(polymorphic.showfields.ShowFieldType, models.Model),
        ),
        migrations.CreateModel(
            name='RelatingModel',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
            ],
        ),
        migrations.CreateModel(
            name='RelationBase',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('field_base', models.CharField(max_length=10)),
            ],
            options={
                'abstract': False,
            },
            bases=(polymorphic.showfields.ShowFieldTypeAndContent, models.Model),
        ),
        migrations.CreateModel(
            name='Top',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=50)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='UUIDPlainA',
            fields=[
                ('uuid_primary_key', UUIDField(default=uuid.uuid1, serialize=False, primary_key=True)),
                ('field1', models.CharField(max_length=10)),
            ],
        ),
        migrations.CreateModel(
            name='UUIDProject',
            fields=[
                ('uuid_primary_key', UUIDField(default=uuid.uuid1, serialize=False, primary_key=True)),
                ('topic', models.CharField(max_length=30)),
            ],
            options={
                'abstract': False,
            },
            bases=(polymorphic.showfields.ShowFieldTypeAndContent, models.Model),
        ),
        migrations.CreateModel(
            name='BlogA',
            fields=[
                ('blogbase_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='tests.BlogBase')),
                ('info', models.CharField(max_length=10)),
            ],
            options={
                'abstract': False,
            },
            bases=('tests.blogbase',),
        ),
        migrations.CreateModel(
            name='BlogB',
            fields=[
                ('blogbase_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='tests.BlogBase')),
            ],
            options={
                'abstract': False,
            },
            bases=('tests.blogbase',),
        ),
        migrations.CreateModel(
            name='CustomPkInherit',
            fields=[
                ('custompkbase_ptr', models.OneToOneField(parent_link=True, auto_created=True, to='tests.CustomPkBase')),
                ('custom_id', models.AutoField(serialize=False, primary_key=True)),
                ('i', models.CharField(max_length=1)),
            ],
            options={
                'abstract': False,
            },
            bases=('tests.custompkbase',),
        ),
        migrations.CreateModel(
            name='Enhance_Inherit',
            fields=[
                ('enhance_plain_ptr', models.OneToOneField(parent_link=True, auto_created=True, to='tests.Enhance_Plain')),
                ('enhance_base_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='tests.Enhance_Base')),
                ('field_i', models.CharField(max_length=10)),
            ],
            options={
                'abstract': False,
            },
            bases=('tests.enhance_base', 'tests.enhance_plain'),
        ),
        migrations.CreateModel(
            name='InitTestModelSubclass',
            fields=[
                ('inittestmodel_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='tests.InitTestModel')),
            ],
            options={
                'abstract': False,
            },
            bases=('tests.inittestmodel',),
        ),
        migrations.CreateModel(
            name='MgrInheritB',
            fields=[
                ('mgrinherita_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='tests.MgrInheritA')),
                ('field2', models.CharField(max_length=10)),
            ],
            bases=('tests.mgrinherita',),
        ),
        migrations.CreateModel(
            name='Middle',
            fields=[
                ('top_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='tests.Top')),
                ('description', models.TextField()),
            ],
            options={
                'abstract': False,
            },
            bases=('tests.top',),
        ),
        migrations.CreateModel(
            name='Model2B',
            fields=[
                ('model2a_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='tests.Model2A')),
                ('field2', models.CharField(max_length=10)),
            ],
            options={
                'abstract': False,
            },
            bases=('tests.model2a',),
        ),
        migrations.CreateModel(
            name='ModelExtraB',
            fields=[
                ('modelextraa_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='tests.ModelExtraA')),
                ('field2', models.CharField(max_length=10)),
            ],
            options={
                'abstract': False,
            },
            bases=('tests.modelextraa',),
        ),
        migrations.CreateModel(
            name='ModelShow2_plain',
            fields=[
                ('modelshow1_plain_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='tests.ModelShow1_plain')),
                ('field2', models.CharField(max_length=10)),
            ],
            options={
                'abstract': False,
            },
            bases=('tests.modelshow1_plain',),
        ),
        migrations.CreateModel(
            name='ModelWithMyManager',
            fields=[
                ('model2a_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='tests.Model2A')),
                ('field4', models.CharField(max_length=10)),
            ],
            options={
                'abstract': False,
            },
            bases=(polymorphic.showfields.ShowFieldTypeAndContent, 'tests.model2a'),
        ),
        migrations.CreateModel(
            name='ModelWithMyManager2',
            fields=[
                ('model2a_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='tests.Model2A')),
                ('field4', models.CharField(max_length=10)),
            ],
            options={
                'abstract': False,
            },
            bases=(polymorphic.showfields.ShowFieldTypeAndContent, 'tests.model2a'),
        ),
        migrations.CreateModel(
            name='ModelWithMyManagerDefault',
            fields=[
                ('model2a_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='tests.Model2A')),
                ('field4', models.CharField(max_length=10)),
            ],
            options={
                'abstract': False,
            },
            bases=(polymorphic.showfields.ShowFieldTypeAndContent, 'tests.model2a'),
        ),
        migrations.CreateModel(
            name='ModelWithMyManagerNoDefault',
            fields=[
                ('model2a_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='tests.Model2A')),
                ('field4', models.CharField(max_length=10)),
            ],
            options={
                'abstract': False,
            },
            bases=(polymorphic.showfields.ShowFieldTypeAndContent, 'tests.model2a'),
        ),
        migrations.CreateModel(
            name='ModelX',
            fields=[
                ('base_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='tests.Base')),
                ('field_x', models.CharField(max_length=10)),
            ],
            options={
                'abstract': False,
            },
            bases=('tests.base',),
        ),
        migrations.CreateModel(
            name='ModelY',
            fields=[
                ('base_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='tests.Base')),
                ('field_y', models.CharField(max_length=10)),
            ],
            options={
                'abstract': False,
            },
            bases=('tests.base',),
        ),
        migrations.CreateModel(
            name='MROBase2',
            fields=[
                ('mrobase1_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='tests.MROBase1')),
            ],
            options={
                'abstract': False,
            },
            bases=('tests.mrobase1',),
        ),
        migrations.CreateModel(
            name='NonProxyChild',
            fields=[
                ('proxybase_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='tests.ProxyBase')),
                ('name', models.CharField(max_length=10)),
            ],
            options={
                'abstract': False,
            },
            bases=('tests.proxybase',),
        ),
        migrations.CreateModel(
            name='One2OneRelatingModelDerived',
            fields=[
                ('one2onerelatingmodel_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='tests.One2OneRelatingModel')),
                ('field2', models.CharField(max_length=10)),
            ],
            options={
                'abstract': False,
            },
            bases=('tests.one2onerelatingmodel',),
        ),
        migrations.CreateModel(
            name='PlainB',
            fields=[
                ('plaina_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='tests.PlainA')),
                ('field2', models.CharField(max_length=10)),
            ],
            bases=('tests.plaina',),
        ),
        migrations.CreateModel(
            name='RelationA',
            fields=[
                ('relationbase_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='tests.RelationBase')),
                ('field_a', models.CharField(max_length=10)),
            ],
            options={
                'abstract': False,
            },
            bases=('tests.relationbase',),
        ),
        migrations.CreateModel(
            name='RelationB',
            fields=[
                ('relationbase_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='tests.RelationBase')),
                ('field_b', models.CharField(max_length=10)),
            ],
            options={
                'abstract': False,
            },
            bases=('tests.relationbase',),
        ),
        migrations.CreateModel(
            name='TestParentLinkAndRelatedName',
            fields=[
                ('superclass', models.OneToOneField(parent_link=True, related_name='related_name_subclass', primary_key=True, serialize=False, to='tests.ModelShow1_plain')),
            ],
            options={
                'abstract': False,
            },
            bases=('tests.modelshow1_plain',),
        ),
        migrations.CreateModel(
            name='UUIDArtProject',
            fields=[
                ('uuidproject_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='tests.UUIDProject')),
                ('artist', models.CharField(max_length=30)),
            ],
            options={
                'abstract': False,
            },
            bases=('tests.uuidproject',),
        ),
        migrations.CreateModel(
            name='UUIDPlainB',
            fields=[
                ('uuidplaina_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='tests.UUIDPlainA')),
                ('field2', models.CharField(max_length=10)),
            ],
            bases=('tests.uuidplaina',),
        ),
        migrations.CreateModel(
            name='UUIDResearchProject',
            fields=[
                ('uuidproject_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='tests.UUIDProject')),
                ('supervisor', models.CharField(max_length=30)),
            ],
            options={
                'abstract': False,
            },
            bases=('tests.uuidproject',),
        ),
        migrations.AddField(
            model_name='uuidproject',
            name='polymorphic_ctype',
            field=models.ForeignKey(related_name='polymorphic_tests.uuidproject_set+', editable=False, to='contenttypes.ContentType', null=True),
        ),
        migrations.AddField(
            model_name='top',
            name='polymorphic_ctype',
            field=models.ForeignKey(related_name='polymorphic_tests.top_set+', editable=False, to='contenttypes.ContentType', null=True),
        ),
        migrations.AddField(
            model_name='relationbase',
            name='fk',
            field=models.ForeignKey(related_name='relationbase_set', to='tests.RelationBase', null=True),
        ),
        migrations.AddField(
            model_name='relationbase',
            name='m2m',
            field=models.ManyToManyField(related_name='_relationbase_m2m_+', to='tests.RelationBase'),
        ),
        migrations.AddField(
            model_name='relationbase',
            name='polymorphic_ctype',
            field=models.ForeignKey(related_name='polymorphic_tests.relationbase_set+', editable=False, to='contenttypes.ContentType', null=True),
        ),
        migrations.AddField(
            model_name='relatingmodel',
            name='many2many',
            field=models.ManyToManyField(to='tests.Model2A'),
        ),
        migrations.AddField(
            model_name='proxybase',
            name='polymorphic_ctype',
            field=models.ForeignKey(related_name='polymorphic_tests.proxybase_set+', editable=False, to='contenttypes.ContentType', null=True),
        ),
        migrations.AddField(
            model_name='plainchildmodelwithmanager',
            name='fk',
            field=models.ForeignKey(related_name='childmodel_set', to='tests.PlainParentModelWithManager'),
        ),
        migrations.AddField(
            model_name='one2onerelatingmodel',
            name='one2one',
            field=models.OneToOneField(to='tests.Model2A'),
        ),
        migrations.AddField(
            model_name='one2onerelatingmodel',
            name='polymorphic_ctype',
            field=models.ForeignKey(related_name='polymorphic_tests.one2onerelatingmodel_set+', editable=False, to='contenttypes.ContentType', null=True),
        ),
        migrations.AddField(
            model_name='mrobase1',
            name='polymorphic_ctype',
            field=models.ForeignKey(related_name='polymorphic_tests.mrobase1_set+', editable=False, to='contenttypes.ContentType', null=True),
        ),
        migrations.AddField(
            model_name='modelunderrelchild',
            name='parent',
            field=models.ForeignKey(related_name='children', to='tests.ModelUnderRelParent'),
        ),
        migrations.AddField(
            model_name='modelunderrelchild',
            name='polymorphic_ctype',
            field=models.ForeignKey(related_name='polymorphic_tests.modelunderrelchild_set+', editable=False, to='contenttypes.ContentType', null=True),
        ),
        migrations.AddField(
            model_name='modelshow1_plain',
            name='polymorphic_ctype',
            field=models.ForeignKey(related_name='polymorphic_tests.modelshow1_plain_set+', editable=False, to='contenttypes.ContentType', null=True),
        ),
        migrations.AddField(
            model_name='modelextraa',
            name='polymorphic_ctype',
            field=models.ForeignKey(related_name='polymorphic_tests.modelextraa_set+', editable=False, to='contenttypes.ContentType', null=True),
        ),
        migrations.AddField(
            model_name='model2a',
            name='polymorphic_ctype',
            field=models.ForeignKey(related_name='polymorphic_tests.model2a_set+', editable=False, to='contenttypes.ContentType', null=True),
        ),
        migrations.AddField(
            model_name='inittestmodel',
            name='polymorphic_ctype',
            field=models.ForeignKey(related_name='polymorphic_tests.inittestmodel_set+', editable=False, to='contenttypes.ContentType', null=True),
        ),
        migrations.AddField(
            model_name='enhance_base',
            name='polymorphic_ctype',
            field=models.ForeignKey(related_name='polymorphic_tests.enhance_base_set+', editable=False, to='contenttypes.ContentType', null=True),
        ),
        migrations.AddField(
            model_name='custompkbase',
            name='polymorphic_ctype',
            field=models.ForeignKey(related_name='polymorphic_tests.custompkbase_set+', editable=False, to='contenttypes.ContentType', null=True),
        ),
        migrations.AddField(
            model_name='childmodelwithmanager',
            name='fk',
            field=models.ForeignKey(related_name='childmodel_set', to='tests.ParentModelWithManager'),
        ),
        migrations.AddField(
            model_name='childmodelwithmanager',
            name='polymorphic_ctype',
            field=models.ForeignKey(related_name='polymorphic_tests.childmodelwithmanager_set+', editable=False, to='contenttypes.ContentType', null=True),
        ),
        migrations.AddField(
            model_name='blogentry_limit_choices_to',
            name='blog',
            field=models.ForeignKey(to='tests.BlogBase'),
        ),
        migrations.AddField(
            model_name='blogentry_limit_choices_to',
            name='polymorphic_ctype',
            field=models.ForeignKey(related_name='polymorphic_tests.blogentry_limit_choices_to_set+', editable=False, to='contenttypes.ContentType', null=True),
        ),
        migrations.AddField(
            model_name='blogbase',
            name='polymorphic_ctype',
            field=models.ForeignKey(related_name='polymorphic_tests.blogbase_set+', editable=False, to='contenttypes.ContentType', null=True),
        ),
        migrations.AddField(
            model_name='base',
            name='polymorphic_ctype',
            field=models.ForeignKey(related_name='polymorphic_tests.base_set+', editable=False, to='contenttypes.ContentType', null=True),
        ),
        migrations.CreateModel(
            name='ProxyChild',
            fields=[
            ],
            options={
                'proxy': True,
            },
            bases=('tests.proxybase',),
        ),
        migrations.CreateModel(
            name='ProxyModelBase',
            fields=[
            ],
            options={
                'proxy': True,
            },
            bases=('tests.proxiedbase',),
        ),
        migrations.CreateModel(
            name='Bottom',
            fields=[
                ('middle_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='tests.Middle')),
                ('author', models.CharField(max_length=50)),
            ],
            options={
                'abstract': False,
            },
            bases=('tests.middle',),
        ),
        migrations.CreateModel(
            name='MgrInheritC',
            fields=[
                ('mgrinheritb_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='tests.MgrInheritB')),
            ],
            bases=(polymorphic.showfields.ShowFieldTypeAndContent, 'tests.mgrinheritb'),
        ),
        migrations.CreateModel(
            name='Model2C',
            fields=[
                ('model2b_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='tests.Model2B')),
                ('field3', models.CharField(max_length=10)),
            ],
            options={
                'abstract': False,
            },
            bases=('tests.model2b',),
        ),
        migrations.CreateModel(
            name='ModelExtraC',
            fields=[
                ('modelextrab_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='tests.ModelExtraB')),
                ('field3', models.CharField(max_length=10)),
            ],
            options={
                'abstract': False,
            },
            bases=('tests.modelextrab',),
        ),
        migrations.CreateModel(
            name='MRODerived',
            fields=[
                ('mrobase3_ptr', models.OneToOneField(parent_link=True, auto_created=True, to='tests.MROBase3')),
                ('mrobase2_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='tests.MROBase2')),
            ],
            options={
                'abstract': False,
            },
            bases=('tests.mrobase2', 'tests.mrobase3'),
        ),
        migrations.CreateModel(
            name='PlainC',
            fields=[
                ('plainb_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='tests.PlainB')),
                ('field3', models.CharField(max_length=10)),
            ],
            bases=('tests.plainb',),
        ),
        migrations.CreateModel(
            name='ProxyModelA',
            fields=[
                ('proxiedbase_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='tests.ProxiedBase')),
                ('field1', models.CharField(max_length=10)),
            ],
            options={
                'abstract': False,
            },
            bases=('tests.proxymodelbase',),
        ),
        migrations.CreateModel(
            name='ProxyModelB',
            fields=[
                ('proxiedbase_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='tests.ProxiedBase')),
                ('field2', models.CharField(max_length=10)),
            ],
            options={
                'abstract': False,
            },
            bases=('tests.proxymodelbase',),
        ),
        migrations.CreateModel(
            name='RelationBC',
            fields=[
                ('relationb_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='tests.RelationB')),
                ('field_c', models.CharField(max_length=10)),
            ],
            options={
                'abstract': False,
            },
            bases=('tests.relationb',),
        ),
        migrations.CreateModel(
            name='UUIDPlainC',
            fields=[
                ('uuidplainb_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='tests.UUIDPlainB')),
                ('field3', models.CharField(max_length=10)),
            ],
            bases=('tests.uuidplainb',),
        ),
        migrations.AddField(
            model_name='blogentry',
            name='blog',
            field=models.ForeignKey(to='tests.BlogA'),
        ),
        migrations.CreateModel(
            name='Model2D',
            fields=[
                ('model2c_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='tests.Model2C')),
                ('field4', models.CharField(max_length=10)),
            ],
            options={
                'abstract': False,
            },
            bases=('tests.model2c',),
        ),
    ]

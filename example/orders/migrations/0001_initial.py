# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=200, verbose_name='Title')),
            ],
            options={
                'ordering': ('title',),
                'verbose_name': 'Organisation',
                'verbose_name_plural': 'Organisations',
            },
        ),
        migrations.CreateModel(
            name='Payment',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('currency', models.CharField(default=b'USD', max_length=3)),
                ('amount', models.DecimalField(max_digits=10, decimal_places=2)),
            ],
            options={
                'verbose_name': 'Payment',
                'verbose_name_plural': 'Payments',
            },
        ),
        migrations.CreateModel(
            name='BankPayment',
            fields=[
                ('payment_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='orders.Payment')),
                ('bank_name', models.CharField(max_length=100)),
                ('swift', models.CharField(max_length=20)),
            ],
            options={
                'verbose_name': 'Bank Payment',
                'verbose_name_plural': 'Bank Payments',
            },
            bases=('orders.payment',),
        ),
        migrations.CreateModel(
            name='CreditCardPayment',
            fields=[
                ('payment_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='orders.Payment')),
                ('card_type', models.CharField(max_length=10)),
                ('expiry_month', models.PositiveSmallIntegerField(choices=[(1, 'jan'), (2, 'feb'), (3, 'mar'), (4, 'apr'), (5, 'may'), (6, 'jun'), (7, 'jul'), (8, 'aug'), (9, 'sep'), (10, 'oct'), (11, 'nov'), (12, 'dec')])),
                ('expiry_year', models.PositiveIntegerField()),
            ],
            options={
                'verbose_name': 'Credit Card Payment',
                'verbose_name_plural': 'Credit Card Payments',
            },
            bases=('orders.payment',),
        ),
        migrations.CreateModel(
            name='SepaPayment',
            fields=[
                ('payment_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='orders.Payment')),
                ('iban', models.CharField(max_length=34)),
                ('bic', models.CharField(max_length=11)),
            ],
            options={
                'verbose_name': 'Bank Payment',
                'verbose_name_plural': 'Bank Payments',
            },
            bases=('orders.payment',),
        ),
        migrations.AddField(
            model_name='payment',
            name='order',
            field=models.ForeignKey(to='orders.Order'),
        ),
        migrations.AddField(
            model_name='payment',
            name='polymorphic_ctype',
            field=models.ForeignKey(related_name='polymorphic_orders.payment_set+', editable=False, to='contenttypes.ContentType', null=True),
        ),
    ]

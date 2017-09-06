from __future__ import print_function

from django.contrib.contenttypes.models import ContentType
from django.db.models import Q
from django.test import TestCase

from polymorphic.tests.models import (
    Base,
    BlogA,
    BlogEntry,
    Model2A,
    Model2B,
    Model2C,
    Model2D,
    ModelX,
    ModelY,
    One2OneRelatingModel,
    RelatingModel,
)


class MultipleDatabasesTests(TestCase):
    multi_db = True

    def test_save_to_non_default_database(self):
        Model2A.objects.db_manager('secondary').create(field1='A1')
        Model2C(field1='C1', field2='C2', field3='C3').save(using='secondary')
        Model2B.objects.create(field1='B1', field2='B2')
        Model2D(field1='D1', field2='D2', field3='D3', field4='D4').save()

        self.assertQuerysetEqual(
            Model2A.objects.order_by('id'),
            [Model2B, Model2D],
            transform=lambda o: o.__class__,
        )

        self.assertQuerysetEqual(
            Model2A.objects.db_manager('secondary').order_by('id'),
            [Model2A, Model2C],
            transform=lambda o: o.__class__,
        )

    def test_instance_of_filter_on_non_default_database(self):
        Base.objects.db_manager('secondary').create(field_b='B1')
        ModelX.objects.db_manager('secondary').create(field_b='B', field_x='X')
        ModelY.objects.db_manager('secondary').create(field_b='Y', field_y='Y')

        objects = Base.objects.db_manager('secondary').filter(instance_of=Base)
        self.assertQuerysetEqual(
            objects,
            [Base, ModelX, ModelY],
            transform=lambda o: o.__class__,
            ordered=False,
        )

        self.assertQuerysetEqual(
            Base.objects.db_manager('secondary').filter(instance_of=ModelX),
            [ModelX],
            transform=lambda o: o.__class__,
        )

        self.assertQuerysetEqual(
            Base.objects.db_manager('secondary').filter(instance_of=ModelY),
            [ModelY],
            transform=lambda o: o.__class__,
        )

        self.assertQuerysetEqual(
            Base.objects.db_manager('secondary').filter(
                Q(instance_of=ModelX) | Q(instance_of=ModelY)
            ),
            [ModelX, ModelY],
            transform=lambda o: o.__class__,
            ordered=False,
        )

    def test_forward_many_to_one_descriptor_on_non_default_database(self):
        def func():
            blog = BlogA.objects.db_manager('secondary').create(name='Blog', info='Info')
            entry = BlogEntry.objects.db_manager('secondary').create(blog=blog, text='Text')
            ContentType.objects.clear_cache()
            entry = BlogEntry.objects.db_manager('secondary').get(pk=entry.id)
            self.assertEqual(blog, entry.blog)

        # Ensure no queries are made using the default database.
        self.assertNumQueries(0, func)

    def test_reverse_many_to_one_descriptor_on_non_default_database(self):
        def func():
            blog = BlogA.objects.db_manager('secondary').create(name='Blog', info='Info')
            entry = BlogEntry.objects.db_manager('secondary').create(blog=blog, text='Text')
            ContentType.objects.clear_cache()
            blog = BlogA.objects.db_manager('secondary').get(pk=blog.id)
            self.assertEqual(entry, blog.blogentry_set.using('secondary').get())

        # Ensure no queries are made using the default database.
        self.assertNumQueries(0, func)

    def test_reverse_one_to_one_descriptor_on_non_default_database(self):
        def func():
            m2a = Model2A.objects.db_manager('secondary').create(field1='A1')
            one2one = One2OneRelatingModel.objects.db_manager('secondary').create(one2one=m2a, field1='121')
            ContentType.objects.clear_cache()
            m2a = Model2A.objects.db_manager('secondary').get(pk=m2a.id)
            self.assertEqual(one2one, m2a.one2onerelatingmodel)

        # Ensure no queries are made using the default database.
        self.assertNumQueries(0, func)

    def test_many_to_many_descriptor_on_non_default_database(self):
        def func():
            m2a = Model2A.objects.db_manager('secondary').create(field1='A1')
            rm = RelatingModel.objects.db_manager('secondary').create()
            rm.many2many.add(m2a)
            ContentType.objects.clear_cache()
            m2a = Model2A.objects.db_manager('secondary').get(pk=m2a.id)
            self.assertEqual(rm, m2a.relatingmodel_set.using('secondary').get())

        # Ensure no queries are made using the default database.
        self.assertNumQueries(0, func)

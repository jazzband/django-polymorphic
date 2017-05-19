from __future__ import print_function

from django.contrib.contenttypes.models import ContentType
from django.db.models import Q
from django.test import TestCase

from polymorphic.tests import *  # all models


class MultipleDatabasesTests(TestCase):
    multi_db = True

    def test_save_to_non_default_database(self):
        Model2A.objects.db_manager('secondary').create(field1='A1')
        Model2C(field1='C1', field2='C2', field3='C3').save(using='secondary')
        Model2B.objects.create(field1='B1', field2='B2')
        Model2D(field1='D1', field2='D2', field3='D3', field4='D4').save()

        default_objects = list(Model2A.objects.order_by('id'))
        self.assertEqual(len(default_objects), 2)
        self.assertEqual(repr(default_objects[0]), '<Model2B: id 1, field1 (CharField), field2 (CharField)>')
        self.assertEqual(repr(default_objects[1]), '<Model2D: id 2, field1 (CharField), field2 (CharField), field3 (CharField), field4 (CharField)>')

        secondary_objects = list(Model2A.objects.db_manager('secondary').order_by('id'))
        self.assertEqual(len(secondary_objects), 2)
        self.assertEqual(repr(secondary_objects[0]), '<Model2A: id 1, field1 (CharField)>')
        self.assertEqual(repr(secondary_objects[1]), '<Model2C: id 2, field1 (CharField), field2 (CharField), field3 (CharField)>')

    def test_instance_of_filter_on_non_default_database(self):
        Base.objects.db_manager('secondary').create(field_b='B1')
        ModelX.objects.db_manager('secondary').create(field_b='B', field_x='X')
        ModelY.objects.db_manager('secondary').create(field_b='Y', field_y='Y')

        objects = Base.objects.db_manager('secondary').filter(instance_of=Base)
        self.assertEqual(len(objects), 3)
        self.assertEqual(repr(objects[0]), '<Base: id 1, field_b (CharField)>')
        self.assertEqual(repr(objects[1]), '<ModelX: id 2, field_b (CharField), field_x (CharField)>')
        self.assertEqual(repr(objects[2]), '<ModelY: id 3, field_b (CharField), field_y (CharField)>')

        objects = Base.objects.db_manager('secondary').filter(instance_of=ModelX)
        self.assertEqual(len(objects), 1)
        self.assertEqual(repr(objects[0]), '<ModelX: id 2, field_b (CharField), field_x (CharField)>')

        objects = Base.objects.db_manager('secondary').filter(instance_of=ModelY)
        self.assertEqual(len(objects), 1)
        self.assertEqual(repr(objects[0]), '<ModelY: id 3, field_b (CharField), field_y (CharField)>')

        objects = Base.objects.db_manager('secondary').filter(Q(instance_of=ModelX) | Q(instance_of=ModelY))
        self.assertEqual(len(objects), 2)
        self.assertEqual(repr(objects[0]), '<ModelX: id 2, field_b (CharField), field_x (CharField)>')
        self.assertEqual(repr(objects[1]), '<ModelY: id 3, field_b (CharField), field_y (CharField)>')

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

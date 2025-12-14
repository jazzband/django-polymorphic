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
    RelationA,
    RelationB,
    RelationBase,
)


class MultipleDatabasesTests(TestCase):
    databases = ["default", "secondary"]

    def test_save_to_non_default_database(self):
        Model2A.objects.db_manager("secondary").create(field1="A1")
        Model2C(field1="C1", field2="C2", field3="C3").save(using="secondary")
        Model2B.objects.create(field1="B1", field2="B2")
        Model2D(field1="D1", field2="D2", field3="D3", field4="D4").save()

        self.assertQuerySetEqual(
            Model2A.objects.order_by("id"),
            [Model2B, Model2D],
            transform=lambda o: o.__class__,
        )

        self.assertQuerySetEqual(
            Model2A.objects.db_manager("secondary").order_by("id"),
            [Model2A, Model2C],
            transform=lambda o: o.__class__,
        )

    def test_instance_of_filter_on_non_default_database(self):
        Base.objects.db_manager("secondary").create(field_b="B1")
        ModelX.objects.db_manager("secondary").create(field_b="B", field_x="X")
        ModelY.objects.db_manager("secondary").create(field_b="Y", field_y="Y")

        objects = Base.objects.db_manager("secondary").filter(instance_of=Base)
        self.assertQuerySetEqual(
            objects,
            [Base, ModelX, ModelY],
            transform=lambda o: o.__class__,
            ordered=False,
        )

        self.assertQuerySetEqual(
            Base.objects.db_manager("secondary").filter(instance_of=ModelX),
            [ModelX],
            transform=lambda o: o.__class__,
        )

        self.assertQuerySetEqual(
            Base.objects.db_manager("secondary").filter(instance_of=ModelY),
            [ModelY],
            transform=lambda o: o.__class__,
        )

        self.assertQuerySetEqual(
            Base.objects.db_manager("secondary").filter(
                Q(instance_of=ModelX) | Q(instance_of=ModelY)
            ),
            [ModelX, ModelY],
            transform=lambda o: o.__class__,
            ordered=False,
        )

    def test_forward_many_to_one_descriptor_on_non_default_database(self):
        def func():
            blog = BlogA.objects.db_manager("secondary").create(name="Blog", info="Info")
            entry = BlogEntry.objects.db_manager("secondary").create(blog=blog, text="Text")
            ContentType.objects.clear_cache()
            entry = BlogEntry.objects.db_manager("secondary").get(pk=entry.id)
            assert blog == entry.blog

        # Ensure no queries are made using the default database.
        self.assertNumQueries(0, func)

    def test_reverse_many_to_one_descriptor_on_non_default_database(self):
        def func():
            blog = BlogA.objects.db_manager("secondary").create(name="Blog", info="Info")
            entry = BlogEntry.objects.db_manager("secondary").create(blog=blog, text="Text")
            ContentType.objects.clear_cache()
            blog = BlogA.objects.db_manager("secondary").get(pk=blog.id)
            assert entry == blog.blogentry_set.using("secondary").get()

        # Ensure no queries are made using the default database.
        self.assertNumQueries(0, func)

    def test_reverse_one_to_one_descriptor_on_non_default_database(self):
        def func():
            m2a = Model2A.objects.db_manager("secondary").create(field1="A1")
            one2one = One2OneRelatingModel.objects.db_manager("secondary").create(
                one2one=m2a, field1="121"
            )
            ContentType.objects.clear_cache()
            m2a = Model2A.objects.db_manager("secondary").get(pk=m2a.id)
            assert one2one == m2a.one2onerelatingmodel

        # Ensure no queries are made using the default database.
        self.assertNumQueries(0, func)

    def test_many_to_many_descriptor_on_non_default_database(self):
        def func():
            m2a = Model2A.objects.db_manager("secondary").create(field1="A1")
            rm = RelatingModel.objects.db_manager("secondary").create()
            rm.many2many.add(m2a)
            ContentType.objects.clear_cache()
            m2a = Model2A.objects.db_manager("secondary").get(pk=m2a.id)
            assert rm == m2a.relatingmodel_set.using("secondary").get()

        # Ensure no queries are made using the default database.
        self.assertNumQueries(0, func)

    def test_deletion_cascade_on_non_default_db(self):
        def run():
            base_db1 = RelationA.objects.db_manager("secondary").create(field_a="Base DB1")
            base_db2 = RelationB.objects.db_manager("secondary").create(
                field_b="Base DB2", fk=base_db1
            )

            ContentType.objects.clear_cache()

            RelationBase.objects.db_manager("secondary").filter(pk=base_db2.pk).delete()

            self.assertEqual(RelationB.objects.db_manager("secondary").count(), 0)

        # Ensure no queries are made using the default database.
        self.assertNumQueries(0, run)

    def test_create_from_super(self):
        # run create test 3 times because initial implementation
        # would fail after first success.
        from polymorphic.tests.models import (
            NormalBase,
            NormalExtension,
            PolyExtension,
            PolyExtChild,
        )

        nb = NormalBase.objects.db_manager("secondary").create(nb_field=1)
        ne = NormalExtension.objects.db_manager("secondary").create(nb_field=2, ne_field="ne2")

        with self.assertRaises(TypeError):
            PolyExtension.objects.db_manager("secondary").create_from_super(nb, poly_ext_field=3)

        pe = PolyExtension.objects.db_manager("secondary").create_from_super(ne, poly_ext_field=3)

        ne.refresh_from_db()
        self.assertEqual(type(ne), NormalExtension)
        self.assertEqual(type(pe), PolyExtension)
        self.assertEqual(pe.pk, ne.pk)

        self.assertEqual(pe.nb_field, 2)
        self.assertEqual(pe.ne_field, "ne2")
        self.assertEqual(pe.poly_ext_field, 3)
        pe.refresh_from_db()
        self.assertEqual(pe.nb_field, 2)
        self.assertEqual(pe.ne_field, "ne2")
        self.assertEqual(pe.poly_ext_field, 3)

        pc = PolyExtChild.objects.db_manager("secondary").create_from_super(
            pe, poly_child_field="pcf6"
        )

        pe.refresh_from_db()
        ne.refresh_from_db()
        self.assertEqual(type(ne), NormalExtension)
        self.assertEqual(type(pe), PolyExtension)
        self.assertEqual(pe.pk, ne.pk)
        self.assertEqual(pe.pk, pc.pk)

        self.assertEqual(pc.nb_field, 2)
        self.assertEqual(pc.ne_field, "ne2")
        self.assertEqual(pc.poly_ext_field, 3)
        pc.refresh_from_db()
        self.assertEqual(pc.nb_field, 2)
        self.assertEqual(pc.ne_field, "ne2")
        self.assertEqual(pc.poly_ext_field, 3)
        self.assertEqual(pc.poly_child_field, "pcf6")

        self.assertEqual(
            pe.polymorphic_ctype,
            ContentType.objects.db_manager("secondary").get_for_model(PolyExtChild),
        )
        self.assertEqual(
            pc.polymorphic_ctype,
            ContentType.objects.db_manager("secondary").get_for_model(PolyExtChild),
        )

        self.assertEqual(set(PolyExtension.objects.db_manager("secondary").all()), {pc})

        a1 = Model2A.objects.db_manager("secondary").create(field1="A1a")
        a2 = Model2A.objects.db_manager("secondary").create(field1="A1b")

        b1 = Model2B.objects.db_manager("secondary").create(field1="B1a", field2="B2a")
        b2 = Model2B.objects.db_manager("secondary").create(field1="B1b", field2="B2b")

        c1 = Model2C.objects.db_manager("secondary").create(
            field1="C1a", field2="C2a", field3="C3a"
        )
        c2 = Model2C.objects.db_manager("secondary").create(
            field1="C1b", field2="C2b", field3="C3b"
        )

        d1 = Model2D.objects.db_manager("secondary").create(
            field1="D1a", field2="D2a", field3="D3a", field4="D4a"
        )
        d2 = Model2D.objects.db_manager("secondary").create(
            field1="D1b", field2="D2b", field3="D3b", field4="D4b"
        )

        with self.assertRaises(TypeError):
            Model2D.objects.db_manager("secondary").create_from_super(
                b1, field3="D3x", field4="D4x"
            )

        b1_of_c = Model2B.objects.db_manager("secondary").non_polymorphic().get(pk=c1.pk)
        with self.assertRaises(TypeError):
            Model2C.objects.db_manager("secondary").create_from_super(b1_of_c, field3="C3x")

        self.assertEqual(
            c1.polymorphic_ctype,
            ContentType.objects.db_manager("secondary").get_for_model(Model2C),
        )
        dfs1 = Model2D.objects.db_manager("secondary").create_from_super(b1_of_c, field4="D4x")
        self.assertEqual(type(dfs1), Model2D)
        self.assertEqual(dfs1.pk, c1.pk)
        self.assertEqual(dfs1.field1, "C1a")
        self.assertEqual(dfs1.field2, "C2a")
        self.assertEqual(dfs1.field3, "C3a")
        self.assertEqual(dfs1.field4, "D4x")
        self.assertEqual(
            dfs1.polymorphic_ctype,
            ContentType.objects.db_manager("secondary").get_for_model(Model2D),
        )
        c1.refresh_from_db()
        self.assertEqual(
            c1.polymorphic_ctype,
            ContentType.objects.db_manager("secondary").get_for_model(Model2D),
        )

        self.assertEqual(
            b2.polymorphic_ctype,
            ContentType.objects.db_manager("secondary").get_for_model(Model2B),
        )
        cfs1 = Model2C.objects.db_manager("secondary").create_from_super(b2, field3="C3y")
        self.assertEqual(type(cfs1), Model2C)
        self.assertEqual(cfs1.pk, b2.pk)
        self.assertEqual(cfs1.field1, "B1b")
        self.assertEqual(cfs1.field2, "B2b")
        self.assertEqual(cfs1.field3, "C3y")
        b2.refresh_from_db()
        self.assertEqual(
            b2.polymorphic_ctype,
            ContentType.objects.db_manager("secondary").get_for_model(Model2C),
        )
        self.assertEqual(
            cfs1.polymorphic_ctype,
            ContentType.objects.db_manager("secondary").get_for_model(Model2C),
        )

        self.assertEqual(
            set(Model2A.objects.db_manager("secondary").all()),
            {a1, a2, b1, dfs1, cfs1, c2, d1, d2},
        )

        self.assertEqual(Model2A.objects.count(), 0)

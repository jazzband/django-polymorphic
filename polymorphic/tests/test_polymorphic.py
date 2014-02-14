from django.test import TestCase
from django.db.models import Count, Q, Manager
from django.test.utils import override_settings

from polymorphic import PolymorphicManager


class PolymorphicTests(TestCase):
    """
    The test suite
    """
    def test_diamond_inheritance(self):
        from .models import DiamondXY

        # Django diamond problem
        # https://code.djangoproject.com/ticket/10808
        o1 = DiamondXY.objects.create(field_b='b', field_x='x', field_y='y')
        o2 = DiamondXY.objects.get()

        self.assertNotEqual(o2.field_b, 'b', "Known django model inheritance diamond problem detected\n%s\n%s" % (
            'DiamondXY fields 1: field_b "{0}", field_x "{1}", field_y "{2}"'.format(o1.field_b, o1.field_x, o1.field_y),
            'DiamondXY fields 2: field_b "{0}", field_x "{1}", field_y "{2}"'.format(o2.field_b, o2.field_x, o2.field_y),
        ))

    def test_annotate_aggregate_order(self):
        from .models import BlogA, BlogEntry, BlogB, BlogBase

        # create a blog of type BlogA
        # create two blog entries in BlogA
        # create some blogs of type BlogB to make the BlogBase table data really polymorphic
        blog = BlogA.objects.create(name='B1', info='i1')
        blog.blogentry_set.create(text='bla')
        BlogEntry.objects.create(blog=blog, text='bla2')
        BlogB.objects.create(name='Bb1')
        BlogB.objects.create(name='Bb2')
        BlogB.objects.create(name='Bb3')

        qs = BlogBase.objects.annotate(entrycount=Count('bloga__blogentry'))
        self.assertEqual(len(qs), 4)

        for o in qs:
            if o.name == 'B1':
                self.assertEqual(o.entrycount, 2)
            else:
                self.assertEqual(o.entrycount, 0)

        x = BlogBase.objects.aggregate(entrycount=Count('bloga__blogentry'))
        self.assertEqual(x['entrycount'], 2)

        # create some more blogs for next test
        BlogA.objects.create(name='B2', info='i2')
        BlogA.objects.create(name='B3', info='i3')
        BlogA.objects.create(name='B4', info='i4')
        BlogA.objects.create(name='B5', info='i5')

        # test ordering for field in all entries
        expected = '''[<BlogB: id 4, name (CharField) "Bb3">, <BlogB: id 3, name (CharField) "Bb2">, <BlogB: id 2, name (CharField) "Bb1">, <BlogA: id 8, name (CharField) "B5", info (CharField) "i5">, <BlogA: id 7, name (CharField) "B4", info (CharField) "i4">, <BlogA: id 6, name (CharField) "B3", info (CharField) "i3">, <BlogA: id 5, name (CharField) "B2", info (CharField) "i2">, <BlogA: id 1, name (CharField) "B1", info (CharField) "i1">]'''
        x = repr(BlogBase.objects.order_by('-name'))
        self.assertEqual(x, expected)

        # test ordering for field in one subclass only
        # MySQL and SQLite return this order
        expected1 = '''[<BlogA: id 8, name (CharField) "B5", info (CharField) "i5">, <BlogA: id 7, name (CharField) "B4", info (CharField) "i4">, <BlogA: id 6, name (CharField) "B3", info (CharField) "i3">, <BlogA: id 5, name (CharField) "B2", info (CharField) "i2">, <BlogA: id 1, name (CharField) "B1", info (CharField) "i1">, <BlogB: id 2, name (CharField) "Bb1">, <BlogB: id 3, name (CharField) "Bb2">, <BlogB: id 4, name (CharField) "Bb3">]'''

        # PostgreSQL returns this order
        expected2 = '''[<BlogB: id 2, name (CharField) "Bb1">, <BlogB: id 3, name (CharField) "Bb2">, <BlogB: id 4, name (CharField) "Bb3">, <BlogA: id 8, name (CharField) "B5", info (CharField) "i5">, <BlogA: id 7, name (CharField) "B4", info (CharField) "i4">, <BlogA: id 6, name (CharField) "B3", info (CharField) "i3">, <BlogA: id 5, name (CharField) "B2", info (CharField) "i2">, <BlogA: id 1, name (CharField) "B1", info (CharField) "i1">]'''
        x = repr(BlogBase.objects.order_by('-bloga__info'))
        self.assertTrue(x == expected1 or x == expected2)

    def test_limit_choices_to(self):
        """
        this is not really a testcase, as limit_choices_to only affects the Django admin
        """
        from .models import BlogA, BlogB, BlogEntry_limit_choices_to
        # create a blog of type BlogA
        blog_a = BlogA.objects.create(name='aa', info='aa')
        blog_b = BlogB.objects.create(name='bb')
        # create two blog entries
        entry1 = BlogEntry_limit_choices_to.objects.create(blog=blog_b, text='bla2')
        entry2 = BlogEntry_limit_choices_to.objects.create(blog=blog_b, text='bla2')


    def test_primary_key_custom_field_problem(self):
        """
        object retrieval problem occuring with some custom primary key fields (UUIDField as test case)
        """
        import re
        import uuid
        from .models import UUIDProject, UUIDArtProject, UUIDResearchProject
        UUIDProject.objects.create(topic="John's gathering")
        UUIDArtProject.objects.create(topic="Sculpting with Tim", artist="T. Turner")
        UUIDResearchProject.objects.create(topic="Swallow Aerodynamics", supervisor="Dr. Winter")

        qs = UUIDProject.objects.all()
        ol = list(qs)
        a = qs[0]
        b = qs[1]
        c = qs[2]
        self.assertEqual(len(qs), 3)
        self.assertIsInstance(a.uuid_primary_key, uuid.UUID)
        self.assertIsInstance(a.pk, uuid.UUID)

        res = repr(qs)
        res = re.sub(r' "[^"]*?\.\.", topic', ', topic', res)
        res_exp = '''[<UUIDProject: uuid_primary_key (UUIDField/pk), topic (CharField) "John's gathering">, <UUIDArtProject: uuid_primary_key (UUIDField/pk), topic (CharField) "Sculpting with Tim", artist (CharField) "T. Turner">, <UUIDResearchProject: uuid_primary_key (UUIDField/pk), topic (CharField) "Swallow Aerodynamics", supervisor (CharField) "Dr. Winter">]'''
        self.assertEqual(res, res_exp)

    def test_primary_key_custom_field_problem2(self):
        import uuid
        from .models import UUIDPlainA, UUIDPlainB, UUIDPlainC
        a = UUIDPlainA.objects.create(field1='A1')
        b = UUIDPlainB.objects.create(field1='B1', field2='B2')
        c = UUIDPlainC.objects.create(field1='C1', field2='C2', field3='C3')
        self.assertTrue(
            isinstance(a.pk, uuid.UUID) and
            isinstance(b.pk, uuid.UUID) and
            isinstance(c.pk, uuid.UUID),
            "known type inconstency with custom primary key field detected (django problem?)")

    def create_model2abcd(self):
        """
        Create the chain of objects of Model2,
        this is reused in various tests.
        """
        from .models import Model2A, Model2B, Model2C, Model2D

        Model2A.objects.create(field1='A1')
        Model2B.objects.create(field1='B1', field2='B2')
        Model2C.objects.create(field1='C1', field2='C2', field3='C3')
        Model2D.objects.create(field1='D1', field2='D2', field3='D3', field4='D4')

    def test_simple_inheritance(self):
        from .models import Model2A

        self.create_model2abcd()

        objects = list(Model2A.objects.all())
        self.assertEqual(repr(objects[0]), '<Model2A: id 1, field1 (CharField)>')
        self.assertEqual(repr(objects[1]), '<Model2B: id 2, field1 (CharField), field2 (CharField)>')
        self.assertEqual(repr(objects[2]), '<Model2C: id 3, field1 (CharField), field2 (CharField), field3 (CharField)>')
        self.assertEqual(repr(objects[3]), '<Model2D: id 4, field1 (CharField), field2 (CharField), field3 (CharField), field4 (CharField)>')

    def test_manual_get_real_instance(self):
        from .models import Model2A

        self.create_model2abcd()

        o = Model2A.objects.non_polymorphic().get(field1='C1')
        self.assertEqual(repr(o.get_real_instance()), '<Model2C: id 3, field1 (CharField), field2 (CharField), field3 (CharField)>')

    def test_non_polymorphic(self):
        from .models import Model2A

        self.create_model2abcd()

        objects = list(Model2A.objects.all().non_polymorphic())
        self.assertEqual(repr(objects[0]), '<Model2A: id 1, field1 (CharField)>')
        self.assertEqual(repr(objects[1]), '<Model2A: id 2, field1 (CharField)>')
        self.assertEqual(repr(objects[2]), '<Model2A: id 3, field1 (CharField)>')
        self.assertEqual(repr(objects[3]), '<Model2A: id 4, field1 (CharField)>')

    def test_get_real_instances(self):
        from .models import Model2A

        self.create_model2abcd()

        qs = Model2A.objects.all().non_polymorphic()

        # from queryset
        objects = qs.get_real_instances()
        self.assertEqual(repr(objects[0]), '<Model2A: id 1, field1 (CharField)>')
        self.assertEqual(repr(objects[1]), '<Model2B: id 2, field1 (CharField), field2 (CharField)>')
        self.assertEqual(repr(objects[2]), '<Model2C: id 3, field1 (CharField), field2 (CharField), field3 (CharField)>')
        self.assertEqual(repr(objects[3]), '<Model2D: id 4, field1 (CharField), field2 (CharField), field3 (CharField), field4 (CharField)>')

        # from a manual list
        objects = Model2A.objects.get_real_instances(list(qs))
        self.assertEqual(repr(objects[0]), '<Model2A: id 1, field1 (CharField)>')
        self.assertEqual(repr(objects[1]), '<Model2B: id 2, field1 (CharField), field2 (CharField)>')
        self.assertEqual(repr(objects[2]), '<Model2C: id 3, field1 (CharField), field2 (CharField), field3 (CharField)>')
        self.assertEqual(repr(objects[3]), '<Model2D: id 4, field1 (CharField), field2 (CharField), field3 (CharField), field4 (CharField)>')

    def test_base_manager(self):
        from .models import PlainA, PlainB, PlainC, Model2A, Model2B, Model2C, One2OneRelatingModel, One2OneRelatingModelDerived

        self.assertIs(type(PlainA._base_manager), Manager)
        self.assertIs(type(PlainB._base_manager), Manager)
        self.assertIs(type(PlainC._base_manager), Manager)

        self.assertIs(type(Model2A._base_manager), PolymorphicManager)
        self.assertIs(type(Model2B._base_manager), PolymorphicManager)
        self.assertIs(type(Model2C._base_manager), PolymorphicManager)

        self.assertIs(type(One2OneRelatingModel._base_manager), PolymorphicManager)
        self.assertIs(type(One2OneRelatingModelDerived._base_manager), PolymorphicManager)

    def test_foreignkey_field(self):
        from .models import Model2A, Model2B

        self.create_model2abcd()

        object2a = Model2A.objects.get(field1='C1')
        self.assertEqual(repr(object2a.model2b), '<Model2B: id 3, field1 (CharField), field2 (CharField)>')

        object2b = Model2B.objects.get(field1='C1')
        self.assertEqual(repr(object2b.model2c), '<Model2C: id 3, field1 (CharField), field2 (CharField), field3 (CharField)>')

    def test_onetoone_field(self):
        from .models import Model2A, One2OneRelatingModelDerived

        self.create_model2abcd()

        a = Model2A.objects.get(field1='C1')
        b = One2OneRelatingModelDerived.objects.create(one2one=a, field1='f1', field2='f2')

        self.assertEqual(repr(b.one2one), '<Model2C: id 3, field1 (CharField), field2 (CharField), field3 (CharField)>')

        c = One2OneRelatingModelDerived.objects.get(field1='f1')
        self.assertEqual(repr(c.one2one), '<Model2C: id 3, field1 (CharField), field2 (CharField), field3 (CharField)>')
        self.assertEqual(repr(a.one2onerelatingmodel), '<One2OneRelatingModelDerived: One2OneRelatingModelDerived object>')

    def test_manytomany_field(self):
        from .models import ModelShow1, ModelShow2, ModelShow3, ModelShow1_plain, ModelShow2_plain

        # Model 1
        o = ModelShow1.objects.create(field1='abc')
        o.m2m.add(o)
        o.save()
        self.assertEqual(repr(ModelShow1.objects.all()), '[<ModelShow1: id 1, field1 (CharField), m2m (ManyToManyField)>]')

        # Model 2
        o = ModelShow2.objects.create(field1='abc')
        o.m2m.add(o)
        o.save()
        self.assertEqual(repr(ModelShow2.objects.all()), '[<ModelShow2: id 1, field1 "abc", m2m 1>]')

        # Model 3
        o = ModelShow3.objects.create(field1='abc')
        o.m2m.add(o)
        o.save()
        self.assertEqual(repr(ModelShow3.objects.all()), '[<ModelShow3: id 1, field1 (CharField) "abc", m2m (ManyToManyField) 1>]')
        self.assertEqual(repr([i.m2m__count for i in ModelShow1.objects.all().annotate(Count('m2m'))]), '[1]')
        self.assertEqual(repr([i.m2m__count for i in ModelShow2.objects.all().annotate(Count('m2m'))]), '[1]')
        self.assertEqual(repr([i.m2m__count for i in ModelShow3.objects.all().annotate(Count('m2m'))]), '[1]')

        # no pretty printing
        ModelShow1_plain.objects.create(field1='abc')
        ModelShow2_plain.objects.create(field1='abc', field2='def')
        self.assertEqual(repr(ModelShow1_plain.objects.all()), '[<ModelShow1_plain: ModelShow1_plain object>, <ModelShow2_plain_Deferred_field2: ModelShow2_plain_Deferred_field2 object>]')

    def test_extra_method(self):
        from .models import Model2A, ModelExtraA, ModelExtraB, ModelExtraC, ModelExtraExternal

        self.create_model2abcd()

        objects = list(Model2A.objects.extra(where=['id IN (2, 3)']))
        self.assertEqual(len(objects), 2)
        self.assertEqual(repr(objects[0]), '<Model2B: id 2, field1 (CharField), field2 (CharField)>')
        self.assertEqual(repr(objects[1]), '<Model2C: id 3, field1 (CharField), field2 (CharField), field3 (CharField)>')

        objects = Model2A.objects.extra(select={"select_test": "field1 = 'A1'"}, where=["field1 = 'A1' OR field1 = 'B1'"], order_by=['-id'])
        self.assertEqual(len(objects), 2)
        self.assertEqual(objects[0].select_test, 0)
        self.assertEqual(objects[1].select_test, 1)

        ModelExtraA.objects.create(field1='A1')
        ModelExtraB.objects.create(field1='B1', field2='B2')
        ModelExtraC.objects.create(field1='C1', field2='C2', field3='C3')
        ModelExtraExternal.objects.create(topic='extra1')
        ModelExtraExternal.objects.create(topic='extra2')
        ModelExtraExternal.objects.create(topic='extra3')
        objects = ModelExtraA.objects.extra(tables=["tests_modelextraexternal"], select={"topic": "tests_modelextraexternal.topic"}, where=["tests_modelextraa.id = tests_modelextraexternal.id"])
        self.assertEqual(len(objects), 3)
        self.assertEqual(objects[0].topic, "extra1")
        self.assertEqual(objects[1].topic, "extra2")
        self.assertEqual(objects[2].topic, "extra3")

    def test_instance_of_filter(self):
        from .models import Model2A, Model2B

        self.create_model2abcd()

        objects = Model2A.objects.instance_of(Model2B)
        self.assertEqual(len(objects), 3)
        self.assertEqual(repr(objects[0]), '<Model2B: id 2, field1 (CharField), field2 (CharField)>')
        self.assertEqual(repr(objects[1]), '<Model2C: id 3, field1 (CharField), field2 (CharField), field3 (CharField)>')
        self.assertEqual(repr(objects[2]), '<Model2D: id 4, field1 (CharField), field2 (CharField), field3 (CharField), field4 (CharField)>')

        objects = Model2A.objects.not_instance_of(Model2B)
        self.assertEqual(len(objects), 1)
        self.assertEqual(repr(objects[0]), '<Model2A: id 1, field1 (CharField)>')

    def test_polymorphic___filter(self):
        from .models import Model2A

        self.create_model2abcd()

        objects = Model2A.objects.filter(Q(model2b__field2='B2') | Q(model2b__model2c__field3='C3'))
        self.assertEqual(len(objects), 2)
        self.assertEqual(repr(objects[0]), '<Model2B: id 2, field1 (CharField), field2 (CharField)>')
        self.assertEqual(repr(objects[1]), '<Model2C: id 3, field1 (CharField), field2 (CharField), field3 (CharField)>')

    def test_delete(self):
        from .models import Model2A

        self.create_model2abcd()

        self.assertEqual(Model2A.objects.count(), 4)

        oa = Model2A.objects.get(id=2)
        self.assertEqual(repr(oa), '<Model2B: id 2, field1 (CharField), field2 (CharField)>')

        oa.delete()
        objects = Model2A.objects.all()
        self.assertEqual(len(objects), 3)
        self.assertEqual(repr(objects[0]), '<Model2A: id 1, field1 (CharField)>')
        self.assertEqual(repr(objects[1]), '<Model2C: id 3, field1 (CharField), field2 (CharField), field3 (CharField)>')
        self.assertEqual(repr(objects[2]), '<Model2D: id 4, field1 (CharField), field2 (CharField), field3 (CharField), field4 (CharField)>')

    def test_combine_querysets(self):
        from .models import Base, ModelX, ModelY
        ModelX.objects.create(field_x='x')
        ModelY.objects.create(field_y='y')

        qs = Base.objects.instance_of(ModelX) | Base.objects.instance_of(ModelY)
        self.assertEqual(len(qs), 2)
        self.assertEqual(repr(qs[0]), '<ModelX: id 1, field_b (CharField), field_x (CharField)>')
        self.assertEqual(repr(qs[1]), '<ModelY: id 2, field_b (CharField), field_y (CharField)>')

    def test_multiple_inheritance(self):
        from .models import Enhance_Base, Enhance_Inherit
        # multiple inheritance, subclassing third party models (mix PolymorphicModel with models.Model)

        Enhance_Base.objects.create(field_b='b-base')
        Enhance_Inherit.objects.create(field_b='b-inherit', field_p='p', field_i='i')

        qs = Enhance_Base.objects.all()
        self.assertEqual(len(qs), 2)
        self.assertEqual(repr(qs[0]), '<Enhance_Base: id 1, field_b (CharField) "b-base">')
        self.assertEqual(repr(qs[1]), '<Enhance_Inherit: id 2, field_b (CharField) "b-inherit", field_p (CharField) "p", field_i (CharField) "i">')

    def create_relationbaseabc(self):
        from .models import RelationBase, RelationA, RelationB, RelationBC
        # ForeignKey, ManyToManyField
        obase = RelationBase.objects.create(field_base='base')
        oa = RelationA.objects.create(field_base='A1', field_a='A2', fk=obase)
        ob = RelationB.objects.create(field_base='B1', field_b='B2', fk=oa)
        oc = RelationBC.objects.create(field_base='C1', field_b='C2', field_c='C3', fk=oa)
        oa.m2m.add(oa)
        oa.m2m.add(ob)

    def test_relation_base(self):
        from .models import RelationBase, RelationA

        self.create_relationbaseabc()

        objects = RelationBase.objects.all()
        self.assertEqual(len(objects), 4)
        self.assertEqual(repr(objects[0]), '<RelationBase: id 1, field_base (CharField) "base", fk (ForeignKey) None, m2m (ManyToManyField) 0>')
        self.assertEqual(repr(objects[1]), '<RelationA: id 2, field_base (CharField) "A1", fk (ForeignKey) RelationBase, field_a (CharField) "A2", m2m (ManyToManyField) 2>')
        self.assertEqual(repr(objects[2]), '<RelationB: id 3, field_base (CharField) "B1", fk (ForeignKey) RelationA, field_b (CharField) "B2", m2m (ManyToManyField) 1>')
        self.assertEqual(repr(objects[3]), '<RelationBC: id 4, field_base (CharField) "C1", fk (ForeignKey) RelationA, field_b (CharField) "C2", field_c (CharField) "C3", m2m (ManyToManyField) 0>')

        oa = RelationBase.objects.get(id=2)
        self.assertEqual(repr(oa.fk), '<RelationBase: id 1, field_base (CharField) "base", fk (ForeignKey) None, m2m (ManyToManyField) 0>')

        objects = oa.relationbase_set.all()
        self.assertEqual(len(objects), 2)
        self.assertEqual(repr(objects[0]), '<RelationB: id 3, field_base (CharField) "B1", fk (ForeignKey) RelationA, field_b (CharField) "B2", m2m (ManyToManyField) 1>')
        self.assertEqual(repr(objects[1]), '<RelationBC: id 4, field_base (CharField) "C1", fk (ForeignKey) RelationA, field_b (CharField) "C2", field_c (CharField) "C3", m2m (ManyToManyField) 0>')

        ob = RelationBase.objects.get(id=3)
        self.assertEqual(repr(ob.fk), '<RelationA: id 2, field_base (CharField) "A1", fk (ForeignKey) RelationBase, field_a (CharField) "A2", m2m (ManyToManyField) 2>')

        oa = RelationA.objects.get()
        objects = oa.m2m.all()
        self.assertEqual(len(objects), 2)
        self.assertEqual(repr(objects[0]), '<RelationA: id 2, field_base (CharField) "A1", fk (ForeignKey) RelationBase, field_a (CharField) "A2", m2m (ManyToManyField) 2>')
        self.assertEqual(repr(objects[1]), '<RelationB: id 3, field_base (CharField) "B1", fk (ForeignKey) RelationA, field_b (CharField) "B2", m2m (ManyToManyField) 1>')

    @override_settings(DEBUG=True)
    def test_relation_base_select_related(self):
        from django.db import connection, reset_queries
        from .models import RelationBase

        self.create_relationbaseabc()

        reset_queries()
        oa = RelationBase.objects.select_related('fk').get(id=2)
        self.assertEqual(oa.fk.field_base, "base")
        queries = len(connection.queries)
        self.assertEqual(queries, 1)

        reset_queries()
        oa = RelationBase.objects.get(id=2)
        self.assertEqual(oa.fk.field_base, "base")
        queries = len(connection.queries)
        self.assertEqual(queries, 2)

    def test_user_defined_manager(self):
        from .models import ModelWithMyManager, MyManager

        self.create_model2abcd()

        ModelWithMyManager.objects.create(field1='D1a', field4='D4a')
        ModelWithMyManager.objects.create(field1='D1b', field4='D4b')

        objects = ModelWithMyManager.objects.all()   # MyManager should reverse the sorting of field1
        self.assertEqual(len(objects), 2)
        self.assertEqual(repr(objects[0]), '<ModelWithMyManager: id 6, field1 (CharField) "D1b", field4 (CharField) "D4b">')
        self.assertEqual(repr(objects[1]), '<ModelWithMyManager: id 5, field1 (CharField) "D1a", field4 (CharField) "D4a">')

        self.assertIs(type(ModelWithMyManager.objects), MyManager)
        self.assertIs(type(ModelWithMyManager._default_manager), MyManager)

    def test_queryset_assignment(self):
        from .models import PlainParentModelWithManager, PlainChildModelWithManager, PlainMyManager, PlainMyManagerQuerySet

        # This is just a consistency check for now, testing standard Django behavior.
        parent = PlainParentModelWithManager.objects.create()
        child = PlainChildModelWithManager.objects.create(fk=parent)
        self.assertIs(type(PlainParentModelWithManager._default_manager), Manager)
        self.assertIs(type(PlainChildModelWithManager._default_manager), PlainMyManager)
        self.assertIs(type(PlainChildModelWithManager.objects), PlainMyManager)
        self.assertIs(type(PlainChildModelWithManager.objects.all()), PlainMyManagerQuerySet)

        # A related set is created using the model's _default_manager, so does gain extra methods.
        self.assertIs(type(parent.childmodel_set.my_queryset_foo()), PlainMyManagerQuerySet)

    def test_plain_manager_inheritance(self):
        from .models import MROPlainDerived, MROPlainBase1, MROPlainBase2, PlainMyManager
        # check for correct default manager
        self.assertIs(type(MROPlainBase1._default_manager), PlainMyManager)

        # Django vanilla inheritance does not inherit PlainMyManager as _default_manager here
        self.assertIs(type(MROPlainBase2._default_manager), Manager)

        # by choice of MRO, should be PlainMyManager from MROPlainBase1.
        self.assertIs(type(MROPlainDerived._default_manager), Manager)

    def test_manager_inheritance(self):
        from .models import MRODerived, MROBase1, MROBase2, MyManager
        # check for correct default manager
        self.assertIs(type(MROBase1._default_manager), MyManager)

        # Django vanilla inheritance does not inherit MyManager as _default_manager here
        self.assertIs(type(MROBase2._default_manager), MyManager)

        # by choice of MRO, should be MyManager from MROBase1.
        self.assertIs(type(MRODerived._default_manager), MyManager)

    def test_queryset_assignment2(self):
        from .models import ParentModelWithManager, ChildModelWithManager, PolymorphicManager, MyManager, MyManagerQuerySet

        # For polymorphic models, the same should happen.
        parent = ParentModelWithManager.objects.create()
        child = ChildModelWithManager.objects.create(fk=parent)
        self.assertIs(type(ParentModelWithManager._default_manager), PolymorphicManager)
        self.assertIs(type(ChildModelWithManager._default_manager), MyManager)
        self.assertIs(type(ChildModelWithManager.objects), MyManager)
        self.assertIs(type(ChildModelWithManager.objects.my_queryset_foo()), MyManagerQuerySet)

        # A related set is created using the model's _default_manager, so does gain extra methods.
        self.assertIs(type(parent.childmodel_set.my_queryset_foo()), MyManagerQuerySet)

    def test_proxy_models(self):
        from .models import ProxyBase, ProxyChild
        # prepare some data
        for data in ('bleep bloop', 'I am a', 'computer'):
            ProxyChild.objects.create(some_data=data)

        # this caches ContentType queries so they don't interfere with our query counts later
        list(ProxyBase.objects.all())

        # one query per concrete class
        with self.assertNumQueries(1):
            items = list(ProxyBase.objects.all())

        self.assertIsInstance(items[0], ProxyChild)

    def test_content_types_for_proxy_models(self):
        """Checks if ContentType is capable of returning proxy models."""
        from django.contrib.contenttypes.models import ContentType
        from .models import ProxyChild

        ct = ContentType.objects.get_for_model(ProxyChild, for_concrete_model=False)
        self.assertEqual(ProxyChild, ct.model_class())

    def test_proxy_model_inheritance(self):
        """
        Polymorphic abilities should also work when the base model is a proxy object.
        """
        from .models import ProxiedBase, ProxyModelBase, ProxyModelA, ProxyModelB

        # The managers should point to the proper objects.
        # otherwise, the whole excersise is pointless.
        self.assertEqual(ProxiedBase.objects.model, ProxiedBase)
        self.assertEqual(ProxyModelBase.objects.model, ProxyModelBase)
        self.assertEqual(ProxyModelA.objects.model, ProxyModelA)
        self.assertEqual(ProxyModelB.objects.model, ProxyModelB)

        # Create objects
        ProxyModelA.objects.create(name="object1")
        ProxyModelB.objects.create(name="object2", field2="bb")

        # Getting single objects
        object1 = ProxyModelBase.objects.get(name='object1')
        object2 = ProxyModelBase.objects.get(name='object2')
        self.assertEqual(repr(object1), '<ProxyModelA: id 1, name (CharField) "object1", field1 (CharField) "">')
        self.assertEqual(repr(object2), '<ProxyModelB: id 2, name (CharField) "object2", field2 (CharField) "bb">')
        self.assertIsInstance(object1, ProxyModelA)
        self.assertIsInstance(object2, ProxyModelB)

        # Same for lists
        objects = list(ProxyModelBase.objects.all().order_by('name'))
        self.assertEqual(repr(objects[0]), '<ProxyModelA: id 1, name (CharField) "object1", field1 (CharField) "">')
        self.assertEqual(repr(objects[1]), '<ProxyModelB: id 2, name (CharField) "object2", field2 (CharField) "bb">')
        self.assertIsInstance(objects[0], ProxyModelA)
        self.assertIsInstance(objects[1], ProxyModelB)

    def test_fix_getattribute(self):
        from .models import ModelFieldNameTest, InitTestModelSubclass

        ### fixed issue in PolymorphicModel.__getattribute__: field name same as model name
        o = ModelFieldNameTest.objects.create(modelfieldnametest='1')
        self.assertEqual(repr(o), '<ModelFieldNameTest: id 1, modelfieldnametest (CharField)>')

        # if subclass defined __init__ and accessed class members,
        # __getattribute__ had a problem: "...has no attribute 'sub_and_superclass_dict'"
        o = InitTestModelSubclass.objects.create()
        self.assertEqual(o.bar, 'XYZ')


class RegressionTests(TestCase):
    def test_for_query_result_incomplete_with_inheritance(self):
        """ https://github.com/bconstantin/django_polymorphic/issues/15 """
        from .models import Top, Middle, Bottom

        top = Top()
        top.save()
        middle = Middle()
        middle.save()
        bottom = Bottom()
        bottom.save()

        expected_queryset = [top, middle, bottom]
        self.assertQuerysetEqual(Top.objects.all(), [repr(r) for r in expected_queryset])

        expected_queryset = [middle, bottom]
        self.assertQuerysetEqual(Middle.objects.all(), [repr(r) for r in expected_queryset])

        expected_queryset = [bottom]
        self.assertQuerysetEqual(Bottom.objects.all(), [repr(r) for r in expected_queryset])

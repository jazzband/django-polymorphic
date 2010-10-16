# -*- coding: utf-8 -*-
""" Test Cases
    Please see README.rst or DOCS.rst or http://bserve.webhop.org/wiki/django_polymorphic
"""

import settings

from django.test import TestCase
from django.db.models.query import QuerySet
from django.db.models import Q,Count
from django.db import models
from django.contrib.contenttypes.models import ContentType
from pprint import pprint

from polymorphic import PolymorphicModel, PolymorphicManager, PolymorphicQuerySet, ShowFieldContent, ShowFieldType, ShowFieldTypeAndContent, get_version

class PlainA(models.Model):
    field1 = models.CharField(max_length=10)
class PlainB(PlainA):
    field2 = models.CharField(max_length=10)
class PlainC(PlainB):
    field3 = models.CharField(max_length=10)

class Model2A(ShowFieldType, PolymorphicModel):
    field1 = models.CharField(max_length=10)
class Model2B(Model2A):
    field2 = models.CharField(max_length=10)
class Model2C(Model2B):
    field3 = models.CharField(max_length=10)

class ModelShow1(ShowFieldType,PolymorphicModel):
    field1 = models.CharField(max_length=10)
    m2m = models.ManyToManyField('self')
class ModelShow2(ShowFieldContent, PolymorphicModel):
    field1 = models.CharField(max_length=10)
    m2m = models.ManyToManyField('self')
class ModelShow3(ShowFieldTypeAndContent, PolymorphicModel):
    field1 = models.CharField(max_length=10)
    m2m = models.ManyToManyField('self')

class Base(ShowFieldType, PolymorphicModel):
    field_b = models.CharField(max_length=10)
class ModelX(Base):
    field_x = models.CharField(max_length=10)
class ModelY(Base):
    field_y = models.CharField(max_length=10)

class Enhance_Plain(models.Model):
    field_p = models.CharField(max_length=10)
class Enhance_Base(ShowFieldTypeAndContent, PolymorphicModel):
    field_b = models.CharField(max_length=10)
class Enhance_Inherit(Enhance_Base, Enhance_Plain):
    field_i = models.CharField(max_length=10)
        
    
class DiamondBase(models.Model):
    field_b = models.CharField(max_length=10)
class DiamondX(DiamondBase):
    field_x = models.CharField(max_length=10)
class DiamondY(DiamondBase):
    field_y = models.CharField(max_length=10)
class DiamondXY(DiamondX, DiamondY):
    pass

class RelationBase(ShowFieldTypeAndContent, PolymorphicModel):
    field_base = models.CharField(max_length=10)
    fk = models.ForeignKey('self', null=True)
    m2m = models.ManyToManyField('self')
class RelationA(RelationBase):
    field_a = models.CharField(max_length=10)
class RelationB(RelationBase):
    field_b = models.CharField(max_length=10)
class RelationBC(RelationB):
    field_c = models.CharField(max_length=10)

class RelatingModel(models.Model):
    many2many = models.ManyToManyField(Model2A)

class MyManager(PolymorphicManager):
    def get_query_set(self):
        return super(MyManager, self).get_query_set().order_by('-field1')
class ModelWithMyManager(ShowFieldTypeAndContent, Model2A):
    objects = MyManager()
    field4 = models.CharField(max_length=10)

class MROBase1(ShowFieldType, PolymorphicModel):
    objects = MyManager()
    field1 = models.CharField(max_length=10) # needed as MyManager uses it
class MROBase2(MROBase1):  
    pass # Django vanilla inheritance does not inherit MyManager as _default_manager here
class MROBase3(models.Model):
    objects = PolymorphicManager()
class MRODerived(MROBase2, MROBase3):  
    pass

class MgrInheritA(models.Model):
    mgrA = models.Manager()
    mgrA2 = models.Manager()
    field1 = models.CharField(max_length=10)
class MgrInheritB(MgrInheritA):  
    mgrB = models.Manager()
    field2 = models.CharField(max_length=10)
class MgrInheritC(ShowFieldTypeAndContent, MgrInheritB):
    pass

class BlogBase(ShowFieldTypeAndContent, PolymorphicModel):
    name = models.CharField(max_length=10)
class BlogA(BlogBase):
    info = models.CharField(max_length=10)
class BlogB(BlogBase):
    pass
class BlogEntry(ShowFieldTypeAndContent, PolymorphicModel):
    blog = models.ForeignKey(BlogA)
    text = models.CharField(max_length=10)

class ModelFieldNameTest(ShowFieldType, PolymorphicModel):
    modelfieldnametest = models.CharField(max_length=10)

class InitTestModel(ShowFieldType, PolymorphicModel):
    bar = models.CharField(max_length=100)
    def __init__(self, *args, **kwargs):
        kwargs['bar'] = self.x()
        super(InitTestModel, self).__init__(*args, **kwargs)
class InitTestModelSubclass(InitTestModel):
    def x(self):
        return 'XYZ'

# test bad field name
#class TestBadFieldModel(ShowFieldType, PolymorphicModel):
#    instance_of = models.CharField(max_length=10)

# validation error: "polymorphic.relatednameclash: Accessor for field 'polymorphic_ctype' clashes
# with related field 'ContentType.relatednameclash_set'." (reported by Andrew Ingram)
# fixed with related_name
class RelatedNameClash(ShowFieldType, PolymorphicModel):
    ctype = models.ForeignKey(ContentType, null=True, editable=False)        


class testclass(TestCase):
    def test_diamond_inheritance(self):    
        # Django diamond problem
        o = DiamondXY.objects.create(field_b='b', field_x='x', field_y='y')
        print 'DiamondXY fields 1: field_b "%s", field_x "%s", field_y "%s"' % (o.field_b, o.field_x, o.field_y)
        o = DiamondXY.objects.get()
        print 'DiamondXY fields 2: field_b "%s", field_x "%s", field_y "%s"' % (o.field_b, o.field_x, o.field_y)
        if o.field_b != 'b': print '# Django model inheritance diamond problem detected'

    def test_annotate_aggregate_order(self):

        # create a blog of type BlogA
        blog = BlogA.objects.create(name='B1', info='i1')
        # create two blog entries in BlogA
        entry1 = blog.blogentry_set.create(text='bla')
        entry2 = BlogEntry.objects.create(blog=blog, text='bla2')

        # create some blogs of type BlogB to make the BlogBase table data really polymorphic
        o = BlogB.objects.create(name='Bb1')
        o = BlogB.objects.create(name='Bb2')
        o = BlogB.objects.create(name='Bb3')

        qs = BlogBase.objects.annotate(entrycount=Count('BlogA___blogentry'))

        assert len(qs)==4

        for o in qs:
            if o.name=='B1':
                assert o.entrycount == 2
            else:
                assert o.entrycount == 0
            
        x = BlogBase.objects.aggregate(entrycount=Count('BlogA___blogentry'))
        assert x['entrycount'] == 2

        # create some more blogs for next test
        b2 = BlogA.objects.create(name='B2', info='i2')
        b2 = BlogA.objects.create(name='B3', info='i3')
        b2 = BlogA.objects.create(name='B4', info='i4')
        b2 = BlogA.objects.create(name='B5', info='i5')

        ### test ordering for field in all entries

        expected = '''
[ <BlogB: id 4, name (CharField): "Bb3">,
  <BlogB: id 3, name (CharField): "Bb2">,
  <BlogB: id 2, name (CharField): "Bb1">,
  <BlogA: id 8, name (CharField): "B5", info (CharField): "i5">,
  <BlogA: id 7, name (CharField): "B4", info (CharField): "i4">,
  <BlogA: id 6, name (CharField): "B3", info (CharField): "i3">,
  <BlogA: id 5, name (CharField): "B2", info (CharField): "i2">,
  <BlogA: id 1, name (CharField): "B1", info (CharField): "i1"> ]'''
        x = '\n' + repr(BlogBase.objects.order_by('-name'))
        assert x == expected

        ### test ordering for field in one subclass only

        # MySQL and SQLite return this order
        expected1='''
[ <BlogA: id 8, name (CharField): "B5", info (CharField): "i5">,
  <BlogA: id 7, name (CharField): "B4", info (CharField): "i4">,
  <BlogA: id 6, name (CharField): "B3", info (CharField): "i3">,
  <BlogA: id 5, name (CharField): "B2", info (CharField): "i2">,
  <BlogA: id 1, name (CharField): "B1", info (CharField): "i1">,
  <BlogB: id 2, name (CharField): "Bb1">,
  <BlogB: id 3, name (CharField): "Bb2">,
  <BlogB: id 4, name (CharField): "Bb3"> ]'''

        # PostgreSQL returns this order
        expected2='''
[ <BlogB: id 2, name (CharField): "Bb1">,
  <BlogB: id 3, name (CharField): "Bb2">,
  <BlogB: id 4, name (CharField): "Bb3">,
  <BlogA: id 8, name (CharField): "B5", info (CharField): "i5">,
  <BlogA: id 7, name (CharField): "B4", info (CharField): "i4">,
  <BlogA: id 6, name (CharField): "B3", info (CharField): "i3">,
  <BlogA: id 5, name (CharField): "B2", info (CharField): "i2">,
  <BlogA: id 1, name (CharField): "B1", info (CharField): "i1"> ]'''

        x = '\n' + repr(BlogBase.objects.order_by('-BlogA___info'))
        assert x == expected1 or x == expected2

        #assert False

        
__test__ = {"doctest": """
#######################################################
### Tests

>>> settings.DEBUG=True

>>> get_version()
'0.5 beta'


### simple inheritance

>>> o=Model2A.objects.create(field1='A1')
>>> o=Model2B.objects.create(field1='B1', field2='B2')
>>> o=Model2C.objects.create(field1='C1', field2='C2', field3='C3')

>>> Model2A.objects.all()
[ <Model2A: id 1, field1 (CharField)>,
  <Model2B: id 2, field1 (CharField), field2 (CharField)>,
  <Model2C: id 3, field1 (CharField), field2 (CharField), field3 (CharField)> ]

# manual get_real_instance()
>>> o=Model2A.base_objects.get(field1='C1')
>>> o.get_real_instance()
<Model2C: id 3, field1 (CharField), field2 (CharField), field3 (CharField)>


### ShowFieldContent, ShowFieldType, ShowFieldTypeAndContent, also with annotate()

>>> o=ModelShow1.objects.create(field1='abc')
>>> o.m2m.add(o) ; o.save()
>>> ModelShow1.objects.all()
[ <ModelShow1: id 1, field1 (CharField), m2m (ManyToManyField)> ]

>>> o=ModelShow2.objects.create(field1='abc')
>>> o.m2m.add(o) ; o.save()
>>> ModelShow2.objects.all()
[ <ModelShow2: id 1, field1: "abc", m2m: 1> ]

>>> o=ModelShow3.objects.create(field1='abc')
>>> o.m2m.add(o) ; o.save()
>>> ModelShow3.objects.all()
[ <ModelShow3: id 1, field1 (CharField): "abc", m2m (ManyToManyField): 1> ]

>>> ModelShow1.objects.all().annotate(Count('m2m'))
[ <ModelShow1: id 1, field1 (CharField), m2m (ManyToManyField) - Ann: m2m__count (int)> ]
>>> ModelShow2.objects.all().annotate(Count('m2m'))
[ <ModelShow2: id 1, field1: "abc", m2m: 1 - Ann: m2m__count: "1"> ]
>>> ModelShow3.objects.all().annotate(Count('m2m'))
[ <ModelShow3: id 1, field1 (CharField): "abc", m2m (ManyToManyField): 1 - Ann: m2m__count (int): "1"> ]
 

### extra() method

>>> Model2A.objects.extra(where=['id IN (2, 3)'])
[ <Model2A: id 2, field1 (CharField)>,
  <Model2A: id 3, field1 (CharField)> ]

>>> Model2A.objects.extra(polymorphic=True, where=['id IN (2, 3)'])
[ <Model2B: id 2, field1 (CharField), field2 (CharField)>,
  <Model2C: id 3, field1 (CharField), field2 (CharField), field3 (CharField)> ]


### class filtering, instance_of, not_instance_of

>>> Model2A.objects.instance_of(Model2B)
[ <Model2B: id 2, field1 (CharField), field2 (CharField)>,
  <Model2C: id 3, field1 (CharField), field2 (CharField), field3 (CharField)> ]

>>> Model2A.objects.filter(instance_of=Model2B)
[ <Model2B: id 2, field1 (CharField), field2 (CharField)>,
  <Model2C: id 3, field1 (CharField), field2 (CharField), field3 (CharField)> ]

>>> Model2A.objects.filter(Q(instance_of=Model2B))
[ <Model2B: id 2, field1 (CharField), field2 (CharField)>,
  <Model2C: id 3, field1 (CharField), field2 (CharField), field3 (CharField)> ]

>>> Model2A.objects.not_instance_of(Model2B)
[ <Model2A: id 1, field1 (CharField)> ]


### polymorphic filtering

>>> Model2A.objects.filter(  Q( Model2B___field2 = 'B2' )  |  Q( Model2C___field3 = 'C3' )  )
[ <Model2B: id 2, field1 (CharField), field2 (CharField)>,
  <Model2C: id 3, field1 (CharField), field2 (CharField), field3 (CharField)> ]


### get & delete

>>> oa=Model2A.objects.get(id=2)
>>> oa
<Model2B: id 2, field1 (CharField), field2 (CharField)>

>>> oa.delete()
>>> Model2A.objects.all()
[ <Model2A: id 1, field1 (CharField)>,
  <Model2C: id 3, field1 (CharField), field2 (CharField), field3 (CharField)> ]


### queryset combining

>>> o=ModelX.objects.create(field_x='x')
>>> o=ModelY.objects.create(field_y='y')

>>> Base.objects.instance_of(ModelX) | Base.objects.instance_of(ModelY)
[ <ModelX: id 1, field_b (CharField), field_x (CharField)>,
  <ModelY: id 2, field_b (CharField), field_y (CharField)> ]


### multiple inheritance, subclassing third party models (mix PolymorphicModel with models.Model)

>>> o = Enhance_Base.objects.create(field_b='b-base')
>>> o = Enhance_Inherit.objects.create(field_b='b-inherit', field_p='p', field_i='i')

>>> Enhance_Base.objects.all()
[ <Enhance_Base: id 1, field_b (CharField): "b-base">,
  <Enhance_Inherit: id 2, field_b (CharField): "b-inherit", field_p (CharField): "p", field_i (CharField): "i"> ]


### ForeignKey, ManyToManyField

>>> obase=RelationBase.objects.create(field_base='base')
>>> oa=RelationA.objects.create(field_base='A1', field_a='A2', fk=obase)
>>> ob=RelationB.objects.create(field_base='B1', field_b='B2', fk=oa)
>>> oc=RelationBC.objects.create(field_base='C1', field_b='C2', field_c='C3', fk=oa)
>>> oa.m2m.add(oa); oa.m2m.add(ob)

>>> RelationBase.objects.all()
[ <RelationBase: id 1, field_base (CharField): "base", fk (ForeignKey): "None", m2m (ManyToManyField): 0>,
  <RelationA: id 2, field_base (CharField): "A1", fk (ForeignKey): "RelationBase", field_a (CharField): "A2", m2m (ManyToManyField): 2>,
  <RelationB: id 3, field_base (CharField): "B1", fk (ForeignKey): "RelationA", field_b (CharField): "B2", m2m (ManyToManyField): 1>,
  <RelationBC: id 4, field_base (CharField): "C1", fk (ForeignKey): "RelationA", field_b (CharField): "C2", field_c (CharField): "C3", m2m (ManyToManyField): 0> ]
      
>>> oa=RelationBase.objects.get(id=2)
>>> oa.fk
<RelationBase: id 1, field_base (CharField): "base", fk (ForeignKey): "None", m2m (ManyToManyField): 0>

>>> oa.relationbase_set.all()
[ <RelationB: id 3, field_base (CharField): "B1", fk (ForeignKey): "RelationA", field_b (CharField): "B2", m2m (ManyToManyField): 1>,
  <RelationBC: id 4, field_base (CharField): "C1", fk (ForeignKey): "RelationA", field_b (CharField): "C2", field_c (CharField): "C3", m2m (ManyToManyField): 0> ]

>>> ob=RelationBase.objects.get(id=3)
>>> ob.fk
<RelationA: id 2, field_base (CharField): "A1", fk (ForeignKey): "RelationBase", field_a (CharField): "A2", m2m (ManyToManyField): 2>

>>> oa=RelationA.objects.get()
>>> oa.m2m.all()
[ <RelationA: id 2, field_base (CharField): "A1", fk (ForeignKey): "RelationBase", field_a (CharField): "A2", m2m (ManyToManyField): 2>,
  <RelationB: id 3, field_base (CharField): "B1", fk (ForeignKey): "RelationA", field_b (CharField): "B2", m2m (ManyToManyField): 1> ]

### user-defined manager

>>> o=ModelWithMyManager.objects.create(field1='D1a', field4='D4a')
>>> o=ModelWithMyManager.objects.create(field1='D1b', field4='D4b')

>>> ModelWithMyManager.objects.all()
[ <ModelWithMyManager: id 5, field1 (CharField): "D1b", field4 (CharField): "D4b">,
  <ModelWithMyManager: id 4, field1 (CharField): "D1a", field4 (CharField): "D4a"> ]

>>> type(ModelWithMyManager.objects)
<class 'polymorphic.tests.MyManager'>
>>> type(ModelWithMyManager._default_manager)
<class 'polymorphic.tests.MyManager'>


### Manager Inheritance

>>> type(MRODerived.objects) # MRO
<class 'polymorphic.tests.MyManager'>

# check for correct default manager
>>> type(MROBase1._default_manager)
<class 'polymorphic.tests.MyManager'>
 
# Django vanilla inheritance does not inherit MyManager as _default_manager here
>>> type(MROBase2._default_manager)
<class 'polymorphic.tests.MyManager'>


### fixed issue in PolymorphicModel.__getattribute__: field name same as model name
>>> ModelFieldNameTest.objects.create(modelfieldnametest='1')
<ModelFieldNameTest: id 1, modelfieldnametest (CharField)>


### fixed issue in PolymorphicModel.__getattribute__:
# if subclass defined __init__ and accessed class members, __getattribute__ had a problem: "...has no attribute 'sub_and_superclass_dict'"
#>>> o
>>> o = InitTestModelSubclass.objects.create()
>>> o.bar
'XYZ'


### Django model inheritance diamond problem, fails for Django 1.1

#>>> o=DiamondXY.objects.create(field_b='b', field_x='x', field_y='y')
#>>> print 'DiamondXY fields 1: field_b "%s", field_x "%s", field_y "%s"' % (o.field_b, o.field_x, o.field_y)
#DiamondXY fields 1: field_b "a", field_x "x", field_y "y"


>>> settings.DEBUG=False

"""}
        

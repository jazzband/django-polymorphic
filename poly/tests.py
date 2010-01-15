# -*- coding: utf-8 -*-
#disabletests = 1
"""
#######################################################
### Tests

>>> settings.DEBUG=True

### simple inheritance

>>> o=ModelA.objects.create(field1='A1')
>>> o=ModelB.objects.create(field1='B1', field2='B2')
>>> o=ModelC.objects.create(field1='C1', field2='C2', field3='C3')

>>> ModelA.objects.all()
[ <ModelA: id 1, field1 (CharField)>,
  <ModelB: id 2, field1 (CharField), field2 (CharField)>,
  <ModelC: id 3, field1 (CharField), field2 (CharField), field3 (CharField)> ]

### class filtering, instance_of, not_instance_of

>>> ModelA.objects.instance_of(ModelB)
[ <ModelB: id 2, field1 (CharField), field2 (CharField)>,
  <ModelC: id 3, field1 (CharField), field2 (CharField), field3 (CharField)> ]

>>> ModelA.objects.not_instance_of(ModelB)
[ <ModelA: id 1, field1 (CharField)> ]

### polymorphic filtering

>>> ModelA.objects.filter(  Q( ModelB___field2 = 'B2' )  |  Q( ModelC___field3 = 'C3' )  )
[ <ModelB: id 2, field1 (CharField), field2 (CharField)>,
  <ModelC: id 3, field1 (CharField), field2 (CharField), field3 (CharField)> ]

### get & delete

>>> oa=ModelA.objects.get(id=2)
>>> oa
<ModelB: id 2, field1 (CharField), field2 (CharField)>

>>> oa.delete()
>>> ModelA.objects.all()
[ <ModelA: id 1, field1 (CharField)>,
  <ModelC: id 3, field1 (CharField), field2 (CharField), field3 (CharField)> ]

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
[ <RelationBase: id 1, field_base (CharField): "base", fk (ForeignKey): "None">,
  <RelationA: id 2, field_base (CharField): "A1", fk (ForeignKey): "RelationBase", field_a (CharField): "A2">,
  <RelationB: id 3, field_base (CharField): "B1", fk (ForeignKey): "RelationA", field_b (CharField): "B2">,
  <RelationBC: id 4, field_base (CharField): "C1", fk (ForeignKey): "RelationA", field_b (CharField): "C2", field_c (CharField): "C3"> ]
      
>>> oa=RelationBase.objects.get(id=2)
>>> oa.fk
<RelationBase: id 1, field_base (CharField): "base", fk (ForeignKey): "None">

>>> oa.relationbase_set.all()
[ <RelationB: id 3, field_base (CharField): "B1", fk (ForeignKey): "RelationA", field_b (CharField): "B2">,
  <RelationBC: id 4, field_base (CharField): "C1", fk (ForeignKey): "RelationA", field_b (CharField): "C2", field_c (CharField): "C3"> ]

>>> ob=RelationBase.objects.get(id=3)
>>> ob.fk
<RelationA: id 2, field_base (CharField): "A1", fk (ForeignKey): "RelationBase", field_a (CharField): "A2">

>>> oa=RelationA.objects.get()
>>> oa.m2m.all()
[ <RelationA: id 2, field_base (CharField): "A1", fk (ForeignKey): "RelationBase", field_a (CharField): "A2">,
  <RelationB: id 3, field_base (CharField): "B1", fk (ForeignKey): "RelationA", field_b (CharField): "B2"> ]

### user-defined manager

>>> o=ModelWithMyManager.objects.create(field1='D1a', field4='D4a')
>>> o=ModelWithMyManager.objects.create(field1='D1b', field4='D4b')

>>> ModelWithMyManager.objects.all()
[ <ModelWithMyManager: id 5, field1 (CharField): "D1b", field4 (CharField): "D4b">,
  <ModelWithMyManager: id 4, field1 (CharField): "D1a", field4 (CharField): "D4a"> ]

>>> type(ModelWithMyManager.objects)
<class 'poly.models.MyManager'>
>>> type(ModelWithMyManager._default_manager)
<class 'poly.models.MyManager'>

### Manager Inheritance

>>> type(MRODerived.objects) # MRO
<class 'poly.models.MyManager'>

# check for correct default manager
>>> type(MROBase1._default_manager)
<class 'poly.models.MyManager'>
 
# Django vanilla inheritance does not inherit MyManager as _default_manager here
>>> type(MROBase2._default_manager)
<class 'poly.models.MyManager'>

### Django model inheritance diamond problem, fails for Django 1.1

#>>> o=DiamondXY.objects.create(field_b='b', field_x='x', field_y='y')
#>>> print 'DiamondXY fields 1: field_b "%s", field_x "%s", field_y "%s"' % (o.field_b, o.field_x, o.field_y)
#DiamondXY fields 1: field_b "a", field_x "x", field_y "y"

>>> settings.DEBUG=False

"""

import settings

from django.test import TestCase
from django.db.models.query import QuerySet
from django.db.models import Q

from models import *

class testclass(TestCase):
    def test_diamond_inheritance(self):    
        # Django diamond problem
        o = DiamondXY.objects.create(field_b='b', field_x='x', field_y='y')
        print 'DiamondXY fields 1: field_b "%s", field_x "%s", field_y "%s"' % (o.field_b, o.field_x, o.field_y)
        o = DiamondXY.objects.get()
        print 'DiamondXY fields 2: field_b "%s", field_x "%s", field_y "%s"' % (o.field_b, o.field_x, o.field_y)
        if o.field_b != 'b': print '# Django model inheritance diamond problem detected'
        
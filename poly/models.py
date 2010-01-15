from django.db import models

from polymorphic import PolymorphicModel, PolymorphicManager, PolymorphicQuerySet

class ShowFieldContent(object):
    def __repr__(self):
        out = 'id %d, ' % (self.id); last = self._meta.fields[-1]
        for f in self._meta.fields:
            if f.name in [ 'id', 'p_classname', 'p_appname' ] or 'ptr' in f.name: continue
            out += f.name + ' (' + type(f).__name__ + ')'
            if isinstance(f, (models.ForeignKey)):
                o = getattr(self, f.name)
                out += ': "' + ('None' if o == None else o.__class__.__name__) + '"'
            else:
                out += ': "' + getattr(self, f.name) + '"'
            if f != last:  out += ', '
        return '<' + self.__class__.__name__ + ': ' + out + '>'

class PlainA(models.Model):
    field1 = models.CharField(max_length=10)
class PlainB(PlainA):
    field2 = models.CharField(max_length=10)
class PlainC(PlainB):
    field3 = models.CharField(max_length=10)

class ModelA(PolymorphicModel):
    field1 = models.CharField(max_length=10)
class ModelB(ModelA):
    field2 = models.CharField(max_length=10)
class ModelC(ModelB):
    field3 = models.CharField(max_length=10)

class Base(PolymorphicModel):
    field_b = models.CharField(max_length=10)
class ModelX(Base):
    field_x = models.CharField(max_length=10)
class ModelY(Base):
    field_y = models.CharField(max_length=10)

class Enhance_Plain(models.Model):
    field_p = models.CharField(max_length=10)
class Enhance_Base(ShowFieldContent, PolymorphicModel):
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

class RelationBase(ShowFieldContent, PolymorphicModel):
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
    many2many = models.ManyToManyField(ModelA)

class MyManager(PolymorphicManager):
    def get_query_set(self):
        return super(MyManager, self).get_query_set().order_by('-field1')
class ModelWithMyManager(ShowFieldContent, ModelA):
    objects = MyManager()
    field4 = models.CharField(max_length=10)

class MROBase1(PolymorphicModel):
    objects = MyManager()
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
class MgrInheritC(ShowFieldContent, MgrInheritB):
    pass


# -*- coding: utf-8 -*-

from django.db import models

def _represent_foreign_key(o):
    if o is None:
        out = '"None"'
    else:
        out = '"' + o.__class__.__name__ + '"'
    return out

class ShowFieldsAndTypes(object):
    """ model mixin, like ShowFields, but also show field types """
    def __repr__(self):
        out = 'id %d' % (self.pk)
        for f in self._meta.fields:
            if f.name in [ 'id' ] + self.polymorphic_internal_model_fields or 'ptr' in f.name: continue
            out += ', ' + f.name + ' (' + type(f).__name__ + ')'
            if isinstance(f, (models.ForeignKey)):
                o = getattr(self, f.name)
                out += ': ' + _represent_foreign_key(o)
            else:
                out += ': "' + getattr(self, f.name) + '"'
        return '<' + self.__class__.__name__ + ': ' + out + '>'

class ShowFields(object):
    """ model mixin that shows the object's class, it's fields and field contents """
    def __repr__(self):
        out = 'id %d, ' % (self.pk)
        for f in self._meta.fields:
            if f.name in [ 'id' ] + self.polymorphic_internal_model_fields or 'ptr' in f.name: continue
            out += ', ' + f.name
            if isinstance(f, (models.ForeignKey)):
                o = getattr(self, f.name)
                out += ': ' + _represent_foreign_key(o)
            else:
                out += ': "' + getattr(self, f.name) + '"'
        return '<' + (self.__class__.__name__ + ': ') + out + '>'

class ShowFieldTypes(object):
    """ INTERNAL; don't use this!
    This mixin is already used by default by PolymorphicModel.
    (model mixin that shows the object's class and it's field types) """
    def __repr__(self):
        out = self.__class__.__name__ + ': id %d' % (self.pk or - 1)
        for f in self._meta.fields:
            if f.name in [ 'id' ] + self.polymorphic_internal_model_fields or 'ptr' in f.name: continue
            out += ', ' + f.name + ' (' + type(f).__name__ + ')'
        return '<' + out + '>'


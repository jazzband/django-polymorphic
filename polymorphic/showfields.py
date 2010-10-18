# -*- coding: utf-8 -*-

from django.db import models


class ShowFieldBase(object):
    """ base class for the ShowField... model mixins, does the work """
    polymorphic_query_multiline_output = True # cause nicer multiline PolymorphicQuery output

    polymorphic_showfield_type = False
    polymorphic_showfield_content = False

    def __repr__(self):
        return self.__unicode__()

    def __unicode__(self):
        out = u'<'+self.__class__.__name__+': id %s' % unicode(self.pk)
        for f in self._meta.fields + self._meta.many_to_many:

            if f.name in [ 'id' ] + self.polymorphic_internal_model_fields or 'ptr' in f.name: continue
            out += ', ' + f.name

            if self.polymorphic_showfield_type:
                out += ' (' + type(f).__name__ + ')'

            if self.polymorphic_showfield_content:
                o = getattr(self, f.name)

                if isinstance(f, (models.ForeignKey)):
                    #out += ': ' + ( '"None"' if o is None else '"' + o.__class__.__name__ + '"' )
                    out += ': '
                    if o is None:
                        out += '"None"'
                    else:
                        out += '"' + o.__class__.__name__ + '"'

                elif isinstance(f, (models.ManyToManyField)):
                    out += ': %d' % o.count()

                else:
                    out += ': "' + unicode(o) + '"'

        if hasattr(self,'polymorphic_annotate_names'):
            out += ' - Ann: '
            for an in self.polymorphic_annotate_names:
                if an != self.polymorphic_annotate_names[0]:
                    out += ', '
                out += an
                if self.polymorphic_showfield_type:
                    out += ' (' + type(getattr(self, an)).__name__ + ')'
                if self.polymorphic_showfield_content:
                    out += ': "' + unicode(getattr(self, an)) + '"'

        return out+'>'

class ShowFieldType(ShowFieldBase):
    """ model mixin that shows the object's class and it's field types """
    polymorphic_showfield_type = True

class ShowFieldContent(ShowFieldBase):
    """ model mixin that shows the object's class, it's fields and field contents """
    polymorphic_showfield_content = True

class ShowFieldTypeAndContent(ShowFieldBase):
    """ model mixin, like ShowFieldContent, but also show field types """
    polymorphic_showfield_type = True
    polymorphic_showfield_content = True


# compatibility with old class names
ShowFieldTypes = ShowFieldType
ShowFields = ShowFieldContent
ShowFieldsAndTypes = ShowFieldTypeAndContent

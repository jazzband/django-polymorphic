# -*- coding: utf-8 -*-

from django.db import models
from django.utils import six


class ShowFieldBase(object):
    """
    Base class for the ShowField... model mixins.
    """

    showfield_type = False
    showfield_content = False

    # these may be overridden by the user
    showfield_max_line_width = None
    showfield_max_field_width = 20
    showfield_old_format = False

    def __repr__(self):
        return self.__unicode__()

    def _showfields_get_content(self, field_name, field_type=type(None)):
        "helper for __unicode__"
        content = getattr(self, field_name)
        if self.showfield_old_format:
            out = ': '
        else:
            out = ' '
        if issubclass(field_type, models.ForeignKey):
            if content is None:
                out += 'None'
            else:
                model = content.__class__
                if model._deferred:
                    model = model._meta.proxy_for_model
                out += model.__name__
        elif issubclass(field_type, models.ManyToManyField):
            out += '%d' % content.count()
        elif isinstance(content, six.integer_types):
            out += str(content)
        elif content is None:
            out += 'None'
        else:
            txt = six.text_type(content)
            if len(txt) > self.showfield_max_field_width:
                txt = txt[:self.showfield_max_field_width - 2] + '..'
            out += '"' + txt + '"'
        return out

    def _showfields_add_regular_fields(self, parts):
        "helper for __unicode__"
        done_fields = set()
        for field in self._meta.fields + self._meta.many_to_many:
            if field.name in self.polymorphic_internal_model_fields or '_ptr' in field.name:
                continue
            if field.name in done_fields:
                continue  # work around django diamond inheritance problem
            done_fields.add(field.name)

            out = field.name

            # if this is the standard primary key named "id", print it as we did with older versions of django_polymorphic
            if field.primary_key and field.name == 'id' and type(field) == models.AutoField:
                out += ' ' + six.text_type(getattr(self, field.name))

            # otherwise, display it just like all other fields (with correct type, shortened content etc.)
            else:
                if self.showfield_type:
                    out += ' (' + type(field).__name__
                    if field.primary_key:
                        out += '/pk'
                    out += ')'

                if self.showfield_content:
                    out += self._showfields_get_content(field.name, type(field))

            parts.append((False, out, ','))

    def __unicode__(self):
        # create list ("parts") containing one tuple for each title/field:
        # ( bool: new section , item-text , separator to use after item )

        # start with model name
        model = self.__class__
        if model._deferred:
            model = model._meta.proxy_for_model

        parts = [(True, model.__name__, ':')]

        # add all regular fields
        self._showfields_add_regular_fields(parts)

        # format result

        indent = len(model.__name__) + 5
        indentstr = ''.rjust(indent)
        out = ''
        xpos = 0
        possible_line_break_pos = None

        for i in range(len(parts)):
            new_section, p, separator = parts[i]
            final = (i == len(parts) - 1)
            if not final:
                next_new_section, _, _ = parts[i + 1]

            if self.showfield_max_line_width and \
               xpos + len(p) > self.showfield_max_line_width and \
               possible_line_break_pos is not None:
                rest = out[possible_line_break_pos:]
                out = out[:possible_line_break_pos]
                out += '\n' + indentstr + rest
                xpos = indent + len(rest)

            out += p
            xpos += len(p)

            if not final:
                if not next_new_section:
                    out += separator
                    xpos += len(separator)
                out += ' '
                xpos += 1

            if not new_section:
                possible_line_break_pos = len(out)

        return '<' + out + '>'


class ShowFieldType(ShowFieldBase):
    """ model mixin that shows the object's class and it's field types """
    showfield_type = True


class ShowFieldContent(ShowFieldBase):
    """ model mixin that shows the object's class, it's fields and field contents """
    showfield_content = True


class ShowFieldTypeAndContent(ShowFieldBase):
    """ model mixin, like ShowFieldContent, but also show field types """
    showfield_type = True
    showfield_content = True


# compatibility with old class names
ShowFieldTypes = ShowFieldType
ShowFields = ShowFieldContent
ShowFieldsAndTypes = ShowFieldTypeAndContent

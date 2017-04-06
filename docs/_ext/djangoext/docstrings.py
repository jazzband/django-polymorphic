"""
Automatically mention all model fields as parameters in the model construction.
Based on http://djangosnippets.org/snippets/2533/
"""
import django
from django.utils.html import strip_tags
from django.utils.encoding import force_text
import inspect


def improve_model_docstring(app, what, name, obj, options, lines):
    from django.db import models  # must be inside the function, to allow settings initialization first.

    if inspect.isclass(obj) and issubclass(obj, models.Model):
        if django.VERSION >= (1,8):
            model_fields = obj._meta.get_fields()
        elif django.VERSION >= (1,6):
            model_fields = obj._meta.fields
        else:
            model_fields = obj._meta._fields()

        for field in model_fields:
            help_text = strip_tags(force_text(field.help_text))
            verbose_name = force_text(field.verbose_name).capitalize()

            # Add parameter
            if help_text:
                lines.append(u':param %s: %s' % (field.attname, help_text))
            else:
                lines.append(u':param %s: %s' % (field.attname, verbose_name))

            # Add type
            if isinstance(field, models.ForeignKey):
                to = field.rel.to
                lines.append(u':type %s: %s to :class:`~%s.%s`' % (field.attname, type(field).__name__, to.__module__, to.__name__))
            else:
                lines.append(u':type %s: %s' % (field.attname, type(field).__name__))

    # Return the extended docstring
    return lines

# Allow this module to be used as sphinx extension:
def setup(app):
    # Generate docstrings for Django model fields
    # Register the docstring processor with sphinx
    app.connect('autodoc-process-docstring', improve_model_docstring)


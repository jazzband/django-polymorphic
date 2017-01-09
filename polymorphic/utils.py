from django.contrib.contenttypes.models import ContentType
from django.db import DEFAULT_DB_ALIAS


def reset_polymorphic_ctype(*models, **filters):
    """
    Set the polymorphic content-type ID field to the proper model
    Sort the ``*models`` from base class to descending class,
    to make sure the content types are properly assigned.

    Add ``preserve_existing=True`` to skip models which already
    have a polymorphic content type.
    """
    using = filters.pop('using', DEFAULT_DB_ALIAS)
    ignore_existing = filters.pop('ignore_existing', False)
    if ignore_existing:
        # When excluding models, make sure we don't ignore the models we
        # just assigned the an content type to. hence, start with child first.
        models = reversed(models)

    for new_model in models:
        new_ct = ContentType.objects.db_manager(using).get_for_model(new_model)

        qs = new_model.objects.db_manager(using)
        if ignore_existing:
            qs = qs.filter(polymorphic_ctype__isnull=True)
        if filters:
            qs = qs.filter(**filters)
        qs.update(polymorphic_ctype=new_ct)

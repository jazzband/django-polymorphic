from django.contrib.contenttypes.models import ContentType


def reset_polymorphic_ctype(*models, **filters):
    """
    Set the polymorphic content-type ID field to the proper model
    Sort the ``*models`` from base class to descending class,
    to make sure the content types are properly assigned.

    Add ``preserve_existing=True`` to skip models which already
    have a polymorphic content type.
    """
    preserve_existing = filters.pop('preserve_existing', False)
    for new_model in models:
        new_ct = ContentType.objects.get_for_model(new_model)

        qs = new_model.objects.all()
        if preserve_existing:
            qs = qs.filter(polymorphic_ctype__isnull=True)
        if filters:
            qs = qs.filter(**filters)
        qs.update(polymorphic_ctype=new_ct)

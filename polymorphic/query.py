# -*- coding: utf-8 -*-
""" QuerySet for PolymorphicModel
    Please see README.rst or DOCS.rst or http://bserve.webhop.org/wiki/django_polymorphic
"""

from compatibility_tools import defaultdict

from django.db.models.query import QuerySet
from django.contrib.contenttypes.models import ContentType

from query_translate import translate_polymorphic_filter_definitions_in_kwargs, translate_polymorphic_filter_definitions_in_args, translate_polymorphic_field_path

# chunk-size: maximum number of objects requested per db-request
# by the polymorphic queryset.iterator() implementation; we use the same chunk size as Django
from django.db.models.query import CHUNK_SIZE               # this is 100 for Django 1.1/1.2
Polymorphic_QuerySet_objects_per_request = CHUNK_SIZE


###################################################################################
### PolymorphicQuerySet

class PolymorphicQuerySet(QuerySet):
    """
    QuerySet for PolymorphicModel

    Contains the core functionality for PolymorphicModel

    Usually not explicitly needed, except if a custom queryset class
    is to be used.
    """

    def __init__(self, *args, **kwargs):
        "init our queryset object member variables"
        self.polymorphic_disabled = False
        super(PolymorphicQuerySet, self).__init__(*args, **kwargs)

    def _clone(self, *args, **kwargs):
        "Django's _clone only copies its own variables, so we need to copy ours here"
        new = super(PolymorphicQuerySet, self)._clone(*args, **kwargs)
        new.polymorphic_disabled = self.polymorphic_disabled
        return new

    def instance_of(self, *args):
        """Filter the queryset to only include the classes in args (and their subclasses).
        Implementation in _translate_polymorphic_filter_defnition."""
        return self.filter(instance_of=args)

    def not_instance_of(self, *args):
        """Filter the queryset to exclude the classes in args (and their subclasses).
        Implementation in _translate_polymorphic_filter_defnition."""
        return self.filter(not_instance_of=args)

    def _filter_or_exclude(self, negate, *args, **kwargs):
        "We override this internal Django functon as it is used for all filter member functions."
        translate_polymorphic_filter_definitions_in_args(self.model, args) # the Q objects
        additional_args = translate_polymorphic_filter_definitions_in_kwargs(self.model, kwargs) # filter_field='data'
        return super(PolymorphicQuerySet, self)._filter_or_exclude(negate, *(list(args) + additional_args), **kwargs)

    def order_by(self, *args, **kwargs):
        """translate the field paths in the args, then call vanilla order_by."""
        new_args = [ translate_polymorphic_field_path(self.model, a) for a in args ]
        return super(PolymorphicQuerySet, self).order_by(*new_args, **kwargs)

    def _process_aggregate_args(self, args, kwargs):
        """for aggregate and annotate kwargs: allow ModelX___field syntax for kwargs, forbid it for args.
        Modifies kwargs if needed (these are Aggregate objects, we translate the lookup member variable)"""
        for a in args:
            assert not '___' in a.lookup, 'PolymorphicModel: annotate()/aggregate(): ___ model lookup supported for keyword arguments only'
        for a in kwargs.values():
            a.lookup = translate_polymorphic_field_path(self.model, a.lookup)

    def annotate(self, *args, **kwargs):
        """translate the field paths in the kwargs, then call vanilla annotate.
        _get_real_instances will do the rest of the job after executing the query."""
        self._process_aggregate_args(args, kwargs)
        return super(PolymorphicQuerySet, self).annotate(*args, **kwargs)

    def aggregate(self, *args, **kwargs):
        """translate the field paths in the kwargs, then call vanilla aggregate.
        We need no polymorphic object retrieval for aggregate => switch it off."""
        self._process_aggregate_args(args, kwargs)
        self.polymorphic_disabled = True
        return super(PolymorphicQuerySet, self).aggregate(*args, **kwargs)

    def extra(self, *args, **kwargs):
        self.polymorphic_disabled = not bool(kwargs.pop('polymorphic', False))
        return super(PolymorphicQuerySet, self).extra(*args, **kwargs)

    def _get_real_instances(self, base_result_objects):
        """
        Polymorphic object loader

        Does the same as:

            return [ o.get_real_instance() for o in base_result_objects ]

        The list base_result_objects contains the objects from the executed
        base class query. The class of all of them is self.model (our base model).

        Some, many or all of these objects were not created and stored as
        class self.model, but as a class derived from self.model. We want to re-fetch
        these objects from the db as their original class so we can return them
        just as they were created/saved.

        We identify these objects by looking at o.polymorphic_ctype, which specifies
        the real class of these objects (the class at the time they were saved).

        First, we sort the result objects in base_result_objects for their
        subclass (from o.polymorphic_ctype), and then we execute one db query per
        subclass of objects. Here, we handle any annotations from annotate().

        Finally we re-sort the resulting objects into the correct order and
        return them as a list.
        """
        ordered_id_list = []    # list of ids of result-objects in correct order
        results = {}            # polymorphic dict of result-objects, keyed with their id (no order)

        # dict contains one entry per unique model type occurring in result,
        # in the format idlist_per_model[modelclass]=[list-of-object-ids]
        idlist_per_model = defaultdict(list)

        # - sort base_result_object ids into idlist_per_model lists, depending on their real class;
        # - also record the correct result order in "ordered_id_list"
        # - store objects that already have the correct class into "results"
        base_result_objects_by_id = {}
        self_model_content_type_id = ContentType.objects.get_for_model(self.model).pk
        for base_object in base_result_objects:
            ordered_id_list.append(base_object.pk)
            base_result_objects_by_id[base_object.pk] = base_object

            # this object is not a derived object and already the real instance => store it right away
            if (base_object.polymorphic_ctype_id == self_model_content_type_id):
                results[base_object.pk] = base_object

            # this object is derived and its real instance needs to be retrieved
            # => store it's id into the bin for this model type
            else:
                idlist_per_model[base_object.get_real_instance_class()].append(base_object.pk)

        # For each model in "idlist_per_model" request its objects (the real model)
        # from the db and store them in results[].
        # Then we copy the annotate fields from the base objects to the real objects.
        # TODO: defer(), only(): support for these would be around here
        for modelclass, idlist in idlist_per_model.items():
            qs = modelclass.base_objects.filter(id__in=idlist)
            qs.dup_select_related(self)    # copy select related configuration to new qs
            for o in qs:
                if self.query.aggregates:
                    for anno in self.query.aggregates.keys():
                        attr = getattr(base_result_objects_by_id[o.pk], anno)
                        setattr(o, anno, attr)
                results[o.pk] = o

        # re-create correct order and return result list
        resultlist = [ results[ordered_id] for ordered_id in ordered_id_list if ordered_id in results ]
        return resultlist

    def iterator(self):
        """
        This function is used by Django for all object retrieval.
        By overriding it, we modify the objects that this queryset returns
        when it is evaluated (or its get method or other object-returning methods are called).

        Here we do the same as:

            base_result_objects=list(super(PolymorphicQuerySet, self).iterator())
            real_results=self._get_real_instances(base_result_objects)
            for o in real_results: yield o

        but it requests the objects in chunks from the database,
        with Polymorphic_QuerySet_objects_per_request per chunk
        """
        base_iter = super(PolymorphicQuerySet, self).iterator()

        # disabled => work just like a normal queryset
        if self.polymorphic_disabled:
            for o in base_iter: yield o
            raise StopIteration

        while True:
            base_result_objects = []
            reached_end = False

            for i in range(Polymorphic_QuerySet_objects_per_request):
                try: base_result_objects.append(base_iter.next())
                except StopIteration:
                    reached_end = True
                    break

            real_results = self._get_real_instances(base_result_objects)

            for o in real_results:
                yield o

            if reached_end: raise StopIteration

    def __repr__(self):
        result = [ repr(o) for o in self.all() ]
        return  '[ ' + ',\n  '.join(result) + ' ]'



import copy
import tempfile
import pickle
import threading

from django.db.models import Q
from django.test import TestCase

from polymorphic.tests.models import Bottom, Middle, Top
from polymorphic.query_translate import translate_polymorphic_filter_definitions_in_args


class QueryTranslateTests(TestCase):
    def test_translate_with_not_pickleable_query(self):
        """
        In some cases, Django may attacha _thread object to the query and we
        will get the following when we try to deepcopy inside of
        translate_polymorphic_filter_definitions_in_args:

            TypeError: cannot pickle '_thread.lock' object


        For this to trigger, we need to somehoe go down this path:

                File "/perfdash/.venv/lib64/python3.12/site-packages/polymorphic/query_translate.py", line 95, in translate_polymorphic_filter_definitions_in_args
            translate_polymorphic_Q_object(queryset_model, copy.deepcopy(q), using=using) for q in args
                                                        ^^^^^^^^^^^^^^^^
        File "/usr/lib64/python3.12/copy.py", line 143, in deepcopy
            y = copier(memo)
                ^^^^^^^^^^^^
        File "/perfdash/.venv/lib64/python3.12/site-packages/django/utils/tree.py", line 53, in __deepcopy__
            obj.children = copy.deepcopy(self.children, memodict)
                        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
        File "/usr/lib64/python3.12/copy.py", line 136, in deepcopy
            y = copier(x, memo)
                ^^^^^^^^^^^^^^^

        Internals in Django, somehow we must trigger this tree.py code in django via
        the deepcopy in order to trigger this.

        """

        with tempfile.TemporaryFile() as fd:
            # verify this is definitely not pickleable
            with self.assertRaises(TypeError):
                pickle.dumps(threading.Lock())

            # I know this doesn't make sense to pass as a Q(), but
            # I haven't found another way to trigger the copy.deepcopy failing.
            q = Q(blog__info="blog info") | Q(blog__info=threading.Lock())

            translate_polymorphic_filter_definitions_in_args(Bottom, args=[q])

    def test_deep_copy_of_q_objects(self):
        import os
        from polymorphic.tests.models import DeepCopyTester, DeepCopyTester2
        # binary fields can have an unpickleable memoryview object in them
        # see https://github.com/jazzband/django-polymorphic/issues/524

        d1_bf = os.urandom(32)
        d2_bf1 = os.urandom(32)
        d2_bf2 = os.urandom(32)

        dct1 = DeepCopyTester.objects.create(binary_field=d1_bf)
        dct2 = DeepCopyTester2.objects.create(binary_field=d2_bf1, binary_field2=d2_bf2)

        self.assertEqual(list(DeepCopyTester.objects.filter(binary_field=d1_bf).all()), [dct1])

        q1 = Q(DeepCopyTester2___binary_field2=d2_bf1)
        self.assertEqual(list(DeepCopyTester.objects.filter(q1).all()), [])
        assert q1.children[0][0] == "DeepCopyTester2___binary_field2"
        q2 = Q(DeepCopyTester2___binary_field2=d2_bf2)
        self.assertEqual(list(DeepCopyTester.objects.filter(q2).all()), [dct2])
        assert q2.children[0][0] == "DeepCopyTester2___binary_field2"

        assert len(DeepCopyTester.objects.filter(Q(binary_field=memoryview(d1_bf)))) == 1

        self.assertEqual(DeepCopyTester.objects.all().delete()[0], 3)
        self.assertEqual(DeepCopyTester.objects.count(), 0)

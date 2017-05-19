# -*- coding: utf-8 -*-
"""
This module is a scratchpad for general development, testing & debugging
Well, even more so than pcmd.py. You best ignore p2cmd.py.
"""
import sys
import time
from pprint import pprint
from random import Random
from django.core.management.base import NoArgsCommand
from django.db import connection

from pexp.models import *


rnd = Random()


def show_queries():
    print()
    print("QUERIES:", len(connection.queries))
    pprint(connection.queries)
    print()
    connection.queries = []


def print_timing(func, message='', iterations=1):
    def wrapper(*arg):
        results = []
        connection.queries_log.clear()
        for i in range(iterations):
            t1 = time.time()
            x = func(*arg)
            t2 = time.time()
            results.append((t2 - t1) * 1000.0)
        res_sum = 0
        for r in results:
            res_sum += r
        print("%s%-19s: %.4f ms, %i queries (%i times)" % (
            message, func.func_name,
            res_sum,
            len(connection.queries),
            iterations
        ))
        sys.stdout.flush()
    return wrapper


class Command(NoArgsCommand):
    help = ""

    def handle_noargs(self, **options):
        if False:
            TestModelA.objects.all().delete()
            a = TestModelA.objects.create(field1='A1')
            b = TestModelB.objects.create(field1='B1', field2='B2')
            c = TestModelC.objects.create(field1='C1', field2='C2', field3='C3')
            connection.queries_log.clear()
            print(TestModelC.base_objects.all())
            show_queries()

        if False:
            TestModelA.objects.all().delete()
            for i in range(1000):
                a = TestModelA.objects.create(field1=str(i % 100))
                b = TestModelB.objects.create(field1=str(i % 100), field2=str(i % 200))
                c = TestModelC.objects.create(field1=str(i % 100), field2=str(i % 200), field3=str(i % 300))
                if i % 100 == 0:
                    print(i)

        f = print_timing(poly_sql_query, iterations=1000)
        f()

        f = print_timing(poly_sql_query2, iterations=1000)
        f()

        return

        NormalModelA.objects.all().delete()
        a = NormalModelA.objects.create(field1='A1')
        b = NormalModelB.objects.create(field1='B1', field2='B2')
        c = NormalModelC.objects.create(field1='C1', field2='C2', field3='C3')
        qs = TestModelA.objects.raw("SELECT * from pexp_testmodela")
        for o in list(qs):
            print(o)


def poly_sql_query():
    cursor = connection.cursor()
    cursor.execute("""
        SELECT id, pexp_testmodela.field1, pexp_testmodelb.field2, pexp_testmodelc.field3
        FROM pexp_testmodela
        LEFT OUTER JOIN pexp_testmodelb
        ON pexp_testmodela.id = pexp_testmodelb.testmodela_ptr_id
        LEFT OUTER JOIN pexp_testmodelc
        ON pexp_testmodelb.testmodela_ptr_id = pexp_testmodelc.testmodelb_ptr_id
        WHERE pexp_testmodela.field1=%i
        ORDER BY pexp_testmodela.id
        """ % rnd.randint(0, 100))
    # row=cursor.fetchone()
    return


def poly_sql_query2():
    cursor = connection.cursor()
    cursor.execute("""
        SELECT id, pexp_testmodela.field1
        FROM pexp_testmodela
        WHERE pexp_testmodela.field1=%i
        ORDER BY pexp_testmodela.id
        """ % rnd.randint(0, 100))
    # row=cursor.fetchone()
    return

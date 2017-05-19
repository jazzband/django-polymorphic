# -*- coding: utf-8 -*-
"""
This module is a scratchpad for general development, testing & debugging
"""

import time
import sys

from django.core.management.base import NoArgsCommand
from django.db import connection
from pprint import pprint
from pexp.models import *


num_objects = 1000


def show_queries():
    print()
    print("QUERIES:", len(connection.queries))
    pprint(connection.queries)
    print()
    connection.queries_log.clear()


###################################################################################
# benchmark wrappers


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
        median = res_sum / len(results)
        print("%s%-19s: %.0f ms, %i queries" % (
            message, func.func_name,
            median,
            len(connection.queries) / len(results)
        ))
        sys.stdout.flush()
    return wrapper


def run_vanilla_any_poly(func, iterations=1):
    f = print_timing(func, '     ', iterations)
    f(NormalModelC)
    f = print_timing(func, 'poly ', iterations)
    f(TestModelC)


###################################################################################
# benchmarks

def bench_create(model):
    for i in xrange(num_objects):
        model.objects.create(field1='abc' + str(i), field2='abcd' + str(i), field3='abcde' + str(i))
    # print 'count:',model.objects.count()


def bench_load1(model):
    for o in model.objects.all():
        pass


def bench_load1_short(model):
    for i in xrange(num_objects / 100):
        for o in model.objects.all()[:100]:
            pass


def bench_load2(model):
    for o in model.objects.all():
        f1 = o.field1
        f2 = o.field2
        f3 = o.field3


def bench_load2_short(model):
    for i in xrange(num_objects / 100):
        for o in model.objects.all()[:100]:
            f1 = o.field1
            f2 = o.field2
            f3 = o.field3


def bench_delete(model):
    model.objects.all().delete()

###################################################################################
# Command


class Command(NoArgsCommand):
    help = ""

    def handle_noargs(self, **options):
        func_list = [
            (bench_delete, 1),
            (bench_create, 1),
            (bench_load1,  5),
            (bench_load1_short, 5),
            (bench_load2, 5),
            (bench_load2_short, 5)
        ]
        for f, iterations in func_list:
            run_vanilla_any_poly(f, iterations=iterations)

        print

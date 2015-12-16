# -*- coding: utf-8 -*-
# flake8: noqa
"""
This module is a scratchpad for general development, testing & debugging
Well, even more so than pcmd.py. You best ignore p2cmd.py.
"""
import uuid

from django.core.management.base import NoArgsCommand
from django.db.models import connection
from pprint import pprint
import time,sys

from pexp.models import *

def reset_queries():
    connection.queries=[]

def show_queries():
    print; print 'QUERIES:',len(connection.queries); pprint(connection.queries); print; connection.queries=[]

def print_timing(func, message='', iterations=1):
    def wrapper(*arg):
        results=[]
        reset_queries()
        for i in xrange(iterations):
            t1 = time.time()
            x = func(*arg)
            t2 = time.time()
            results.append((t2-t1)*1000.0)
        res_sum=0
        for r in results: res_sum +=r
        median = res_sum / len(results)
        print '%s%-19s: %.4f ms, %i queries (%i times)' % (
            message,func.func_name,
            res_sum,
            len(connection.queries),
            iterations
            )
        sys.stdout.flush()
    return wrapper

class Command(NoArgsCommand):
    help = ""

    def handle_noargs(self, **options):
        if False:
            ModelA.objects.all().delete()
            a=ModelA.objects.create(field1='A1')
            b=ModelB.objects.create(field1='B1', field2='B2')
            c=ModelC.objects.create(field1='C1', field2='C2', field3='C3')
            reset_queries()
            print ModelC.base_objects.all();
            show_queries()

        if False:
            ModelA.objects.all().delete()
            for i in xrange(1000):
                a=ModelA.objects.create(field1=str(i%100))
                b=ModelB.objects.create(field1=str(i%100), field2=str(i%200))
                c=ModelC.objects.create(field1=str(i%100), field2=str(i%200), field3=str(i%300))
                if i%100==0: print i

        f=print_timing(poly_sql_query,iterations=1000)
        f()

        f=print_timing(poly_sql_query2,iterations=1000)
        f()

        return

        nModelA.objects.all().delete()
        a=nModelA.objects.create(field1='A1')
        b=nModelB.objects.create(field1='B1', field2='B2')
        c=nModelC.objects.create(field1='C1', field2='C2', field3='C3')
        qs=ModelA.objects.raw("SELECT * from pexp_modela")
        for o in list(qs): print o

from django.db import connection, transaction
from random import Random
rnd=Random()

def poly_sql_query():
    cursor = connection.cursor()
    cursor.execute("""
        SELECT id, pexp_modela.field1, pexp_modelb.field2, pexp_modelc.field3
        FROM pexp_modela
        LEFT OUTER JOIN pexp_modelb
        ON pexp_modela.id = pexp_modelb.modela_ptr_id
        LEFT OUTER JOIN pexp_modelc
        ON pexp_modelb.modela_ptr_id = pexp_modelc.modelb_ptr_id
        WHERE pexp_modela.field1=%i
        ORDER BY pexp_modela.id
        """ % rnd.randint(0,100) )
    #row=cursor.fetchone()
    return

def poly_sql_query2():
    cursor = connection.cursor()
    cursor.execute("""
        SELECT id, pexp_modela.field1
        FROM pexp_modela
        WHERE pexp_modela.field1=%i
        ORDER BY pexp_modela.id
        """ % rnd.randint(0,100) )
    #row=cursor.fetchone()
    return

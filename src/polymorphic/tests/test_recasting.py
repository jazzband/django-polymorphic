from django.test import TransactionTestCase
from polymorphic.tests.models import Model2A, Model2B, Model2C, Model2D


class CreateFromSuperTests(TransactionTestCase):
    def test_create_from_super(self):
        # run create test 3 times because initial implementation
        # would fail after first success.
        for i in range(3):
            mc = Model2C.objects.create(
                field1="C1{}".format(i), field2="C2{}".format(i), field3="C3{}".format(i)
            )
            mc.save()
            field4 = "D4{}".format(i)
            md = Model2D.objects.create_from_super(mc, field4=field4)
            self.assertEqual(mc.id, md.id)
            self.assertEqual(mc.field1, md.field1)
            self.assertEqual(mc.field2, md.field2)
            self.assertEqual(mc.field3, md.field3)
            self.assertEqual(md.field4, field4)
        ma = Model2A.objects.create(field1="A1e")
        self.assertRaises(Exception, Model2D.objects.create_from_super, ma, field4="D4e")
        mb = Model2B.objects.create(field1="B1e", field2="B2e")
        self.assertRaises(Exception, Model2D.objects.create_from_super, mb, field4="D4e")

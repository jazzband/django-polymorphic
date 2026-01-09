from django.test import TestCase
import shutil
import tempfile
from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from django.test.utils import CaptureQueriesContext
from django.test import override_settings
from django.db import connection


@override_settings()
class TestDeletion(TestCase):
    def setUp(self):
        super().setUp()
        self._media_root = tempfile.mkdtemp(prefix="test-media-")
        self._media_override = override_settings(MEDIA_ROOT=self._media_root)
        self._media_override.enable()

    def tearDown(self):
        self._media_override.disable()
        shutil.rmtree(self._media_root, ignore_errors=True)
        super().tearDown()

    def test_deletion_bug_160(self):
        """https://github.com/jazzband/django-polymorphic/issues/160"""
        from .models import A_160, B_160, B1_160, B2_160, C_160
        from .models import A_160Plain, B_160Plain, C_160Plain, B1_160Plain, B2_160Plain

        a = A_160Plain.objects.create()
        a2 = A_160Plain.objects.create()
        b1 = B1_160Plain.objects.create(a=a)
        b2 = B2_160Plain.objects.create(a=a)
        b2_2 = B2_160Plain.objects.create(a=a2)
        c = C_160Plain.objects.create(b=b1)
        a.delete()
        assert [a2] == list(A_160Plain.objects.all())
        assert B_160Plain.objects.count() == 1
        assert B1_160Plain.objects.count() == 0
        assert [b2_2] == list(B2_160Plain.objects.all())
        assert C_160Plain.objects.count() == 0

        a = A_160.objects.create()
        a2 = A_160.objects.create()
        b1 = B1_160.objects.create(a=a)
        b2 = B2_160.objects.create(a=a)
        b2_2 = B2_160.objects.create(a=a2)
        c = C_160.objects.create(b=b1)
        a.delete()
        assert [a2] == list(A_160.objects.all())
        assert B_160.objects.count() == 1
        assert B1_160.objects.count() == 0
        assert [b2_2] == list(B2_160.objects.all())
        assert C_160.objects.count() == 0

    def test_deletion_bug_229(self):
        """
        https://github.com/jazzband/django-polymorphic/issues/229
        """
        from .models import Farm, Animal, Dog, Cat

        farm = Farm.objects.create()
        Dog.objects.create(farm=farm, name="Rex", dog_param="kibble")
        Cat.objects.create(farm=farm, name="Misty", cat_param="whiskers")
        farm.delete()
        assert Animal.objects.count() == 0
        assert Dog.objects.count() == 0
        assert Cat.objects.count() == 0
        assert Farm.objects.count() == 0

        farm = Farm.objects.create()
        Dog.objects.create(farm=farm, name="Rex", dog_param="kibble")
        Cat.objects.create(farm=farm, name="Misty", cat_param="whiskers")
        farm2 = Farm.objects.create()
        hugo = Cat.objects.create(farm=farm2, name="Hugo", cat_param="10")
        marlo = Cat.objects.create(farm=farm2, name="Marlo", cat_param="14")
        assert Animal.objects.count() == 4
        farm.delete()
        assert Animal.objects.count() == 2
        assert hugo in Cat.objects.all()
        assert marlo in Cat.objects.all()
        assert hugo in Animal.objects.all()
        assert marlo in Animal.objects.all()
        assert hugo in farm2.animals.all()
        assert marlo in farm2.animals.all()

        Animal.objects.all().delete()
        assert Animal.objects.count() == 0
        assert Dog.objects.count() == 0
        assert Cat.objects.count() == 0
        assert Farm.objects.count() == 1
        assert farm2 in Farm.objects.all()
        assert farm2.animals.count() == 0

    def test_deletion_bug_274(self):
        """
        https://github.com/jazzband/django-polymorphic/issues/274
        """
        from .models import A_274, B_274, C_274, D_274, E_274

        B_274.objects.create()
        D_274.objects.create()
        E_274.objects.create()
        A_274.objects.all().delete()

        assert A_274.objects.count() == 0
        assert B_274.objects.count() == 0
        assert D_274.objects.count() == 0
        assert E_274.objects.count() == 0
        assert C_274.objects.count() == 0

    def test_deletion_bug_357(self):
        """
        https://github.com/jazzband/django-polymorphic/issues/357
        """
        from .models import Order, Payment, CreditCardPayment, SepaPayment, Beneficiary

        order1 = Order.objects.create(title="Order 1")
        payment1 = SepaPayment.objects.create(
            order=order1,
            amount=100.00,
            iban="DE89370400440532013000",
            bic="COBADEFFXXX",
        )
        CreditCardPayment.objects.create(
            order=order1,
            amount=100.00,
            card_type="VISA",
        )
        bk = Beneficiary.objects.create(firstname="Brian", lastname="Kohan")
        ea = Beneficiary.objects.create(firstname="Edward", lastname="Abbey")
        payment1.beneficiaries.add(bk, ea)

        Order.objects.all().delete()

        assert Order.objects.count() == 0
        assert Payment.objects.count() == 0
        assert set(Beneficiary.objects.all()) == {bk, ea}

    def test_deletion_bug_540(self):
        """
        https://github.com/jazzband/django-polymorphic/issues/540
        """
        from .models import A_540, B_540

        b = B_540.objects.create(self_referential=None, name="b")
        a = A_540.objects.create(self_referential=b)

        A_540.objects.all().delete()

        assert A_540.objects.count() == 0
        assert B_540.objects.count() == 0

    def test_deletion_bug_547(self):
        """
        https://github.com/jazzband/django-polymorphic/issues/547
        """
        from .models import Project, DatasetFolder, OriginalFile, DatasetRelation, OriginalDataset

        User = get_user_model()
        user = User.objects.create_user(username="u1", password="x")

        project = Project.objects.create(name="p1", created_by=user)
        folder = DatasetFolder.objects.create(prjct=project)

        rel_bytes = b"id,parent_id\n1,\n2,1\n"
        rel_file = ContentFile(rel_bytes, name="relations.csv")
        relation = DatasetRelation.objects.create(
            dataset_folder=folder,
            content_type="text/csv",
            size=len(rel_bytes),
            file=rel_file,
            original_file_name="relations.csv",
        )

        ds_bytes = b"id,value\n1,foo\n2,bar\n"
        ds_file = ContentFile(ds_bytes, name="data.csv")
        OriginalDataset.objects.create(
            dataset_folder=folder,
            content_type="text/csv",
            size=len(ds_bytes),
            dataset_relation=relation,
            file=ds_file,
            original_file_name="data.csv",
            table_name="data",
            rows_number=2,
            dataset_metadata={"columns": ["id", "value"]},
        )

        # This is the operation that (per report) can crash with:
        # AttributeError: 'NoneType' object has no attribute 'attname'
        #
        # If the bug is present, this test will error here.
        project.delete()

        # If deletion succeeded, everything should be gone.
        assert Project.objects.count() == 0
        assert DatasetFolder.objects.count() == 0
        assert OriginalFile.objects.count() == 0
        assert DatasetRelation.objects.count() == 0
        assert OriginalDataset.objects.count() == 0

    def test_deletion_bug_608(self):
        """
        https://github.com/jazzband/django-polymorphic/issues/608
        """
        from .models import (
            PolyDevice,
            PolyEthernetInterface,
            PolyFCInterface,
            PolyFixedInterface,
            PolyInterface,
            PolyModularInterface,
            PolyWirelessInterface,
            # NotPolyInterface
        )

        device = PolyDevice.objects.create(name="Device 1")
        PolyEthernetInterface.objects.create(name="Eth0", device=device, ethernety_stuff="stuff")
        PolyFCInterface.objects.create(name="FC0", device=device, fc_stuff="stuff")
        PolyFixedInterface.objects.create(name="Fixed0", device=device, fixed_stuff="stuff")
        PolyModularInterface.objects.create(name="Modular0", device=device, modular_stuff="stuff")
        PolyWirelessInterface.objects.create(
            name="Wireless0", device=device, wirelessy_stuff="stuff"
        )
        PolyDevice.objects.all().delete()
        assert PolyDevice.objects.count() == 0

    def test_deletion_bug_608_2(self):
        """
        https://github.com/jazzband/django-polymorphic/issues/608
        """
        from .models import Poll, Question, Answer, TextAnswer, YesNoAnswer

        poll = Poll.objects.create()
        question = Question.objects.create(poll=poll)
        answer1 = TextAnswer.objects.create(question=question, answer="test")
        answer2 = YesNoAnswer.objects.create(question=question, answer=True)

        poll.delete()

        assert Poll.objects.count() == 0
        assert Question.objects.count() == 0
        assert Answer.objects.count() == 0
        assert TextAnswer.objects.count() == 0
        assert YesNoAnswer.objects.count() == 0

    def test_vanilla_deletion(self):
        """
        Test Django's vanilla multi table inheritance deletion and signaling.

                                    PlainA *-----> Standalone
                                 /          \
        Standalone *------* PlainB1       PlainB2 *------> Standalone
                               |
                            PlainC1 *------> Standalone
        """
        from .models import (
            PlainA,
            PlainB1,
            PlainC1,
            PlainB2,
            Standalone,
            RelatedToChild,
            Base,
            Child,
            GrandChild,
            RelatedToGrandChild,
        )

        print("---------------------------")

        PlainA.objects.create()
        with CaptureQueriesContext(connection) as ctx:
            """
            SELECT "plaina"."id", "plaina"."standalone_parent_id" FROM "plaina"
            SELECT "plainb1"."plaina_ptr_id" FROM "plainb1" WHERE "plainb1"."plaina_ptr_id" IN (1)
            DELETE FROM "plainb2" WHERE "plainb2"."plaina_ptr_id" IN (1)
            DELETE FROM "plaina" WHERE "plaina"."id" IN (1)
            """
            PlainA.objects.all().delete()

        # for q in ctx.captured_queries:
        #     print(q["sql"])

        print("---------------------------")
        PlainB1.objects.create()
        with CaptureQueriesContext(connection) as ctx:
            """
            SELECT "plaina"."id", "plaina"."standalone_parent_id", "plainb1"."plaina_ptr_id" FROM "plainb1" INNER JOIN "plaina" ON ("plainb1"."plaina_ptr_id" = "plaina"."id")
            SELECT "plainb1"."plaina_ptr_id", "plainc1"."plainb1_ptr_id" FROM "plainc1" INNER JOIN "plainb1" ON ("plainc1"."plainb1_ptr_id" = "plainb1"."plaina_ptr_id") WHERE "plainc1"."plainb1_ptr_id" IN (2)
            DELETE FROM "plainb1_standalones" WHERE "plainb1_standalones"."plainb1_id" IN (2)
            DELETE FROM "plainb1" WHERE "plainb1"."plaina_ptr_id" IN (2)
            DELETE FROM "plaina" WHERE "plaina"."id" IN (2)
            """
            PlainB1.objects.all().delete()

        # for q in ctx.captured_queries:
        #     print(q["sql"])

        print("---------------------------")
        PlainC1.objects.create()
        with CaptureQueriesContext(connection) as ctx:
            """
            SELECT "plaina"."id", "plaina"."standalone_parent_id", "plainb1"."plaina_ptr_id", "plainc1"."plainb1_ptr_id", "plainc1"."standalone_id" FROM "plainc1" INNER JOIN "plainb1" ON ("plainc1"."plainb1_ptr_id" = "plainb1"."plaina_ptr_id") INNER JOIN "plaina" ON ("plainb1"."plaina_ptr_id" = "plaina"."id")
            DELETE FROM "plainb1_standalones" WHERE "plainb1_standalones"."plainb1_id" IN (3)
            DELETE FROM "plainc1" WHERE "plainc1"."plainb1_ptr_id" IN (3)
            DELETE FROM "plainb1" WHERE "plainb1"."plaina_ptr_id" IN (3)
            DELETE FROM "plaina" WHERE "plaina"."id" IN (3)
            """
            PlainC1.objects.all().delete()

        # for q in ctx.captured_queries:
        #     print(q["sql"])

        print("---------------------------")
        PlainC1.objects.create()
        with CaptureQueriesContext(connection) as ctx:
            """
            SELECT "plaina"."id", "plaina"."standalone_parent_id" FROM "plaina"
            SELECT "plainb1"."plaina_ptr_id" FROM "plainb1" WHERE "plainb1"."plaina_ptr_id" IN (4)
            SELECT "plaina"."id", "plaina"."standalone_parent_id" FROM "plaina" WHERE "plaina"."id" = 4 LIMIT 21
            SELECT "plainb1"."plaina_ptr_id", "plainc1"."plainb1_ptr_id" FROM "plainc1" INNER JOIN "plainb1" ON ("plainc1"."plainb1_ptr_id" = "plainb1"."plaina_ptr_id") WHERE "plainc1"."plainb1_ptr_id" IN (4)
            SELECT "plaina"."id", "plaina"."standalone_parent_id", "plainb1"."plaina_ptr_id" FROM "plainb1" INNER JOIN "plaina" ON ("plainb1"."plaina_ptr_id" = "plaina"."id") WHERE "plainb1"."plaina_ptr_id" = 4 LIMIT 21
            DELETE FROM "plainb1_standalones" WHERE "plainb1_standalones"."plainb1_id" IN (4)
            DELETE FROM "plainb1_standalones" WHERE "plainb1_standalones"."plainb1_id" IN (4)
            DELETE FROM "plainb2" WHERE "plainb2"."plaina_ptr_id" IN (4)
            DELETE FROM "plainc1" WHERE "plainc1"."plainb1_ptr_id" IN (4)
            DELETE FROM "plainb1" WHERE "plainb1"."plaina_ptr_id" IN (4)
            DELETE FROM "plaina" WHERE "plaina"."id" IN (4)
            """
            PlainA.objects.all().delete()

        assert PlainC1.objects.count() == 0
        # for q in ctx.captured_queries:
        #     print(q["sql"])

        print("---------------------------")
        s0 = Standalone.objects.create()
        PlainC1.objects.create(standalone=s0)
        PlainB2.objects.create(standalone=s0)
        with CaptureQueriesContext(connection) as ctx:
            """
            SELECT "standalone"."id" FROM "standalone"
            SELECT "plaina"."id" FROM "plaina" WHERE "plaina"."standalone_parent_id" IN (1)
            SELECT "plaina"."id", "plaina"."standalone_parent_id", "plainb2"."plaina_ptr_id", "plainb2"."standalone_id" FROM "plainb2" INNER JOIN "plaina" ON ("plainb2"."plaina_ptr_id" = "plaina"."id") WHERE "plainb2"."standalone_id" IN (1)
            SELECT "plainb1"."plaina_ptr_id", "plainc1"."plainb1_ptr_id" FROM "plainc1" INNER JOIN "plainb1" ON ("plainc1"."plainb1_ptr_id" = "plainb1"."plaina_ptr_id") WHERE "plainc1"."standalone_id" IN (1)
            SELECT "plaina"."id", "plaina"."standalone_parent_id", "plainb1"."plaina_ptr_id" FROM "plainb1" INNER JOIN "plaina" ON ("plainb1"."plaina_ptr_id" = "plaina"."id") WHERE "plainb1"."plaina_ptr_id" = 5 LIMIT 21
            DELETE FROM "plainb1_standalones" WHERE "plainb1_standalones"."plainb1_id" IN (5)
            DELETE FROM "plainb1_standalones" WHERE "plainb1_standalones"."standalone_id" IN (1)
            DELETE FROM "standalone" WHERE "standalone"."id" IN (1)
            DELETE FROM "plainb2" WHERE "plainb2"."plaina_ptr_id" IN (6)
            DELETE FROM "plainc1" WHERE "plainc1"."plainb1_ptr_id" IN (5)
            DELETE FROM "plainb1" WHERE "plainb1"."plaina_ptr_id" IN (5)
            DELETE FROM "plaina" WHERE "plaina"."id" IN (6, 5)
            """
            Standalone.objects.all().delete()

        assert PlainC1.objects.count() == 0
        assert PlainB2.objects.count() == 0
        # for q in ctx.captured_queries:
        #     print(q["sql"])

        print("---------------------------")
        s0 = Standalone.objects.create()
        s1 = Standalone.objects.create()
        PlainB2.objects.create(standalone_parent=s0, standalone=s1)
        with CaptureQueriesContext(connection) as ctx:
            """
            SELECT "plaina"."id" FROM "plaina" WHERE "plaina"."standalone_parent_id" IN (2)
            SELECT "plainb1"."plaina_ptr_id" FROM "plainb1" WHERE "plainb1"."plaina_ptr_id" IN (7)
            SELECT "plaina"."id", "plaina"."standalone_parent_id", "plainb2"."plaina_ptr_id", "plainb2"."standalone_id" FROM "plainb2" INNER JOIN "plaina" ON ("plainb2"."plaina_ptr_id" = "plaina"."id") WHERE "plainb2"."standalone_id" IN (2)
            SELECT "plainb1"."plaina_ptr_id", "plainc1"."plainb1_ptr_id" FROM "plainc1" INNER JOIN "plainb1" ON ("plainc1"."plainb1_ptr_id" = "plainb1"."plaina_ptr_id") WHERE "plainc1"."standalone_id" IN (2)
            DELETE FROM "plainb2" WHERE "plainb2"."plaina_ptr_id" IN (7)
            DELETE FROM "plainb1_standalones" WHERE "plainb1_standalones"."standalone_id" IN (2)
            DELETE FROM "standalone" WHERE "standalone"."id" IN (2)
            DELETE FROM "plaina" WHERE "plaina"."id" IN (7)
            """
            s0.delete()

        assert PlainB2.objects.count() == 0
        assert list(Standalone.objects.all()) == [s1]
        # for q in ctx.captured_queries:
        #     print(q["sql"])

        print("---------------------------")
        grand_child = GrandChild.objects.create()
        RelatedToChild.objects.create(child=Child.objects.get(pk=grand_child.pk))
        RelatedToGrandChild.objects.create(grand_child=grand_child)

        with CaptureQueriesContext(connection) as ctx:
            """
            SELECT "base"."id" FROM "base" WHERE "base"."id" = 1
            SELECT "child"."base_ptr_id" FROM "child" WHERE "child"."base_ptr_id" IN (1)
            SELECT "base"."id" FROM "base" WHERE "base"."id" = 1 LIMIT 21
            SELECT "child"."base_ptr_id", "grandchild"."child_ptr_id" FROM "grandchild" INNER JOIN "child" ON ("grandchild"."child_ptr_id" = "child"."base_ptr_id") WHERE "grandchild"."child_ptr_id" IN (1)
            SELECT "base"."id", "child"."base_ptr_id" FROM "child" INNER JOIN "base" ON ("child"."base_ptr_id" = "base"."id") WHERE "child"."base_ptr_id" = 1 LIMIT 21
            DELETE FROM "relatedtochild" WHERE "relatedtochild"."child_id" IN (1)
            DELETE FROM "relatedtograndchild" WHERE "relatedtograndchild"."grand_child_id" IN (1)
            DELETE FROM "relatedtochild" WHERE "relatedtochild"."child_id" IN (1)
            DELETE FROM "grandchild" WHERE "grandchild"."child_ptr_id" IN (1)
            DELETE FROM "child" WHERE "child"."base_ptr_id" IN (1)
            DELETE FROM "base" WHERE "base"."id" IN (1)
            """
            Base.objects.filter(pk=grand_child.pk).delete()  # cascade should reach relatives!

        assert Base.objects.count() == 0
        assert Child.objects.count() == 0
        assert GrandChild.objects.count() == 0
        assert RelatedToChild.objects.count() == 0
        assert RelatedToGrandChild.objects.count() == 0
        # for q in ctx.captured_queries:
        #     print(q["sql"])

    def test_polymorphic_deletion_scenario1(self):
        """
        Test the first polymorphic deletion scenario:

        A normal model holds a foreign key to a polymorphic base model with several
        children.

                 <-- cascade --
         Normal1 ----- FK ---->  Poly1
                               /   |   \
                              A1   B1   C1

        Tests that when you delete from a poly instance at any level of the
        poly hierarchy, cascading deletion propagates correctly to Normal1.

        And deleting Normal1 also works with no effects on the poly instances.
        """
        from .models import (
            Normal1,
            Poly1,
            A1,
            B1,
            C1,
        )

        p1 = Poly1.objects.create()
        a1 = A1.objects.create()
        b1 = B1.objects.create()
        c1 = C1.objects.create()

        n1 = Normal1.objects.create(poly=p1)
        n2 = Normal1.objects.create(poly=c1)

        n3 = Normal1.objects.create(poly=a1)
        n4 = Normal1.objects.create(poly=b1)

        n5 = Normal1.objects.create(poly=p1)
        n6 = Normal1.objects.create(poly=b1)

        n7 = Normal1.objects.create(poly=b1)
        n8 = Normal1.objects.create(poly=c1)

        # test delete from parent
        Poly1.objects.filter(pk=a1.pk).delete()
        assert Normal1.objects.count() == 7
        assert n3 not in Normal1.objects.all()
        assert A1.objects.count() == 0

        Poly1.objects.filter(pk=p1.pk).delete()
        assert Normal1.objects.count() == 5
        assert n1 not in Normal1.objects.all()
        assert n5 not in Normal1.objects.all()

        n6.delete()
        assert Normal1.objects.count() == 4
        assert B1.objects.count() == 1
        assert C1.objects.count() == 1
        assert b1 in Poly1.objects.all()
        assert c1 in Poly1.objects.all()

        Poly1.objects.all().delete()
        assert Normal1.objects.count() == 0
        assert Poly1.objects.count() == 0

    def test_polymorphic_deletion_scenario2(self):
        """
        Test the second polymorphic deletion scenario:

        A polymorphic model holds a foreign key to a base model with several
        children.

                -- cascade -->
        Normal2 <----- FK ----  Poly2
                               /  |  \
                             A2   B2   C2

        Tests that when you delete a normal instance all related poly instances cascade
        correctly regardless of their concrete type in the hierarchy.

        This is the major collector failure mode.
        """

        from .models import (
            Normal2,
            Poly2,
            A2,
            B2,
            C2,
        )

        n1, n2, n3, n4 = (
            Normal2.objects.create(),
            Normal2.objects.create(),
            Normal2.objects.create(),
            Normal2.objects.create(),
        )

        p1, p2 = Poly2.objects.create(normal=n1), Poly2.objects.create(normal=n4)
        a1, a2 = A2.objects.create(normal=n2), A2.objects.create(normal=n3)
        b1, b2 = B2.objects.create(normal=n4), B2.objects.create(normal=n2)
        c1, c2 = C2.objects.create(normal=n3), C2.objects.create(normal=n1)

        assert set(n1.polies.all()) == {p1, c2}
        assert set(n2.polies.all()) == {a1, b2}
        assert set(n3.polies.all()) == {a2, c1}
        assert set(n4.polies.all()) == {p2, b1}

        n2.delete()
        assert Poly2.objects.count() == 6
        assert a1 not in Poly2.objects.all()
        assert b2 not in Poly2.objects.all()

        Normal2.objects.filter(pk__in=[n1.pk, n4.pk]).delete()
        assert Poly2.objects.count() == 2
        assert p1 not in Poly2.objects.all()
        assert c2 not in Poly2.objects.all()
        assert p2 not in Poly2.objects.all()
        assert b1 not in Poly2.objects.all()
        n3.delete()
        assert Poly2.objects.count() == 0

    def test_polymorphic_deletion_scenario3(self):
        """
        Scenario 3

        Normal3
        |
        Poly3
        | \
        A3 B3

        Deleting Poly3 should cascade delete Normal3 and deleting from Normal3 should
        cascade down to children.
        """

        from .models import (
            Normal3,
            Poly3,
            A3,
            B3,
        )

        b1 = B3.objects.create()
        assert b1 in Poly3.objects.all()
        Normal3.objects.filter(pk=b1.pk).delete()
        assert b1 not in Poly3.objects.all()
        assert Poly3.objects.count() == 0

        b2 = B3.objects.create()
        assert Normal3.objects.filter(pk=b2.pk).exists()
        assert b2 in Poly3.objects.all()
        b2.delete()
        assert not Normal3.objects.filter(pk=b2.pk).exists()
        assert Poly3.objects.count() == 0

    def test_polymorphic_deletion_scenario4(self):
        """
        Scenario 4 - M2Ms between normal/poly models

                <--- cascade --->
        Normal4 <----- M2M ----->  Poly4
                                  /  |  \
                               A4   B4   C4

        Ensure relations are appropriately cascaded on deletions from either side.
        """

        from .models import (
            Normal4,
            Poly4,
            A4,
            B4,
            C4,
        )

        n1, n2, n3, n4 = (
            Normal4.objects.create(),
            Normal4.objects.create(),
            Normal4.objects.create(),
            Normal4.objects.create(),
        )

        p1, p2 = Poly4.objects.create(), Poly4.objects.create()
        a1, a2 = A4.objects.create(), A4.objects.create()
        b1, b2 = B4.objects.create(), B4.objects.create()
        c1, c2 = C4.objects.create(), C4.objects.create()

        n1.polies.add(p1, a1, b1, c1)
        n2.polies.add(p2, a2, b2, c2)
        n3.polies.add(b1, c1)
        n4.polies.add(p2, c2)

        assert set(n1.polies.all()) == {p1, a1, b1, c1}
        assert set(n2.polies.all()) == {p2, a2, b2, c2}
        assert set(n3.polies.all()) == {b1, c1}
        assert set(n4.polies.all()) == {p2, c2}

        a1.delete()
        assert set(n1.polies.all()) == {p1, b1, c1}
        assert set(n2.polies.all()) == {p2, a2, b2, c2}
        assert set(n3.polies.all()) == {b1, c1}
        assert set(n4.polies.all()) == {p2, c2}

        n4.delete()
        assert set(n1.polies.all()) == {p1, b1, c1}
        assert set(n2.polies.all()) == {p2, a2, b2, c2}
        assert set(n3.polies.all()) == {b1, c1}
        assert set(p2.normals.all()) == {n2}
        assert set(c2.normals.all()) == {n2}

        Poly4.objects.all().delete()
        assert n1.polies.count() == 0
        assert n2.polies.count() == 0
        assert n3.polies.count() == 0

    def test_polymorphic_deletion_scenario4_1(self):
        """
        Scenario 4 - M2Ms between normal/poly models

                  <--- cascade --->
        Normal4_1 <----- M2M ----->  Poly4
                                    /  |  \
                                  A4   B4   C4

        Ensure relations are appropriately cascaded on deletions from either side.
        """

        from .models import (
            Normal4_1,
            Poly4_1,
            A4_1,
            B4_1,
            C4_1,
        )

        n1, n2, n3, n4 = (
            Normal4_1.objects.create(),
            Normal4_1.objects.create(),
            Normal4_1.objects.create(),
            Normal4_1.objects.create(),
        )

        p1, p2 = Poly4_1.objects.create(), Poly4_1.objects.create()
        a1, a2 = A4_1.objects.create(), A4_1.objects.create()
        b1, b2 = B4_1.objects.create(), B4_1.objects.create()
        c1, c2 = C4_1.objects.create(), C4_1.objects.create()

        n1.polies.add(p1, a1, b1, c1)
        n2.polies.add(p2, a2, b2, c2)
        n3.polies.add(b1, c1)
        n4.polies.add(p2, c2)

        assert set(n1.polies.all()) == {p1, a1, b1, c1}
        assert set(n2.polies.all()) == {p2, a2, b2, c2}
        assert set(n3.polies.all()) == {b1, c1}
        assert set(n4.polies.all()) == {p2, c2}

        a1.delete()
        assert set(n1.polies.all()) == {p1, b1, c1}
        assert set(n2.polies.all()) == {p2, a2, b2, c2}
        assert set(n3.polies.all()) == {b1, c1}
        assert set(n4.polies.all()) == {p2, c2}

        n4.delete()
        assert set(n1.polies.all()) == {p1, b1, c1}
        assert set(n2.polies.all()) == {p2, a2, b2, c2}
        assert set(n3.polies.all()) == {b1, c1}
        assert set(p2.normals.all()) == {n2}
        assert set(c2.normals.all()) == {n2}

        Poly4_1.objects.all().delete()
        assert n1.polies.count() == 0
        assert n2.polies.count() == 0
        assert n3.polies.count() == 0

    def test_polymorphic_deletion_scenario5(self):
        """
        Scenario 5 - scenario3 with custom/different PKs

        Normal5
        |
        Poly5
        | \
        A5 B5

        Deleting Poly5 should cascade delete Normal5 and deleting from Normal5 should
        cascade down to children.
        """

        from .models import (
            Normal5,
            Poly5,
            A5,
            B5,
        )

        b1 = B5.objects.create()
        assert b1 in Poly5.objects.all()
        Normal5.objects.filter(pk=b1.pk).delete()
        assert b1 not in Poly5.objects.all()
        assert Poly5.objects.count() == 0

        b2 = B5.objects.create()
        assert Normal5.objects.filter(pk=b2.pk).exists()
        assert b2 in Poly5.objects.all()
        b2.delete()
        assert not Normal5.objects.filter(pk=b2.pk).exists()
        assert Poly5.objects.count() == 0

        # FIXME: django-polymorphic assumes all rows share the same PK value
        # n = Normal5.objects.create(n_pk=100)
        # p = Poly5.objects.create_from_super(n, p_pk=200)
        # A5.objects.create_from_super(p, a_pk=300)
        # b = B5.objects.create_from_super(p, b_pk=400)
        # assert Poly5.objects.count() == 1
        # assert b in Poly5.objects.all()
        # Normal5.objects.filter(pk=n.pk).delete()
        # assert Poly5.objects.count() == 0

        # n1 = Normal5.objects.create(n_pk=101)
        # p1 = Poly5.objects.create_from_super(n1, p_pk=201)
        # A5.objects.create_from_super(p1, a_pk=301)
        # b1 = B5.objects.create_from_super(p1, b_pk=401)
        # assert Poly5.objects.count() == 1
        # assert b1 in Poly5.objects.all()
        # b1.delete()
        # assert Poly5.objects.count() == 0
        # assert Normal5.objects.count() == 0

    def test_raw_delete_results(self):
        """
        Test what happens when you delete a child row with raw SQL then try to access
        polymorphic objects.

        With best effort approach, when a polymorphic_ctype_id points to a non-existing
        derived row, the parent object is returned instead of being filtered out.
        """
        from .models import Poly1, A1

        a1 = A1.objects.create(some_data="test")
        p1 = Poly1.objects.non_polymorphic().get(pk=a1.pk)
        p2 = Poly1.objects.create()

        with connection.cursor() as cursor:
            cursor.execute(
                f"DELETE FROM {A1._meta.db_table} WHERE {A1._meta.pk.column} = %s", [a1.pk]
            )

        # Best effort: parent object is returned when child is deleted via raw SQL
        result = list(Poly1.objects.all())
        assert len(result) == 2
        assert p2 in result
        # p1 is returned as Poly1 (parent) since A1 (child) was deleted
        assert any(
            obj.pk == p1.pk and isinstance(obj, Poly1) and not isinstance(obj, A1)
            for obj in result
        )

        assert set(Poly1.objects.non_polymorphic().all()) == {p1, p2}

        p1_fetched = Poly1.objects.non_polymorphic().get(pk=a1.pk)
        assert p1_fetched.get_real_instance().__class__ is Poly1

    def test_delete_keep_parents(self):
        """
        Test that delete(keep_parents=True) works as expected in polymorphic models
        by updating the relevant parent row ctypes.
        """
        from .models import Poly3, A3, B3, Normal3

        a1 = A3.objects.create()
        b1 = B3.objects.create()
        p1 = Poly3.objects.create()
        Normal3.objects.create()
        a1_pk = a1.pk
        b1_pk = b1.pk
        p1_pk = p1.pk

        a1.delete(keep_parents=True)
        assert A3.objects.count() == 0
        assert B3.objects.count() == 1
        assert Poly3.objects.count() == 3
        assert Normal3.objects.count() == 4
        assert Poly3.objects.get(pk=a1_pk).__class__ is Poly3

        p1.delete(keep_parents=True)
        assert A3.objects.count() == 0
        assert B3.objects.count() == 1
        assert Poly3.objects.count() == 2
        assert Normal3.objects.count() == 4
        assert Normal3.objects.get(pk=p1_pk).__class__ is Normal3

        # deleting an instance with more derived tables from a class higher up in its
        # hierarchy will delete all child rows below that level.
        b1_base = Poly3.objects.non_polymorphic().get(pk=b1_pk)
        b1_base.delete(keep_parents=True)
        assert A3.objects.count() == 0
        assert B3.objects.count() == 0
        assert Poly3.objects.count() == 1
        assert Normal3.objects.count() == 4
        assert Normal3.objects.get(pk=b1_pk).__class__ is Normal3
        assert not Poly3.objects.filter(pk=b1_pk).exists()

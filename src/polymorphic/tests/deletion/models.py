from django.db import models
from django.conf import settings
from polymorphic.models import PolymorphicModel
from polymorphic.deletion import PolymorphicGuard
from decimal import Decimal


def project_directory_path(instance, filename):
    # just to satisfy upload_to; keep it deterministic for tests
    return f"p{instance.dataset_folder.prjct_id}/{filename}"


CASCADE = models.CASCADE


class Standalone(models.Model):
    pass


class PlainA(models.Model):
    standalone_parent = models.ForeignKey(
        Standalone, on_delete=CASCADE, null=True, default=None, related_name="plainas"
    )


class PlainB1(PlainA):
    standalones = models.ManyToManyField(Standalone)


class PlainB2(PlainA):
    standalone = models.ForeignKey(
        Standalone, on_delete=CASCADE, null=True, default=None, related_name="plainb2s"
    )


class PlainC1(PlainB1):
    standalone = models.ForeignKey(
        Standalone, on_delete=CASCADE, null=True, default=None, related_name="plainc1s"
    )


class RelatedToChild(models.Model):
    child = models.ForeignKey(
        "Child", on_delete=CASCADE, null=True, default=None, related_name="relatives"
    )


class Base(models.Model):
    pass


class Child(Base):
    pass


class GrandChild(Child):
    pass


class RelatedToGrandChild(models.Model):
    grand_child = models.ForeignKey(
        GrandChild, on_delete=CASCADE, null=True, default=None, related_name="grand_relatives"
    )


###########################################################

"""
Scenario 1

        <-- cascade --
Normal1 ----- FK ---->  Poly1
                       /  |  \
                     A1   B1   C1
"""


class Normal1(models.Model):
    poly = models.ForeignKey("Poly1", on_delete=models.CASCADE)  # <-- this is fine


class Poly1(PolymorphicModel):
    pass


class A1(Poly1):
    pass


class B1(Poly1):
    pass


class C1(Poly1):
    pass


"""
Scenario 2

        -- cascade -->
Normal2 <----- FK ----  Poly2
                       /  |  \
                     A2   B2   C2
"""


class Normal2(models.Model):
    pass


class Poly2(PolymorphicModel):
    normal = models.ForeignKey(Normal2, on_delete=CASCADE, related_name="polies")


class A2(Poly2):
    pass


class B2(Poly2):
    pass


class C2(Poly2):
    pass


"""
Scenario 3

Normal3
  |
 Poly3
  | \
  A3 B3
"""


class Normal3(models.Model):
    pass


class Poly3(PolymorphicModel, Normal3):
    pass


class A3(Poly3):
    pass


class B3(Poly3):
    pass


"""
Scenario 4

        <--- cascade --->
Normal4 <----- M2M ----->  Poly4
                          /  |  \
                        A4   B4   C4
"""


class Normal4(models.Model):
    pass


class Poly4(PolymorphicModel):
    normals = models.ManyToManyField(Normal4, related_name="polies", blank=True)


class A4(Poly4):
    pass


class B4(Poly4):
    pass


class C4(Poly4):
    pass


class Normal4_1(models.Model):
    polies = models.ManyToManyField("Poly4_1", related_name="normals", blank=True)


class Poly4_1(PolymorphicModel):
    pass


class A4_1(Poly4_1):
    pass


class B4_1(Poly4_1):
    pass


class C4_1(Poly4_1):
    pass


"""
Scenario 5 - scenario3 with custom/different PKs

Normal3
  |
 Poly3
  | \
  A3 B3
"""


class Normal5(models.Model):
    n_pk = models.AutoField(primary_key=True)


class Poly5(PolymorphicModel, Normal5):
    p_pk = models.AutoField(primary_key=True)


class A5(Poly5):
    a_pk = models.AutoField(primary_key=True)


class B5(Poly5):
    b_pk = models.AutoField(primary_key=True)


########################################################################################
# There were 15 years of deletion bug reports - many were duplicates but many also
# included example models. We copy all of these provided tests in here not being too
# concerned about redundancy - we just want to make sure we don't regress on any of
# them. Each block is tagged with the root issue. In some cases we mirror the setup
# with a plain django model parallel - mostly for debug/comparison purposes

###########################################################
# https://github.com/jazzband/django-polymorphic/issues/160


class A_160(models.Model):
    pass


class B_160(PolymorphicModel):
    a = models.ForeignKey(A_160, on_delete=CASCADE)


class B1_160(B_160):
    pass


class B2_160(B_160):
    pass


class C_160(models.Model):
    b = models.ForeignKey(B1_160, on_delete=CASCADE)


# Plain
class A_160Plain(models.Model):
    pass


class B_160Plain(models.Model):
    a = models.ForeignKey(A_160Plain, on_delete=CASCADE)


class B1_160Plain(B_160Plain):
    pass


class B2_160Plain(B_160Plain):
    pass


class C_160Plain(models.Model):
    # test that guard misapplication is fine
    b = models.ForeignKey(B1_160Plain, on_delete=PolymorphicGuard(CASCADE))


###########################################################
###########################################################
# https://github.com/jazzband/django-polymorphic/issues/229


class Farm(models.Model):
    pass


class Animal(PolymorphicModel):
    farm = models.ForeignKey(
        "Farm", on_delete=PolymorphicGuard(models.CASCADE), related_name="animals"
    )
    name = models.CharField(max_length=100)


class Dog(Animal):
    dog_param = models.CharField(max_length=100)


class Cat(Animal):
    cat_param = models.CharField(max_length=100)


###########################################################
# https://github.com/jazzband/django-polymorphic/issues/274


class A_274(PolymorphicModel):
    pass


class B_274(A_274):
    pass


class D_274(A_274):
    pass


class E_274(D_274):
    pass


class C_274(B_274):
    pass


###########################################################
###########################################################
# https://github.com/jazzband/django-polymorphic/issues/357


class Order(models.Model):
    title = models.CharField("Title", max_length=200)

    class Meta:
        ordering = ("title",)

    def __str__(self):
        return self.title


class Payment(PolymorphicModel):
    order = models.ForeignKey(Order, on_delete=CASCADE)
    amount = models.DecimalField(default=Decimal(0.0), blank=True, max_digits=10, decimal_places=2)
    index = models.PositiveIntegerField(default=0, blank=False)

    class Meta:
        ordering = ("index",)


class CreditCardPayment(Payment):
    card_type = models.CharField(max_length=32)


class Beneficiary(models.Model):
    firstname = models.CharField(max_length=100)
    lastname = models.CharField(max_length=100)


class SepaPayment(Payment):
    iban = models.CharField(max_length=34)
    bic = models.CharField(max_length=11)
    beneficiaries = models.ManyToManyField(Beneficiary, "sepa", blank=True)


###########################################################
###########################################################
# https://github.com/jazzband/django-polymorphic/issues/481

# no example given - how to?


###########################################################
###########################################################
# https://github.com/jazzband/django-polymorphic/issues/540


class A_540(PolymorphicModel):
    self_referential = models.ForeignKey("self", null=True, blank=True, on_delete=CASCADE)


class B_540(A_540):
    name = models.CharField(max_length=256)


###########################################################
###########################################################
# https://github.com/jazzband/django-polymorphic/issues/547


class CustomModel(models.Model):
    pass


class Project(CustomModel):
    name = models.CharField(max_length=30)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)


class DatasetFolder(CustomModel):
    prjct = models.ForeignKey(Project, on_delete=CASCADE)


class OriginalFile(PolymorphicModel, CustomModel):
    dataset_folder = models.ForeignKey(DatasetFolder, on_delete=CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    content_type = models.CharField(max_length=100)
    size = models.PositiveIntegerField()


class DatasetRelation(OriginalFile):
    file = models.FileField(max_length=500, upload_to=project_directory_path)
    original_file_name = models.CharField(max_length=100)


class OriginalDataset(OriginalFile):
    dataset_relation = models.ForeignKey(
        DatasetRelation, on_delete=models.SET_NULL, blank=True, null=True
    )
    file = models.FileField(max_length=500, upload_to=project_directory_path)
    original_file_name = models.CharField(max_length=100, null=True, blank=True)
    table_name = models.CharField(max_length=100, null=True, blank=True)
    rows_number = models.PositiveIntegerField()
    dataset_metadata = models.JSONField()


class OriginalImage(OriginalFile):
    original_file_name = models.CharField(max_length=100)
    file = models.FileField(max_length=500, upload_to=project_directory_path)


###########################################################
###########################################################
# https://github.com/jazzband/django-polymorphic/issues/608


class PolyDevice(models.Model):
    name = models.CharField(max_length=64)


class PolyInterface(PolymorphicModel):
    name = models.CharField(max_length=64)
    device = models.ForeignKey(to=PolyDevice, on_delete=CASCADE)


class PolyEthernetInterface(PolyInterface):
    ethernety_stuff = models.CharField(max_length=64)


class PolyModularInterface(PolyEthernetInterface):
    modular_stuff = models.CharField(max_length=64)


class PolyFixedInterface(PolyEthernetInterface):
    fixed_stuff = models.CharField(max_length=64)


class PolyWirelessInterface(PolyInterface):
    wirelessy_stuff = models.CharField(max_length=64)


class PolyFCInterface(PolyInterface):
    fc_stuff = models.CharField(max_length=64)


class Poll(models.Model):
    pass


class Question(models.Model):
    poll = models.ForeignKey(to=Poll, on_delete=CASCADE)


class Answer(PolymorphicModel):
    question = models.ForeignKey(to=Question, on_delete=CASCADE)


class TextAnswer(Answer):
    answer = models.CharField(default="", blank=True, max_length=500)


class YesNoAnswer(Answer):
    answer = models.BooleanField("answer", default=False)

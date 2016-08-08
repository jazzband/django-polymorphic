from django.db import models
from django.utils.dates import MONTHS_3
from django.utils.six import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _

from polymorphic.models import PolymorphicModel


@python_2_unicode_compatible
class Order(models.Model):
    """
    An example order that has polymorphic relations
    """
    title = models.CharField(_("Title"), max_length=200)

    class Meta:
        verbose_name = _("Organisation")
        verbose_name_plural = _("Organisations")
        ordering = ('title',)

    def __str__(self):
        return self.title


@python_2_unicode_compatible
class Payment(PolymorphicModel):
    """
    A generic payment model.
    """
    order = models.ForeignKey(Order)
    currency = models.CharField(default='USD', max_length=3)
    amount = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        verbose_name = _("Payment")
        verbose_name_plural = _("Payments")

    def __str__(self):
        return "{0} {1}".format(self.currency, self.amount)


class CreditCardPayment(Payment):
    """
    Credit card
    """
    MONTH_CHOICES = [(i, n) for i, n in sorted(MONTHS_3.items())]

    card_type = models.CharField(max_length=10)
    expiry_month = models.PositiveSmallIntegerField(choices=MONTH_CHOICES)
    expiry_year = models.PositiveIntegerField()

    class Meta:
        verbose_name = _("Credit Card Payment")
        verbose_name_plural = _("Credit Card Payments")


class BankPayment(Payment):
    """
    Payment by bank
    """
    bank_name = models.CharField(max_length=100)
    swift = models.CharField(max_length=20)

    class Meta:
        verbose_name = _("Bank Payment")
        verbose_name_plural = _("Bank Payments")


class SepaPayment(Payment):
    """
    Payment by SEPA (EU)
    """
    iban = models.CharField(max_length=34)
    bic = models.CharField(max_length=11)

    class Meta:
        verbose_name = _("SEPA Payment")
        verbose_name_plural = _("SEPA Payments")

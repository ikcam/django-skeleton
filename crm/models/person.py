from django.db import models
from django.db.models import Sum
from django.core.exceptions import ValidationError
from django.urls import reverse_lazy
from django.utils.functional import cached_property
from django.utils.translation import ugettext_lazy as _

from localflavor.us.models import USStateField, USZipCodeField

from account.models import User
from core.mixins import AuditableMixin
from core.constants import PERSON_CUSTOMER, PERSON_LEAD
from core.utils import phone_clean


class Person(AuditableMixin):
    PERSON_CHOICES = (
        (PERSON_LEAD, _("Lead")),
        (PERSON_CUSTOMER, _("Customer")),
    )

    company = models.ForeignKey(
        'core.Company', editable=False, on_delete=models.CASCADE,
        verbose_name=_("Company")
    )
    user = models.ForeignKey(
        User, blank=True, null=True, on_delete=models.SET_NULL,
        verbose_name=_("User")
    )
    type = models.SlugField(
        choices=PERSON_CHOICES, default=PERSON_LEAD, editable=False,
        verbose_name=_("Type")
    )
    company_name = models.CharField(
        max_length=75, blank=True, null=True, verbose_name=_("Company name")
    )
    first_name = models.CharField(
        max_length=75, blank=True, null=True, verbose_name=_("First name")
    )
    last_name = models.CharField(
        max_length=75, blank=True, null=True, verbose_name=_("Last name")
    )
    full_name = models.CharField(
        max_length=250, editable=False, verbose_name=_("Full name")
    )
    email = models.EmailField(
        blank=True, null=True, verbose_name=_("Email")
    )
    cellphone = models.CharField(
        max_length=20, blank=True, null=True, verbose_name=_("Cellphone")
    )
    phone_number = models.CharField(
        max_length=20, blank=True, null=True, verbose_name=_("Phone number")
    )
    address = models.TextField(
        blank=True, null=True, verbose_name=_("Address")
    )
    address_2 = models.TextField(
        blank=True, null=True, verbose_name=_("Address 2")
    )
    city = models.CharField(
        max_length=50, blank=True, null=True, verbose_name=_("City")
    )
    state = USStateField(
        blank=True, null=True, verbose_name=_("State")
    )
    zip_code = USZipCodeField(
        blank=True, verbose_name=_("Zip code")
    )
    send_sms = models.BooleanField(
        default=True, editable=False, verbose_name=_("Send SMS")
    )
    send_email = models.BooleanField(
        default=True, editable=False, verbose_name=_("Send email")
    )
    source = models.ForeignKey(
        'crm.Source', blank=True, null=True,
        on_delete=models.SET_NULL, verbose_name=_("Source")
    )
    website = models.URLField(
        blank=True, null=True, verbose_name=_("Website")
    )

    class Meta:
        ordering = ['full_name', ]
        verbose_name = _("Person")
        verbose_name_plural = _("Persons")

    def __str__(self):
        if self.first_name and self.last_name:
            return "%s %s" % (self.first_name, self.last_name)
        elif self.first_name:
            return "%s" % self.first_name
        elif self.last_name:
            return "%s" % self.last_name
        elif self.company_name:
            return "%s" % self.company_name

    def get_absolute_url(self):
        if self.type == PERSON_CUSTOMER:
            return reverse_lazy('crm:customer_detail', args=[self.pk, ])
        else:
            return reverse_lazy('crm:lead_detail', args=[self.pk, ])

    @property
    def actions(self):
        return [
            (_("Change"), 'change', 'success', 'pencil'),
            (_("Delete"), 'delete', 'danger', 'trash'),
        ]

    def save(self, *args, **kwargs):
        if self.first_name and self.last_name:
            self.full_name = '%s %s' % (self.first_name, self.last_name)
        elif self.first_name:
            self.full_name = '%s' % self.first_name
        elif self.last_name:
            self.full_name = '%s' % self.last_name

        self.full_name = self.full_name.strip()

        if self.full_name and self.company_name:
            self.full_name += ' - %s' % self.company_name
        elif self.company_name:
            self.full_name = '%s' % self.company_name

        if not self.full_name:
            raise ValidationError(_("Can't save without any name."))

        self.phone_number = phone_clean(self.phone_number)
        self.cellphone = phone_clean(self.cellphone)

        return super().save(*args, **kwargs)

    @property
    def full_address(self):
        address = ''
        if self.address:
            address += '%s' % self.address
        if self.address_2:
            address += ' %s' % self.address_2
        if self.city:
            address += '\n%s' % self.city
        if self.state:
            address += ', %s' % self.state
        if self.zip_code:
            address += ' %s' % self.zip_code
        return address

    @property
    def items(self):
        from .item import Item
        return Item.objects.filter(invoice__person=self)

    @property
    def payments(self):
        from .payment import Payment
        return Payment.objects.filter(invoice__person=self)

    @cached_property
    def total_invoices(self):
        total = self.items.all().aggregate(Sum('subtotal'))['subtotal__sum']
        return round(total or 0, 2)

    @cached_property
    def total_payments(self):
        total = self.payments.all().aggregate(Sum('total'))['total__sum']
        return round(total or 0, 2)

    @cached_property
    def balance(self):
        total = float(self.total_invoices) - float(self.total_payments)
        return round(total, 2)

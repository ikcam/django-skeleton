from datetime import timedelta

from django.db import models
from django.db.models import Sum
from django.urls import reverse_lazy
from django.utils import timezone
from django.utils.functional import cached_property
from django.utils.translation import ugettext_lazy as _

from core.constants import GRACE_DAYS
from core.mixins import AuditableMixin
from . import culqipy


class Invoice(AuditableMixin, models.Model):
    company = models.ForeignKey(
        'core.Company', on_delete=models.CASCADE,
        verbose_name=_("Company")
    )
    description = models.TextField(
        blank=True, null=True, verbose_name=_("Description")
    )
    aditional_fees = models.DecimalField(
        max_digits=10, decimal_places=2, default=0,
        verbose_name=_("Aditional fees")
    )
    subtotal = models.DecimalField(
        max_digits=10, decimal_places=2, editable=False,
        verbose_name=_("Subtotal")
    )

    class Meta:
        ordering = ['-date_creation', ]
        verbose_name = _("Invoice")
        verbose_name_plural = _("Invoices")

    def __str__(self):
        return "#%06d" % self.id

    def get_absolute_url(self):
        return reverse_lazy('public:invoice_detail', args=[self.pk, ])

    def action_list(self):
        return ('view', )

    def create_payment_from_culqi(self, token, email):
        dir_charge = {
            'amount': self.culqi_amount,
            "capture": True,
            'currency_code': 'USD',
            'description': self.description,
            'email': email,
            'installments': 0,
            "source_id": token,
        }
        charge = culqipy.Charge.create(dir_charge)

        self.payment_set.create(
            description=charge['id'],
            total=float(charge['amount'] / 100)
        )

    @property
    def culqi_amount(self):
        return int(self.total_pending * 100)

    @property
    def date_expiration(self):
        return self.date_creation + timedelta(days=GRACE_DAYS)

    @property
    def is_expired(self):
        return timezone.now() > self.date_expiration

    @cached_property
    def is_paid(self):
        return self.total_pending == 0

    @property
    def total(self):
        total = float(self.aditional_fees) + float(self.subtotal)
        return round(total, 2)

    @cached_property
    def total_payments(self):
        total = self.payment_set.all().aggregate(Sum('total'))['total__sum']
        total = float(total or 0)
        return round(total, 2)

    @cached_property
    def total_pending(self):
        total = float(self.total) - float(self.total_payments)
        return round(total, 2)

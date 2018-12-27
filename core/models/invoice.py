from datetime import timedelta

from django.db import models
from django.db.models import Sum
from django.urls import reverse_lazy
from django.utils import timezone
from django.utils.functional import cached_property
from django.utils.translation import ugettext_lazy as _

from core.constants import GRACE_DAYS, LEVEL_ERROR, LEVEL_SUCCESS, MODULE_LIST
from core.mixins import AuditableMixin


class Invoice(AuditableMixin):
    company = models.ForeignKey(
        'core.Company', on_delete=models.PROTECT,
        related_name='core_invoice_set', db_index=True,
        verbose_name=_("company")
    )
    module = models.SlugField(
        choices=MODULE_LIST, blank=True, null=True, verbose_name=_("module")
    )
    description = models.TextField(
        blank=True, null=True, verbose_name=_("description")
    )
    total = models.DecimalField(
        max_digits=10, decimal_places=2, verbose_name=_("total")
    )

    class Meta:
        ordering = ['-date_creation', ]
        verbose_name = _("invoice")
        verbose_name_plural = _("invoices")

    def __str__(self):
        return "#%06d" % self.id

    @property
    def action_list(self):
        return ('view', 'pay', )

    @property
    def date_expiration(self):
        return self.date_creation + timedelta(days=GRACE_DAYS)

    def get_absolute_url(self):
        return reverse_lazy('public:invoice_detail', args=[self.pk, ])

    @property
    def is_expired(self):
        return timezone.now() > self.date_expiration

    @cached_property
    def is_paid(self):
        return self.total_pending == 0

    def pay(self, card, **kwargs):
        assert card in self.company.card_set.all(), _(
            "SECURITY BREACH. Invalid card."
        )

        response = card.charge(
            amount=self.total, description=self.description, **kwargs
        )

        if isinstance(response, str):
            return LEVEL_ERROR, response

        api, api_id, total = response

        self.payment_set.create(
            api=api,
            api_id=api_id,
            total=total,
        )
        return LEVEL_SUCCESS, _("Payment added successfully.")

    @cached_property
    def total_payments(self):
        if hasattr(self, '_total_payments'):
            return self._total_payments
        total = self.payment_set.all().aggregate(Sum('total'))['total__sum']
        total = float(total or 0)
        self._total_payments = round(total, 2)
        return self._total_payments

    @cached_property
    def total_pending(self):
        if hasattr(self, '_total_pending'):
            return self._total_pending
        total = float(self.total) - float(self.total_payments)
        return round(total, 2)
        self._total_pending = round(total, 2)
        return self._total_pending

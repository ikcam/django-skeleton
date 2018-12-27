from django.db import models
from django.db.models import signals
from django.utils.translation import ugettext_lazy as _

from core.mixins import AuditableMixin


class Payment(AuditableMixin):
    invoice = models.ForeignKey(
        'core.Invoice', editable=False, on_delete=models.CASCADE,
        db_index=True, verbose_name=_("invoice")
    )
    description = models.TextField(
        blank=True, null=True, verbose_name=_("description")
    )
    total = models.DecimalField(
        max_digits=12, decimal_places=2, verbose_name=_("total")
    )

    class Meta:
        ordering = ['-date_creation', ]
        verbose_name = _("payment")
        verbose_name_plural = _("payments")

    def __str__(self):
        return "%.2f" % self.total

    def get_absolute_url(self):
        return self.parent.get_absolute_url()

    @property
    def company(self):
        return self.parent.company

    @property
    def parent(self):
        return self.invoice


def post_save_payment(instance, sender, created, **kwargs):
    if instance.invoice.is_paid and not instance.company.is_active:
        instance.company.activate()


signals.post_save.connect(post_save_payment, sender=Payment)

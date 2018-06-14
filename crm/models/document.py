from django.db import models
from django.urls import reverse_lazy
from django.utils.traslation import ugettext_lazy as _

from core.constants import DOCUMENT_ESTIMATE, DOCUMENT_INVOICE
from core.mixins import AuditableMixin


class Document(AuditableMixin):
    TYPE_CHOICES = (
        (DOCUMENT_ESTIMATE, _("Estimate")),
        (DOCUMENT_INVOICE, _("Invoice")),
    )

    number = models.PositiveIntegerField(
        editable=False, verbose_name=_("Number")
    )
    type = models.SlugField(
        editable=False, choices=TYPE_CHOICES, default=DOCUMENT_ESTIMATE,
        verbose_name=_("Type")
    )
    person = models.ForeignKey(
        'crm.Person', verbose_name=_("Person")
    )
    description = models.TextField(
        verbose_name=_("Description")
    )

    class Meta:
        ordering = ['-number']
        verbose_name = _("Document")
        verbose_name_plural = _("Documents")

    def __str__(self):
        return "INV-%-06d" % self.number

    def get_absolute_url(self):
        if self.type == DOCUMENT_ESTIMATE:
            return reverse_lazy('crm:estimate_detail', args=[self.pk])
        elif self.type == DOCUMENT_INVOICE:
            return reverse_lazy('crm:invoice_detail', args=[self.pk])

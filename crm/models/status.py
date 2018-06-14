from django.db import models
from django.urls import reverse_lazy
from django.utils.translation import ugettext_lazy as _

from core.mixins import AuditableMixin


class Status(AuditableMixin):
    company = models.ForeignKey(
        'core.Company', on_delete=models.CASCADE, editable=False,
        verbose_name=_("Company")
    )
    name = models.CharField(
        max_length=50, verbose_name=_("Name")
    )
    description = models.TextField(
        blank=True, null=True, verbose_name=_("Description")
    )
    order = models.PositiveIntegerField(
        default=0, verbose_name=_("Order")
    )

    class Meta:
        ordering = ['order']
        verbose_name = _("Status")
        verbose_name_plural = _("Status")

    def __str__(self):
        return "%s" % self.name

    def get_absolute_url(self):
        return reverse_lazy('crm:status_detail', args=[self.pk])

    @property
    def actions(self):
        return (
            (_("Change"), 'change', 'success', 'pencil', 'crm:change_status'),
            (_("Delete"), 'delete', 'danger', 'trash', 'crm:delete_status'),
        )

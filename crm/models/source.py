from django.db import models
from django.urls import reverse_lazy
from django.utils.translation import ugettext_lazy as _

from core.mixins import AuditableMixin


class Source(AuditableMixin):
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

    class Meta:
        ordering = ['name']
        verbose_name = _("Source")
        verbose_name_plural = _("Sources")

    def __str__(self):
        return "%s" % self.name

    @property
    def actions(self):
        return (
            (
                _("Change"), 'change', 'success', 'pencil',
                'crm:change_source'
            ),
            (
                _("Delete"), 'delete', 'danger', 'trash',
                'crm:delete_source'
            ),
        )

    def get_absolute_url(self):
        return reverse_lazy('crm:source_detail', args=[self.pk])

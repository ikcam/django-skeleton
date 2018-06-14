from django.db import models
from django.urls import reverse_lazy
from django.utils.translation import ugettext_lazy as _

from core.mixins import AuditableMixin


class JobDescription(AuditableMixin):
    company = models.ForeignKey(
        'core.Company', on_delete=models.CASCADE, editable=False,
        verbose_name=_("Company")
    )
    name = models.CharField(
        max_length=50, verbose_name=_("Name")
    )
    parent = models.ForeignKey(
        'self', blank=True, null=True, on_delete=models.CASCADE,
        verbose_name=_("Parent")
    )
    description = models.TextField(
        blank=True, null=True, verbose_name=_("Description")
    )

    class Meta:
        ordering = ['name']
        verbose_name = _("Job description")
        verbose_name_plural = _("Job descriptions")

    def __str__(self):
        return "%s" % self.name

    @property
    def actions(self):
        return (
            (
                _("Change"), 'change', 'success', 'pencil',
                'crm:change_jobdescription'
            ),
            (
                _("Delete"), 'delete', 'danger', 'trash',
                'crm:delete_jobdescription'
            ),
        )

    def get_absolute_url(self):
        return reverse_lazy('crm:jobdescription_detail', args=[self.pk])

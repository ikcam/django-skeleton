from django.db import models
from django.urls import reverse_lazy
from django.utils.translation import ugettext_lazy as _

from core.mixins import AuditableMixin


class Opportunity(AuditableMixin):
    company = models.ForeignKey(
        'core.Company', on_delete=models.CASCADE, editable=False,
        verbose_name=_("Company")
    )
    user = models.ForeignKey(
        'account.User', on_delete=models.SET_NULL, blank=True, null=True,
        verbose_name=_("User")
    )
    person = models.ForeignKey(
        'crm.Person', on_delete=models.CASCADE, verbose_name=_("Person")
    )
    number = models.PositiveIntegerField(
        default=1001, editable=False, verbose_name=_("Number")
    )
    job_description = models.ForeignKey(
        'crm.JobDescription', on_delete=models.CASCADE,
        verbose_name=_("Job description")
    )
    square_feet = models.PositiveIntegerField(
        default=0, verbose_name=_("Square feet")
    )
    description = models.TextField(
        blank=True, null=True, verbose_name=_("Description")
    )
    details = models.TextField(
        blank=True, null=True, verbose_name=_("Details")
    )
    price = models.DecimalField(
        max_digits=12, decimal_places=2, verbose_name=_("Price")
    )

    class Meta:
        ordering = ['-number']
        verbose_name = _("Opportunity")
        verbose_name_plural = _("Opportunities")

    def __str__(self):
        return "OPT-%-06d" % self.number

    def get_absolute_url(self):
        return reverse_lazy('crm:opportunity_detail', args=[self.pk])

    @property
    def actions(self):
        return (
            (
                _("Change"), 'change', 'success', 'pencil',
                'crm:change_opportunity'
            ),
            (
                _("Delete"), 'delete', 'danger', 'trash',
                'crm:delete_opportunity'
            ),
        )

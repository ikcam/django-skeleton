
from django.db import models
from django.urls import reverse_lazy
from django.utils.translation import ugettext_lazy as _

from core.mixins import AuditableMixin


class Role(AuditableMixin, models.Model):
    company = models.ForeignKey(
        'core.Company', editable=False, on_delete=models.CASCADE,
        verbose_name=_("Company")
    )
    name = models.CharField(
        max_length=50, verbose_name=_("Name")
    )
    permissions = models.ManyToManyField(
        'auth.Permission', blank=True, verbose_name=_("Permissions")
    )

    class Meta:
        ordering = ['name', ]
        verbose_name = _("Role")
        verbose_name_plural = _("Roles")

    def __str__(self):
        return "%s" % self.name

    def get_absolute_url(self):
        return reverse_lazy('public:role_list')

    def action_list(self):
        return ('change', 'delete')

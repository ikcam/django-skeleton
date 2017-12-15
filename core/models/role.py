from django.contrib.auth.models import Permission
from django.db import models
from django.urls import reverse_lazy
from django.utils.translation import ugettext_lazy as _

from core.mixins import AuditableMixin
from .company import Company


class Role(AuditableMixin, models.Model):
    company = models.ForeignKey(
        Company, editable=False, related_name='roles',
        on_delete=models.CASCADE, verbose_name=_("Company")
    )
    name = models.CharField(
        max_length=50, verbose_name=_("Name")
    )
    permissions = models.ManyToManyField(
        Permission, blank=True, verbose_name=_("Permissions")
    )

    class Meta:
        ordering = ['name', ]
        verbose_name = _("Role")
        verbose_name_plural = _("Roles")

    def __str__(self):
        return "%s" % self.name

    def get_absolute_url(self):
        return reverse_lazy('core:role_list')

    def actions(self):
        return (
            (_("Change"), 'change', 'success', 'pencil', 'core:change_role'),
            (_("Delete"), 'delete', 'danger', 'trash', 'core:delete_role'),
        )

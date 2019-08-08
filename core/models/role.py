
from django.db import models
from django.urls import reverse_lazy
from django.utils.translation import ugettext_lazy as _

from core.models.mixins import AuditableMixin, get_active_mixin


class Role(get_active_mixin(editable=True), AuditableMixin):
    company = models.ForeignKey(
        'core.Company', editable=False, on_delete=models.CASCADE,
        db_index=True, verbose_name=_("company")
    )
    name = models.CharField(
        max_length=50, verbose_name=_("name")
    )
    permissions = models.ManyToManyField(
        'auth.Permission', blank=True, verbose_name=_("permissions")
    )

    class Meta:
        ordering = ['name', ]
        verbose_name = _("role")
        verbose_name_plural = _("roles")

    def __str__(self):
        return "%s" % self.name

    def get_absolute_url(self):
        return reverse_lazy('panel:role_list')

    def action_list(self):
        return ('change', 'delete')

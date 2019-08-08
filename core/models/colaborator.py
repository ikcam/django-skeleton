from django.db import models
from django.utils.translation import ugettext_lazy as _

from core.models.mixins import AuditableMixin, get_active_mixin


class Colaborator(get_active_mixin(editable=True), AuditableMixin):
    user = models.ForeignKey(
        'core.User', on_delete=models.CASCADE,
        db_index=True, verbose_name=_("user")
    )
    company = models.ForeignKey(
        'core.Company', on_delete=models.CASCADE,
        db_index=True, verbose_name=_("company")
    )
    roles = models.ManyToManyField(
        'core.Role', blank=True, verbose_name=_("roles")
    )
    permissions = models.ManyToManyField(
        'auth.Permission', blank=True, verbose_name=_("permissions")
    )

    class Meta:
        ordering = ['user', ]
        unique_together = ('user', 'company')
        verbose_name = _("colaborator")
        verbose_name_plural = _("colaborators")

    def __str__(self):
        return str(self.user)

    def get_absolute_url(self):
        return self.parent.get_absolute_url()

    @property
    def parent(self):
        return self.user

from django.db import models
from django.utils.translation import ugettext_lazy as _


class Colaborator(models.Model):
    user = models.ForeignKey(
        'core.User', on_delete=models.CASCADE,
        verbose_name=_("User")
    )
    company = models.ForeignKey(
        'core.Company', on_delete=models.CASCADE,
        verbose_name=_("Company")
    )
    date_joined = models.DateTimeField(
        auto_now=True, verbose_name=_("Join date")
    )
    is_active = models.BooleanField(
        default=True, verbose_name=_("Active")
    )
    roles = models.ManyToManyField(
        'core.Role', blank=True, verbose_name=("Roles")
    )
    permissions = models.ManyToManyField(
        'auth.Permission', blank=True, verbose_name=_("Permissions")
    )

    class Meta:
        ordering = ['user', ]
        unique_together = ('user', 'company')
        verbose_name = _("Colaborator")
        verbose_name_plural = _("Colaborators")

    def __str__(self):
        return "%s" % self.user

    def get_absolute_url(self):
        return self.parent.get_absolute_url()

    @property
    def parent(self):
        return self.user

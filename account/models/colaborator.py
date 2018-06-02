from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.db import models
from django.utils.translation import ugettext_lazy as _

from core.models import Company, Role


User = get_user_model()


class Colaborator(models.Model):
    user = models.ForeignKey(
        User, editable=False, on_delete=models.CASCADE,
        verbose_name=_("User")
    )
    company = models.ForeignKey(
        Company, editable=False, related_name='users_all',
        on_delete=models.CASCADE, verbose_name=_("Company")
    )
    date_joined = models.DateTimeField(
        auto_now=True, verbose_name=_("Join date")
    )
    is_active = models.BooleanField(
        default=True, verbose_name=_("Active")
    )
    roles = models.ManyToManyField(
        Role, blank=True, verbose_name=("Roles")
    )
    permissions = models.ManyToManyField(
        Permission, blank=True, verbose_name=_("Permissions")
    )

    class Meta:
        ordering = ['user', ]
        unique_together = ('user', 'company')
        verbose_name = _("Colaborator")
        verbose_name_plural = _("Colaborators")

    def __str__(self):
        return "%s" % self.profile

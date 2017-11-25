from django.contrib.auth.models import Permission
from django.db import models
from django.utils.translation import ugettext_lazy as _

from core.models import Company, Role
from .profile import Profile


class Colaborator(models.Model):
    profile = models.ForeignKey(
        Profile, editable=False, verbose_name=_("Profile")
    )
    company = models.ForeignKey(
        Company, editable=False, related_name='users_all',
        verbose_name=_("Company")
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
        ordering = ['profile', ]
        unique_together = ('profile', 'company')
        verbose_name = _("Colaborator")
        verbose_name_plural = _("Colaborators")

    def __str__(self):
        return "%s" % self.profile

    @property
    def user(self):
        return self.profile.user

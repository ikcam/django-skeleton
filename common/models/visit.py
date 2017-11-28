from django.db import models
from django.utils.translation import ugettext_lazy as _

from core.mixins import AuditableMixin
from .link import Link


class Visit(AuditableMixin):
    link = models.ForeignKey(
        Link, editable=False, related_name='visits',
        verbose_name=_("Link")
    )
    ip_address = models.GenericIPAddressField(
        protocol='both', verbose_name=_("IP address")
    )

    class Meta:
        ordering = ['date_creation', ]
        verbose_name = _("Visit")
        verbose_name_plural = _("Visits")

    def __str__(self):
        return "%s" % self.ip_address

    def get_absolute_url(self):
        return self.parent.get_absolute_url()

    @property
    def company(self):
        return self.parent.company

    @property
    def parent(self):
        return self.link

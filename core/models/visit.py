import uuid

from django.db import models
from django.utils.translation import ugettext_lazy as _

from core.models.mixins import AuditableMixin


class Visit(AuditableMixin):
    id = models.UUIDField(
        default=uuid.uuid4, primary_key=True, editable=False,
        verbose_name=_("id")
    )
    link = models.ForeignKey(
        'core.Link', editable=False, on_delete=models.CASCADE,
        db_index=True, verbose_name=_("link")
    )
    ip_address = models.GenericIPAddressField(
        protocol='both', verbose_name=_("ip address")
    )

    class Meta:
        ordering = ['date_creation', ]
        verbose_name = _("visit")
        verbose_name_plural = _("visits")

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

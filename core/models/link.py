import hashlib
import random

from django.db import models
from django.urls import reverse_lazy
from django.utils.functional import cached_property
from django.utils.translation import ugettext_lazy as _

from core.mixins import AuditableMixin


class Link(AuditableMixin):
    company = models.ForeignKey(
        'core.Company', editable=False, on_delete=models.CASCADE,
        verbose_name=_("Company")
    )
    message = models.ForeignKey(
        'core.Message', editable=False, blank=True, null=True,
        on_delete=models.SET_NULL, verbose_name=_("Message")
    )
    user = models.ForeignKey(
        'core.User', editable=False, blank=True, null=True,
        on_delete=models.SET_NULL, verbose_name=_("User")
    )
    token = models.CharField(
        max_length=150, blank=True, null=True, editable=False,
        verbose_name=_("Token")
    )
    destination = models.URLField(
        verbose_name=_("Destination")
    )

    class Meta:
        ordering = ['-date_creation', ]
        verbose_name = _("Link")
        verbose_name_plural = _("Links")

    def __str__(self):
        if len(self.destination) > 30:
            return "%s..." % self.destination[:30]
        return self.destination

    def get_absolute_url(self):
        return reverse_lazy('public:link_detail', args=[self.pk, ])

    def get_public_url(self):
        if self.token:
            path = reverse_lazy(
                'public:link_public_token', args=[self.token, ]
            )
        else:
            path = reverse_lazy(
                'public:link_public_direct', args=[self.pk, ]
            )

        return '{0}{1}'.format(self.company.domain, path)

    @property
    def actions(self):
        if self.is_open:
            return

        return [
            (_("Change"), 'change', 'success', 'pencil', 'core:change_link'),
            (_("Delete"), 'delete', 'danger', 'trash', 'core:delete_link'),
        ]

    @cached_property
    def is_open(self):
        return self.total_visits > 0

    def token_generate(self):
        if self.token:
            return False

        salt = hashlib.sha1(
            str(random.random()).encode("utf-8")
        ).hexdigest()[:5]

        self.token = hashlib.sha1(
            salt.encode("utf-8") + 'link-{}'.format(self.pk).encode("utf-8")
        ).hexdigest()
        self.save()

        return True

    @cached_property
    def total_visits(self):
        return self.visits.all().count()

    def visit_create(self, ip_address):
        return self.visits.create(ip_address=ip_address)

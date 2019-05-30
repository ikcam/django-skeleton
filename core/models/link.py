import uuid

from django.db import models
from django.urls import reverse_lazy
from django.utils.functional import cached_property
from django.utils.translation import ugettext_lazy as _

from core.models.mixins import AuditableMixin, get_active_mixin


class Link(get_active_mixin(editable=True), AuditableMixin):
    id = models.UUIDField(
        default=uuid.uuid4, primary_key=True, editable=False,
        verbose_name=_("id")
    )
    company = models.ForeignKey(
        'core.Company', editable=False, on_delete=models.CASCADE,
        db_index=True, verbose_name=_("company")
    )
    message = models.ForeignKey(
        'core.Message', editable=False, blank=True, null=True,
        db_index=True, on_delete=models.SET_NULL, verbose_name=_("message")
    )
    user = models.ForeignKey(
        'core.User', editable=False, blank=True, null=True,
        db_index=True, on_delete=models.SET_NULL, verbose_name=_("user")
    )
    destination = models.URLField(
        verbose_name=_("destination")
    )

    class Meta:
        ordering = ['-date_creation', ]
        permissions = (
            ('view_all_link', 'Can view all link'),
        )
        verbose_name = _("link")
        verbose_name_plural = _("links")

    def __str__(self):
        if len(self.destination) > 30:
            return "%s..." % self.destination[:30]
        return self.destination

    def get_absolute_url(self):
        return reverse_lazy('panel:link_detail', args=[self.pk])

    def get_public_url(self, scheme=None, host=None):
        return '{scheme}://{domain}{path}'.format(
            scheme=scheme if scheme else 'https',
            domain=host if host else self.company.domain,
            path=reverse_lazy('public:link_detail', args=[self.pk])
        )

    @property
    def action_list(self):
        if self.is_open():
            return

        return ('change', 'delete')

    def is_open(self):
        return self.total_visits > 0
    is_open.boolean = True

    @cached_property
    def total_visits(self):
        return self.visit_set.all().count()

    def visit_create(self, ip_address, **kwargs):
        return self.visit_set.create(ip_address=ip_address)

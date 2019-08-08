from django.db import models
from django.urls import reverse_lazy
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.utils.translation import ugettext_lazy as _

from core.constants import LEVEL_ERROR
from core.models.mixins import AuditableMixin, get_active_mixin
from core.tokens import default_token_generator


class Invite(get_active_mixin(editable=True), AuditableMixin):
    company = models.ForeignKey(
        'core.Company', editable=False, on_delete=models.CASCADE,
        db_index=True, verbose_name=_("company")
    )
    name = models.CharField(
        max_length=50, verbose_name=_("name")
    )
    email = models.EmailField(
        verbose_name=_("email")
    )
    date_send = models.DateTimeField(
        blank=True, null=True, editable=False, verbose_name=_("sent date")
    )
    roles = models.ManyToManyField(
        'core.Role', blank=True, verbose_name=_("roles")
    )
    user = models.OneToOneField(
        'core.User', blank=True, null=True, editable=False,
        related_name='invite', on_delete=models.CASCADE,
        verbose_name=_("user")
    )

    class Meta:
        ordering = ['-date_creation']
        permissions = (
            ('send_invite', 'Can send invite'),
        )
        unique_together = ("company", "email")
        verbose_name = _("invite")
        verbose_name_plural = _("invites")

    def __str__(self):
        return self.email

    def get_absolute_url(self):
        return reverse_lazy('panel:invite_list')

    @property
    def action_list(self):
        return ('send', 'delete') if not self.user else None

    def is_send(self):
        return True if self.date_send else False
    is_send.boolean = True

    def send(self, scheme, host, **kwargs):
        if self.user:
            return LEVEL_ERROR, _("Invite was used already.")

        context = dict(
            object=self,
            scheme=scheme,
            host=host,
            uid=urlsafe_base64_encode(force_bytes(self.pk)),
            token=default_token_generator.make_token(self)
        )
        subject = _(
            "You have receive an invitation to join %(company)s"
        ) % dict(
            company=self.company
        )

        message = self.company.message_set.create_html_email(
            from_name=self.company.name,
            from_email=self.company.email,
            model=self,
            to_email=self.email,
            subject=subject,
            template_name='panel/invite/invite_email.html',
            context=context,
            user=kwargs.get('user', None),
        )
        return message.send(scheme=scheme, host=host)

import hashlib
import random

from django.contrib.auth.models import User
from django.db import models
from django.template.loader import get_template
from django.urls import reverse_lazy
from django.utils import timezone
from django.utils.translation import activate, ugettext_lazy as _

from core.mixins import AuditableMixin
from .company import Company


class Invite(AuditableMixin, models.Model):
    company = models.ForeignKey(
        Company, editable=False, related_name='invites',
        verbose_name=_("Company")
    )
    name = models.CharField(
        max_length=50, verbose_name=_("Name")
    )
    email = models.EmailField(
        verbose_name=_("Email")
    )
    date_send = models.DateTimeField(
        blank=True, null=True, editable=False, verbose_name=_("Sent date")
    )
    activation_key = models.CharField(
        max_length=255, blank=True, null=True, editable=False,
        verbose_name=_("Activation key")
    )
    user = models.OneToOneField(
        User, blank=True, null=True, editable=False, related_name='invite',
        verbose_name=_("User")
    )

    class Meta:
        ordering = ['-date_creation']
        permissions = (
            ('send_invite', 'Can send invite'),
        )
        unique_together = ("company", "email")
        verbose_name = _("Invite")
        verbose_name_plural = _("Invites")

    def __str__(self):
        return self.email

    def clean(self):
        super().clean()

        if not self.pk:
            self.key_generate()

    def get_absolute_url(self):
        return reverse_lazy('core:invite_list')

    @property
    def actions(self):
        if not self.user:
            return (
                (
                    _('Send'), 'send', 'info', 'envelope', 'core:send_invite'
                ),
                (
                    _('Delete'), 'delete', 'danger', 'trash',
                    'core:delete_invite'
                ),
            )

    @property
    def is_send(self):
        return True if self.date_send else False

    def key_generate(self):
        salt = hashlib.sha1(
            str(random.random()).encode("utf-8")
        ).hexdigest()[:5]

        self.activation_key = hashlib.sha1(
            salt.encode("utf-8") + 'invite-{}'.format(self.pk).encode("utf-8")
        ).hexdigest()

    def send(self):
        if self.user:
            return ('error', _("Invite was used already."))
        elif not self.activation_key:
            return ('error', _("Activation key not set. Contact support."))

        self.date_send = timezone.now()
        self.save()

        activate(self.company.language)

        content_template = get_template('core/invite_email.html')
        content = content_template.render({'object': self})
        subject = _(
            "You have receive an invitation to join %(company)s"
        ) % dict(
            company=self.company
        )

        message = self.company.messages.create(
            from_name=self.company.name,
            from_email=self.company.email,
            model=self,
            to_email=self.email,
            subject=subject,
            content=content,
        )
        return message._send()

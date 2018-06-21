import hashlib
import random

from django.db import models
from django.template.loader import get_template
from django.urls import reverse_lazy
from django.utils import timezone
from django.utils.translation import activate, ugettext_lazy as _

from core.constants import LEVEL_ERROR
from core.mixins import AuditableMixin


class Invite(AuditableMixin, models.Model):
    company = models.ForeignKey(
        'core.Company', editable=False, on_delete=models.CASCADE,
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
    roles = models.ManyToManyField(
        'core.Role', blank=True, verbose_name=_("Roles")
    )
    activation_key = models.CharField(
        max_length=255, blank=True, null=True, editable=False,
        verbose_name=_("Activation key")
    )
    user = models.OneToOneField(
        'core.User', blank=True, null=True, editable=False,
        related_name='invite', on_delete=models.CASCADE,
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

    def get_absolute_url(self):
        return reverse_lazy('public:invite_list')

    @property
    def action_list(self):
        if self.user:
            return
        return ('send', 'delete')

    @property
    def is_send(self):
        return True if self.date_send else False

    def key_generate(self):
        if self.activation_key:
            return

        salt = hashlib.sha1(
            str(random.random()).encode("utf-8")
        ).hexdigest()[:5]

        self.activation_key = hashlib.sha1(
            salt.encode("utf-8") + 'invite-{}'.format(self.pk).encode("utf-8")
        ).hexdigest()

    def send(self, **kwargs):
        if self.user:
            return (LEVEL_ERROR, _("Invite was used already."))

        self.key_generate()
        self.date_send = timezone.now()
        self.save(update_fields=['activation_key', 'date_send'])

        activate(self.company.language)

        content_template = get_template('public/invite_email.html')
        content = content_template.render({'object': self})
        subject = _(
            "You have receive an invitation to join %(company)s"
        ) % dict(
            company=self.company
        )

        message = self.company.message_set.create(
            from_name=self.company.name,
            from_email=self.company.email,
            model=self,
            to_email=self.email,
            subject=subject,
            content=content,
            user=kwargs.get('user', None),
        )
        return message.send()

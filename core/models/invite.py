import hashlib
import random

from django.conf import settings
from django.contrib.auth.models import User
from django.db import models
from django.db.models import signals
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from boilerplate.mail import SendEmail

from core import tasks
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
    date_sent = models.DateTimeField(
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
        unique_together = ("company", "email")
        verbose_name = _("Invite")
        verbose_name_plural = _("Invites")

    def __str__(self):
        return self.email

    def clean(self):
        super().clean()

        if not self.pk:
            self.key_generate()

    @property
    def actions(self):
        if not self.user:
            return (
                (_('Send'), 'send', 'info', 'envelope'),
                (_('Delete'), 'delete', 'danger', 'trash'),
            )

    def key_generate(self):
        salt = hashlib.sha1(
            str(random.random()).encode("utf-8")
        ).hexdigest()[:5]

        self.activation_key = hashlib.sha1(
            salt.encode("utf-8") + self.email.encode("utf-8")
        ).hexdigest()

    def send(self):
        if self.user:
            raise Exception(_("Invite was used already."))
        elif not self.activation_key:
            raise Exception(_("Activation key not set."))

        email = SendEmail(
            to=self.email,
            template_name_suffix='invite',
            subject=_("You have receive an invite to join %(company)s") % dict(
                company=self.company
            ),
        )
        email.add_context_data('object', self)
        response = email.send()

        if response > 0:
            self.date_sent = timezone.now()
            self.save()
            return True

        return False


def post_save_invite(sender, instance, created, **kwargs):
    if created:
        if settings.DEBUG:
            instance.send()
        else:
            tasks.invite_task.delay(instance.pk, 'send')


signals.post_save.connect(post_save_invite, sender=Invite)

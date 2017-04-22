from datetime import timedelta
import hashlib
import logging
import random

from django.conf import settings
from django.contrib.auth.models import User
from django.db import models
from django.db.models import signals
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from boilerplate.mail import SendEmail
from boilerplate.signals import add_view_permissions

from . import tasks


logger = logging.getLogger(__name__)


ACCOUNT_ACTIVATION_HOURS = 48


class Profile(models.Model):
    user = models.OneToOneField(
        User, primary_key=True, editable=False, related_name='profile',
        verbose_name=_('User')
    )
    activation_key = models.CharField(
        blank=True, null=True, max_length=255,
        editable=False, verbose_name=_("Activation key")
    )
    date_key_expiration = models.DateTimeField(
        blank=True, null=True,  editable=False,
        verbose_name=_("Date key expiration")
    )

    class Meta:
        ordering = ['user', ]
        verbose_name = _('Profile')
        verbose_name_plural = _('Profiles')

    def __str__(self):
        return '%s' % self.user

    def key_deactivate(self):
        if self.user.is_active:
            return False
        elif not self.activation_key or not self.date_key_expiration:
            return False
        elif timezone.now() > self.date_key_expiration:
            return False

        self.user.is_active = True
        self.user.save()

        self.activation_key = None
        self.date_key_expiration = None
        self.save()

        return True

    def key_generate(self):
        if self.user.is_active:
            return False
        elif (
            self.date_key_expiration and
            self.date_key_expiration > timezone.now()
        ):
            return False

        salt = hashlib.sha1(
            str(random.random()).encode("utf-8")
        ).hexdigest()[:5]

        self.activation_key = hashlib.sha1(
            salt.encode("utf-8") + self.user.email.encode("utf-8")
        ).hexdigest()
        self.date_key_expiration = (
            timezone.now() + timedelta(hours=ACCOUNT_ACTIVATION_HOURS)
        )
        self.save()

        if settings.DEBUG:
            self.key_send()
        else:
            tasks.profile_tasks.delay(self.pk, 'key_send')

        return True

    def key_send(self):
        email = SendEmail(
            to=self.user.email,
            template_name_suffix='key',
            subject=_("Activate your account"),
            is_html=True
        )
        email.add_context_data('object', self)
        response = email.send()

        if response > 0:
            return True
        return False


def user_str(self):
    if self.first_name and self.last_name:
        return '%s %s' % (self.first_name, self.last_name)
    else:
        return self.username


User.add_to_class('__str__', user_str)


def post_save_user(sender, instance, created, **kwargs):
    if created:
        Profile.objects.get_or_create(user=instance)

        if not instance.is_active:
            instance.profile.key_generate()


def pre_delete_creditcard(sender, instance, **kwargs):
    if instance.stripe_sid:
        instance.stripe_remove()


signals.post_save.connect(post_save_user, sender=User)
signals.post_migrate.connect(add_view_permissions)

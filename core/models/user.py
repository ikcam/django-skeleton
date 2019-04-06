from datetime import timedelta
import hashlib
import pytz
import random

from django.contrib.auth.models import AbstractUser, UserManager
from django.contrib.contenttypes.models import ContentType
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.db.models import signals
from django.urls import reverse_lazy
from django.utils import timezone
from django.utils.functional import cached_property
from django.utils.translation import ugettext_lazy as _

from boilerplate.mail import SendEmail
from boilerplate.signals import add_view_permissions
from rest_framework.authtoken.models import Token

from core.constants import (
    ACCOUNT_ACTIVATION_HOURS, LEVEL_ERROR, LEVEL_SUCCESS
)
from core import tasks


class UserManager(UserManager):
    pass


class User(AbstractUser):
    TIMEZONES = [(c, c) for c in pytz.common_timezones]

    activation_key = models.CharField(
        blank=True, null=True, max_length=255,
        editable=False, verbose_name=_("activation key")
    )
    companies = models.ManyToManyField(
        'core.Company', blank=True, through='Colaborator', related_name='+',
        verbose_name=_("companies")
    )
    date_key_expiration = models.DateTimeField(
        blank=True, null=True, editable=False,
        verbose_name=_("date key expiration")
    )
    facebook_id = models.CharField(
        max_length=100, editable=False, blank=True, null=True,
        verbose_name=_("facebook ID")
    )
    facebook_access_token = models.CharField(
        max_length=255, editable=False, blank=True, null=True,
        verbose_name=_("facebook access token")
    )
    language = models.SlugField(
        default=settings.LANGUAGE_CODE, choices=settings.LANGUAGES,
        verbose_name=_("language")
    )
    nav_expanded = models.BooleanField(
        default=True, verbose_name=_("nav expanded")
    )
    photo = models.ImageField(
        upload_to='core/users/', blank=True, null=True,
        verbose_name=_("photo")
    )
    timezone = models.CharField(
        max_length=100, default=settings.TIME_ZONE,
        choices=TIMEZONES, verbose_name=_("timezone")
    )
    objects = UserManager()

    class Meta:
        ordering = ['username', ]
        permissions = (
            ('remove_user', 'Can remove user'),
        )
        verbose_name = _('user')
        verbose_name_plural = _('user')

    def __str__(self):
        if self.first_name and self.last_name:
            return '%s %s' % (self.first_name, self.last_name)
        elif self.first_name:
            return self.first_name
        elif self.last_name:
            return self.last_name
        else:
            return self.username

    def get_absolute_url(self):
        return reverse_lazy('panel:user_list')

    def action_list(self):
        return ('change', )

    def as_colaborator(self, company):
        if any([self.is_staff, self.is_superuser]):
            colaborator, created = self.colaborator_set.get_or_create(
                company=company,
                defaults={'is_active': True}
            )
            return colaborator

        try:
            return self.colaborator_set.get(
                company=company,
                is_active=True
            )
        except ObjectDoesNotExist:
            return

    def can_activate(self):
        if self.is_active:
            return False
        elif not self.activation_key:
            return False
        elif timezone.now() > self.date_key_expiration:
            return False
        return True

    def company_remove(self, company, **kwargs):
        if company.user == self:
            return LEVEL_ERROR, _(
                "Can't remove from your own company."
            )

        # Remove from company list
        self.colaborator_set.get(company=company).delete()

        return LEVEL_SUCCESS, _(
            'User: "%(user)s" has been removed from %(company)s.'
        ) % dict(
            user=self,
            company=company,
        )

    def key_deactivate(self):
        if not self.can_activate():
            return False

        self.is_active = True
        self.activation_key = None
        self.date_key_expiration = None
        self.save(
            update_fields=[
                'is_active', 'activation_key', 'date_key_expiration'
            ]
        )

        return True

    def key_generate(self):
        if self.is_active:
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
            salt.encode("utf-8") + self.email.encode("utf-8")
        ).hexdigest()
        self.date_key_expiration = (
            timezone.now() + timedelta(hours=ACCOUNT_ACTIVATION_HOURS)
        )
        self.save(update_fields=['activation_key', 'date_key_expiration'])

        task = tasks.user_task

        if not settings.DEBUG:
            task = task.delay

        task(
            company_id=self.company,
            task='key_send',
            pk=self.pk
        )

        return True

    def key_send(self):
        email = SendEmail(
            to=self.email,
            template_name_suffix='key',
            subject=_("Activate your account"),
            is_html=True
        )
        email.add_context_data('object', self)
        return email.send()

    @cached_property
    def perms(self):
        if not self.company or not self.company.is_active:
            return []

        try:
            role_perms = self.colaborator_set \
                .get(company=self.company, is_active=True) \
                .roles.all() \
                .select_related('permissions__content_type') \
                .values(
                    'permissions__content_type__app_label',
                    'permissions__codename'
                )

            user_perms = self.colaborator_set \
                .get(company=self.company, is_active=True) \
                .permissions.all() \
                .select_related('content_type') \
                .values('content_type__app_label', 'codename')

            role_data = [
                '{}:{}'.format(
                    c['permissions__content_type__app_label'],
                    c['permissions__codename']
                ) for c in role_perms
            ]

            user_data = [
                '{}:{}'.format(
                    c['content_type__app_label'], c['codename']
                ) for c in user_perms
            ]

            return role_data + list(set(user_data) - set(role_data))
        except Exception:
            if settings.DEBUG:
                raise
            return []

    def add_notification(self, company, model, obj, response):
        level, content = response

        if hasattr(obj, 'pk'):
            self.notification_set.create(
                company=company,
                model=obj,
                level=level,
                content=content,
                destination=obj.get_absolute_url(),
            )
        else:
            ct = ContentType.objects.get(
                app_label=model._meta.app_label,
                model=model._meta.model_name
            )
            destination = reverse_lazy('{}:{}_list'.format(
                model._meta.app_label, model._meta.model_name
            ))
            self.notification_set.create(
                company=company,
                contenttype=ct,
                level=level,
                content=content,
                destination=destination,
            )

    def companies_available(self):
        return self.colaborator_set.filter(
            is_active=True
        ).exclude(company_id=self.company.pk)

    def notifications_unread(self):
        return self.notification_set.filter(
            company=self.company,
            date_read__isnull=True
        )

    def has_company_perm(self, perm, obj=None):
        if self.is_superuser:
            return True
        elif self.is_staff:
            return self.has_perm(perm, obj)
        elif self == self.company.user:
            return True

        return perm in self.perms

    def has_company_perms(self, perm_list, obj=None):
        if self.is_superuser:
            return True
        elif self.is_staff:
            return self.has_perms(perm_list, obj)
        elif self == self.company.user:
            return True

        return all(self.has_company_perm(perm, obj) for perm in perm_list)


def post_save_user(sender, instance, created, **kwargs):
    if created:
        Token.objects.get_or_create(user=instance)

        if not instance.is_active:
            instance.key_generate()


signals.post_save.connect(post_save_user, sender=User)
signals.post_migrate.connect(add_view_permissions)

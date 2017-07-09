from datetime import timedelta
import hashlib
import random
import pytz

from django.conf import settings
from django.contrib.auth.models import Permission, User
from django.db import models
from django.db.models import signals
from django.utils import timezone
from django.utils.functional import cached_property
from django.utils.translation import ugettext_lazy as _

from boilerplate.mail import SendEmail
from boilerplate.signals import add_view_permissions
from rest_framework.authtoken.models import Token

from . import tasks
from core.models import Company


ACCOUNT_ACTIVATION_HOURS = 48


class Profile(models.Model):
    TIMEZONES = [(c, c) for c in pytz.common_timezones]

    user = models.OneToOneField(
        User, primary_key=True, editable=False, related_name='profile',
        verbose_name=_('User')
    )
    company = models.ForeignKey(
        Company, blank=True, null=True, related_name='users_active',
        on_delete=models.SET_NULL, verbose_name=_("Company")
    )
    companies = models.ManyToManyField(
        Company, blank=True, through='Colaborator', verbose_name=_("Companies")
    )
    activation_key = models.CharField(
        blank=True, null=True, max_length=255,
        editable=False, verbose_name=_("Activation key")
    )
    date_key_expiration = models.DateTimeField(
        blank=True, null=True, editable=False,
        verbose_name=_("Date key expiration")
    )
    timezone = models.CharField(
        max_length=100, default=settings.TIME_ZONE,
        choices=TIMEZONES, verbose_name=_("Timezone")
    )

    class Meta:
        ordering = ['user', ]
        verbose_name = _('Profile')
        verbose_name_plural = _('Profiles')

    def __str__(self):
        return '%s' % self.user

    @property
    def companies_available(self):
        if self.user.is_staff:
            return Company.objects.all().exclude(pk=self.company.pk)

        return self.companies.all().exclude(pk=self.company.pk)

    def company_remove(self, company, user):
        if not isinstance(company, Company):
            raise Exception(_("company must be a Company instance."))

        if company.user == self.user:
            return False

        # Remove from company list
        self.colaborator_set.get(company=company).delete()

        # Remove if in this company
        if self.company == company:
            try:
                self.company = self.companies.all().first()
            except Exception:
                self.company = None
        self.save()

        # Change created objects
        self.user.invite.delete()

    def company_switch(self, company):
        if not isinstance(company, Company):
            raise Exception(_("company must be a Company instance."))

        if (
            not self.user.is_staff and
            company not in self.companies.all()
        ):
            raise Exception(_("Invalid company."))

        self.company = company
        self.save()

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

    @cached_property
    def perms(self):
        if (
            not self.company or
            not self.company.is_active
        ):
            return False

        try:
            perms = self.colaborator_set \
                .get(company=self.company, is_active=True) \
                .permissions.all() \
                .select_related('content_type') \
                .values('content_type__app_label', 'codename')

            return [
                '{}:{}'.format(
                    c['content_type__app_label'], c['codename']
                ) for c in perms
            ]
        except Exception:
            return []


class Colaborator(models.Model):
    profile = models.ForeignKey(
        Profile, editable=False, verbose_name=_("Profile")
    )
    company = models.ForeignKey(
        Company, editable=False, related_name='users_all',
        verbose_name=_("Company")
    )
    date_joined = models.DateTimeField(
        auto_now=True, verbose_name=_("Join date")
    )
    is_active = models.BooleanField(
        default=True, verbose_name=_("Active")
    )
    permissions = models.ManyToManyField(
        Permission, blank=True, verbose_name=_("Permissions")
    )

    class Meta:
        ordering = ['profile', ]
        unique_together = ('profile', 'company')
        verbose_name = _("Colaborator")
        verbose_name_plural = _("Colaborators")

    def __str__(self):
        return "%s" % self.profile

    @property
    def user(self):
        return self.profile.user


def has_company_perm(self, perm, obj=None):
    if self.is_superuser:
        return True
    elif self == self.profile.company:
        return True
    elif self.is_staff:
        return self.has_perm(perm, obj)

    return perm in self.profile.perms


def has_company_perms(self, perm_list, obj=None):
    if self.is_superuser:
        return True
    elif self == self.profile.company:
        return True
    elif self.is_staff:
        return self.has_pemrs(perm_list, obj)

    return all(self.has_company_perm(perm, obj) for perm in perm_list)


def user_str(self):
    if self.first_name and self.last_name:
        return '%s %s' % (self.first_name, self.last_name)
    else:
        return self.username


User.add_to_class('__str__', user_str)
User.add_to_class('has_company_perm', has_company_perm)
User.add_to_class('has_company_perms', has_company_perms)


def post_save_user(sender, instance, created, **kwargs):
    if created:
        Profile.objects.get_or_create(user=instance)
        Token.objects.get_or_create(user=instance)

        if not instance.is_active:
            instance.profile.key_generate()


signals.post_save.connect(post_save_user, sender=User)
signals.post_migrate.connect(add_view_permissions)

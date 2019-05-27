from django.conf import settings
from django.contrib.auth.models import Permission
from django.core.exceptions import ImproperlyConfigured
from django.db import models
from django.db.models import signals
from django.http.request import split_domain_port
from django.urls import reverse_lazy
from django.utils.functional import cached_property
from django.utils.translation import ugettext_lazy as _

from boilerplate.mail import SendEmail
from django_countries.fields import CountryField

from core.constants import (
    LEVEL_ERROR, LEVEL_SUCCESS, MODULE_LIST, MODULE_PRICE_LIST
)
from core.context_processors import settings as secure_settings
from core.models.mixins import AuditableMixin, get_active_mixin
from core.validators import validate_domain, validate_comma_separated_str_list


COMPANY_CACHE = {}


class CompanyManager(models.Manager):
    use_in_migrations = True

    def _get_company_by_id(self, company_id):
        if company_id not in COMPANY_CACHE:
            company = self.get(pk=company_id)
            COMPANY_CACHE[company_id] = company
        return COMPANY_CACHE[company_id]

    def _get_company_by_request(self, request):
        host = request.get_host()
        try:
            if host not in COMPANY_CACHE:
                COMPANY_CACHE[host] = self.get(domain__iexact=host)
            return COMPANY_CACHE[host]
        except self.model.DoesNotExist:
            domain, port = split_domain_port(host)
            if domain not in COMPANY_CACHE:
                COMPANY_CACHE[domain] = self.get(domain__iexact=domain)
            return COMPANY_CACHE[domain]

    def get_current(self, request=None):
        from django.conf import settings
        if getattr(settings, 'COMPANY_ID', ''):
            company_id = settings.COMPANY_ID
            return self._get_company_by_id(company_id)
        elif request:
            return self._get_company_by_request(request)

        raise ImproperlyConfigured(
            "You're using \"companies\" without having "
            "set the COMPANY_ID setting. Create a site in your database and "
            "set the COMPANY_ID setting or pass a request to "
            "Company.objects.get_current() to fix this error."
        )

    def clear_cache(self):
        """Clear the ``Company`` object cache."""
        global COMPANY_CACHE
        COMPANY_CACHE = {}

    def get_by_natural_key(self, domain):
        return self.get(domain=domain)


class Company(get_active_mixin(editable=True), AuditableMixin):
    name = models.CharField(
        max_length=50, unique=True, verbose_name=_("name")
    )
    user = models.ForeignKey(
        'core.User', db_index=True, on_delete=models.CASCADE,
        verbose_name=_("user")
    )
    email = models.EmailField(
        verbose_name=_("email")
    )
    language = models.CharField(
        max_length=10, choices=settings.LANGUAGES,
        default=settings.LANGUAGE_CODE, verbose_name=_("language")
    )
    phone = models.CharField(
        blank=True, null=True, max_length=20, verbose_name=_("phone")
    )
    mobile = models.CharField(
        blank=True, null=True, max_length=20, verbose_name=_("mobile")
    )
    address = models.TextField(
        blank=True, null=True, verbose_name=_("address")
    )
    address_2 = models.TextField(
        blank=True, null=True, verbose_name=_("address 2")
    )
    city = models.CharField(
        max_length=100, blank=True, null=True, verbose_name=_("city")
    )
    state = models.CharField(
        max_length=100, blank=True, null=True, verbose_name=_("state")
    )
    country = CountryField(
        blank=True, null=True, verbose_name=_("country")
    )
    zip_code = models.CharField(
        max_length=10, blank=True, verbose_name=_("zip code")
    )
    logo = models.ImageField(
        upload_to='core/companies/', blank=True, null=True,
        verbose_name=_("logo")
    )
    modules = models.CharField(
        max_length=150, blank=True, null=True,
        validators=[validate_comma_separated_str_list],
        verbose_name=_("modules")
    )
    domain = models.CharField(
        max_length=255, validators=[validate_domain],
        unique=True, verbose_name=_("custom domain")
    )
    users = models.ManyToManyField(
        'core.User', blank=True,
        through='Colaborator', related_name='+',
        verbose_name=_("users")
    )
    # API Fields
    mailgun_email = models.EmailField(
        blank=True, null=True, verbose_name=_("mailgun email"),
        help_text=_("on mailgun: default smtp login.")
    )
    mailgun_password = models.CharField(
        max_length=100, blank=True, null=True,
        verbose_name=_('mailgun password'),
        help_text=_("on mailgun: default password.")
    )
    objects = CompanyManager()

    class Meta:
        ordering = ['name', ]
        verbose_name = _("company")
        verbose_name_plural = _("companies")

    def __str__(self):
        return self.name

    @property
    def action_list(self):
        return ('change', )

    @property
    def full_address(self):
        address = ''
        if self.address:
            address += '%s' % self.address
        if self.address_2:
            address += ' %s' % self.address_2
        if self.city:
            address += '\n%s' % self.city
        if self.state:
            address += ', %s' % self.state
        if self.zip_code:
            address += ' %s' % self.zip_code
        return address

    def get_absolute_url(self):
        return reverse_lazy('panel:company_detail')

    def get_module_display(self, module):
        return dict(self.MODULE_LIST).get(module)

    def get_module_price(self, module):
        return dict(MODULE_PRICE_LIST).get(module)

    def has_module(self, module):
        assert isinstance(module, str)
        return module in self.module_list

    @property
    def mailgun_available(self):
        return all([self.mailgun_email, self.mailgun_password])

    def module_add(self, module, force=False, **kwargs):
        assert module in dict(MODULE_LIST), _(
            'Invalid module "%s"' % module
        )

        module_name = self.get_module_display(module)

        if self.has_module(module):
            return LEVEL_ERROR, _(
                'Module "%s" already added.' % module_name
            )

        module_list = self.module_list
        module_list.append(module)
        self.modules = ','.join(module_list)
        self.save(update_fields=['modules'])

        return LEVEL_SUCCESS, _(
            'Module "%s" added successfully.'
        ) % module_name

    @property
    def module_excluded(self):
        module_list = dict(MODULE_LIST)
        modules_excluded = module_list.copy()
        for module in module_list:
            if module in self.module_list:
                modules_excluded.pop(module)
        return modules_excluded.keys()

    @property
    def module_list(self):
        return self.modules.split(',') if self.modules else []

    def module_remove(self, module, **kwargs):
        assert module in dict(MODULE_LIST), _(
            'Invalid module "%s"' % module
        )
        module_name = self.get_module_display(module)

        if not self.has_module(module):
            return LEVEL_ERROR, _(
                'Module "%s" already not added.' % module_name
            )

        module_list = self.module_list
        index = 0
        for mod in module_list:
            if mod == module:
                module_list.pop(index)
                break
            index += 1

        self.modules = ','.join(module_list)
        self.save(update_fields=['modules'])

        return LEVEL_SUCCESS, _(
            'Module removed successfully.'
        ) % module_name

    def notify_admins(self):
        emails = [email for name, email in settings.MANAGERS]

        if not emails:
            return

        settings_secure = secure_settings()
        email = SendEmail(
            to=emails,
            template_name_suffix='company',
            subject=_("A new company has been created."),
            is_html=True
        )
        email.add_context_data('object', self)
        email.add_context_data('settings', settings_secure['settings'])
        response = email.send()
        return response > 0

    @cached_property
    def permission_queryset(self):
        perms = Permission.objects.all().exclude(
            content_type__app_label__in=(
                'admin', 'authtoken', 'contenttypes', 'sessions'
            )
        ).exclude(
            content_type__app_label='core', content_type__model__in=(
                'colaborator', 'notification'
            )
        ).exclude(
            content_type__app_label='auth', content_type__model__in=(
                'group', 'permission'
            )
        ).exclude(
            content_type__app_label='core', codename__in=(
                'add_attachment', 'change_attachment', 'delete_attachment',
                'add_company', 'delete_company',
                'add_message', 'change_message', 'delete_message',
                'add_visit', 'change_visit', 'delete_visit'
            )
        )

        if self.module_excluded:
            perms = perms.exclude(
                content_type__app_label__in=self.module_excluded
            )

        return perms.order_by(
            'content_type__app_label', 'content_type', 'codename'
        ).select_related('content_type')

    @property
    def short_name(self):
        return '{}+'.format(self.name[:2].upper())


def post_save_company(sender, instance, created, **kwargs):
    if created:
        user = instance.user

        user.company = instance
        user.save(update_fields=['company'])
        user.colaborator_set.get_or_create(company=instance)

        instance.notify_admins()


def clear_company_cache(sender, **kwargs):
    instance = kwargs['instance']
    using = kwargs['using']
    try:
        del COMPANY_CACHE[instance.pk]
    except KeyError:
        pass
    try:
        del COMPANY_CACHE[
            Company.objects.using(using).get(pk=instance.pk).domain
        ]
    except (KeyError, Company.DoesNotExist):
        pass


signals.pre_delete.connect(clear_company_cache, sender=Company)
signals.pre_save.connect(clear_company_cache, sender=Company)
signals.post_save.connect(post_save_company, sender=Company)

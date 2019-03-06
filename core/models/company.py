from django.conf import settings
from django.contrib.auth.models import Permission
from django.db import models
from django.db.models import signals
from django.urls import reverse_lazy
from django.utils import timezone
from django.utils.functional import cached_property
from django.utils.text import slugify
from django.utils.translation import activate, ugettext_lazy as _

from dateutil.relativedelta import relativedelta
from django_countries.fields import CountryField

from core.constants import (
    MODULE_LIST, MODULE_PRICE_LIST, RECURRING_CICLE, RECURRING_FEE
)
from core.context_processors import settings as secure_settings
from core.mixins import AuditableMixin
from core.validators import validate_comma_separated_str_list


class Company(AuditableMixin):
    name = models.CharField(
        max_length=50, unique=True, verbose_name=_("name")
    )
    slug = models.SlugField(
        editable=False, unique=True, verbose_name=_("slug")
    )
    user = models.ForeignKey(
        'core.User', related_name='company_created_set',
        db_index=True, on_delete=models.CASCADE, verbose_name=_("user")
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
    custom_domain = models.URLField(
        blank=True, null=True, verbose_name=_("custom domain")
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

    class Meta:
        ordering = ['name', ]
        verbose_name = _("company")
        verbose_name_plural = _("companies")

    def __str__(self):
        return "%s" % self.name

    @property
    def action_list(self):
        return ('change', )

    @classmethod
    def check_all(cls):
        for company in cls.objects.filter(is_active=True):
            company.generate_next_invoice()
            invoice = company.last_invoice

            if (
                invoice and
                not invoice.is_payed and
                timezone.now() > invoice.date_expiration
            ):
                company.deactivate()

    @property
    def domain(self):
        return self.custom_domain or settings.SITE_URL

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
        return reverse_lazy('public:company_detail')

    def get_module_display(self, module):
        return dict(self.MODULE_LIST).get(module)

    def get_module_price(self, module):
        return dict(MODULE_PRICE_LIST).get(module)

    def has_module(self, module):
        assert isinstance(module, str)
        return module in self.module_list

    @cached_property
    def last_invoice(self):
        return self.core_invoice_set.all().first()

    @property
    def mailgun_available(self):
        if self.mailgun_email and self.mailgun_password:
            return True
        return False

    def module_add(self, module, force=False, **kwargs):
        assert module in dict(MODULE_LIST), _(
            'Invalid module "%s"' % module
        )
        assert not self.has_module(module), _(
            'Module "%s" already added.' % module
        )
        if not force:
            assert self.card_set.all().exists(), _(
                "At least one credit card is required."
            )
        module_name = self.get_module_display(module)
        module_price = self.module_price(module)
        module_list = self.module_list

        if not force:
            card = self.card_set.all().first()

            try:
                charge = card.charge(
                    amount=module_price,
                    description=module_name,
                    email=self.email
                )
            except stripe.error.InvalidRequestError as e:
                body = e.json_body
                err = body.get('error', {'message', _("Unknown error.")})
                return LEVEL_ERROR, err['message']
            except stripe.error.CardError as e:
                body = e.json_body
                err = body.get('error', {'message', _("Unknown error.")})
                return LEVEL_ERROR, err['message']

            invoice = self.company_invoice_set.create(
                description=module_name,
                total=module_price,
            )
            invoice.payment_set.create(
                api=card.api,
                api_id=charge['id'],
                total=float(charge['amount'])/100,
            )

        module_list.append(module)
        self.recurring_fee = (
            float(self.recurring_fee or 0) + float(module_price or 0)
        )
        self.modules = ','.join(module_list)
        self.save(update_fields=['modules', 'recurring_fee'])

        return LEVEL_SUCCESS, _("Module added successfully.")

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
        assert self.has_module(module), _(
            'Module "%s" already not added.' % module
        )

        module_name = self.get_module_display(module)
        module_price = self.module_price(module)
        module_list = self.module_list
        index = 0
        for mod in module_list:
            if mod == module:
                module_list.pop(index)
                break
            index += 1

        self.recurring_fee = (
            float(self.recurring_fee or 0) - float(module_price or 0)
        )
        self.modules = ','.join(module_list)
        self.save(update_fields=['modules', 'recurring_fee'])

        return LEVEL_SUCCESS, _("Module removed successfully.")

    def notify_admins(self):
        emails = [email for name, email in settings.MANAGERS]

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
                'colaborator', 'notification', 'payment'
            )
        ).exclude(
            content_type__app_label='auth', content_type__model__in=(
                'group', 'permission', 'colaborator'
            )
        ).exclude(
            content_type__app_label='core', codename__in=(
                'add_attachment', 'change_attachment', 'delete_attachment',
                'add_company', 'delete_company',
                'add_invoice', 'change_invoice', 'delete_invoice',
                'add_message', 'change_message', 'delete_message',
                'send_message',
                'add_visit', 'change_visit', 'delete_visit',
                'delete_user', 'view_user'
            )
        )

        if self.module_excluded:
            perms = perms.exclude(
                content_type__app_label__in=self.module_excluded
            )

        return perms.order_by(
            'content_type__app_label', 'content_type', 'codename'
        ).select_related('content_type')

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        return super().save(*args, **kwargs)

    @property
    def switch_url(self):
        return reverse_lazy('public:company_switch', args=[self.pk])


def post_save_company(sender, instance, created, **kwargs):
    if created:
        user = instance.user

        user.company = instance
        user.save(update_fields=['company'])
        user.colaborator_set.get_or_create(company=instance)

        instance.notify_admins()


signals.post_save.connect(post_save_company, sender=Company)

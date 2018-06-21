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

from core.constants import RECURRING_CICLE, RECURRING_FEE
from core.mixins import AuditableMixin


class Company(AuditableMixin, models.Model):
    name = models.CharField(
        max_length=50, unique=True, verbose_name=_("Name")
    )
    slug = models.SlugField(
        editable=False, unique=True, verbose_name=_("Slug")
    )
    user = models.ForeignKey(
        'core.User', related_name='company_created_set',
        on_delete=models.CASCADE, verbose_name=_("User")
    )
    date_next_invoice = models.DateTimeField(
        blank=True, null=True, verbose_name=_("Next invoice date")
    )
    email = models.EmailField(
        verbose_name=_("Email")
    )
    language = models.CharField(
        max_length=10, choices=settings.LANGUAGES,
        default=settings.LANGUAGE_CODE, verbose_name=_("Language")
    )
    custom_domain = models.URLField(
        blank=True, null=True, verbose_name=_("Custom domain")
    )

    class Meta:
        ordering = ['name', ]
        verbose_name = _("Company")
        verbose_name_plural = _("Companies")

    def __str__(self):
        return "%s" % self.name

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        return super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse_lazy('public:company_detail')

    @property
    def action_list(self):
        return ('change', )

    @property
    def domain(self):
        return self.custom_domain or settings.SITE_URL

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

    def generate_next_invoice(self):
        today = timezone.now() \
            .replace(hour=0, minute=0, second=0, microsecond=0)

        activate(self.language)

        if not self.date_next_invoice or today >= self.date_next_invoice:
            self.invoice_set.create(
                description=_("%(cicle)sy fee for %(company)s.") % dict(
                    cicle=RECURRING_CICLE.title(),
                    company=self.name,
                ),
                subtotal=RECURRING_FEE
            )
            next_args = {'{}s'.format(RECURRING_CICLE): 1}
            if self.date_next_invoice:
                next_ = self.date_next_invoice + relativedelta(**next_args)
            else:
                next_ = timezone.now() + relativedelta(**next_args)
            self.date_next_invoice = next_
            self.save(update_fields=['date_next_invoice'])

    @cached_property
    def permission_queryset(self):
        return Permission.objects.all().exclude(
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

    @property
    def switch_url(self):
        return reverse_lazy('public:company_switch', args=[self.pk])


def post_save_company(sender, instance, created, **kwargs):
    if created:
        instance.user.company = instance
        instance.user.save(update_fields=['company'])
        instance.user.colaborator_set.get_or_create(company=instance)
        instance.generate_next_invoice()


signals.post_save.connect(post_save_company, sender=Company)

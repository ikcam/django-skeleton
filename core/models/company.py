from django.conf import settings
from django.db import models
from django.db.models import signals
from django.urls import reverse_lazy
from django.utils import timezone
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
        'account.User', related_name='+', on_delete=models.CASCADE,
        verbose_name=_("User")
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
        return reverse_lazy('core:company_detail')

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
            self.invoices.create(
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
            self.save()

    @property
    def switch_url(self):
        return reverse_lazy('core:company_switch', args=[self.pk])


def post_save_company(sender, instance, created, **kwargs):
    if created:
        instance.user.company = instance
        instance.user.colaborator_set.create(company=instance)
        instance.user.save()
        instance.generate_next_invoice()


signals.post_save.connect(post_save_company, sender=Company)

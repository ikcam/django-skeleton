from django.contrib.auth.models import User
from django.db import models
from django.db.models import signals
from django.urls import reverse_lazy
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from dateutil.relativedelta import relativedelta

from core.mixins import AuditableMixin
from . import MONTHLY_FEE


class Company(AuditableMixin, models.Model):
    name = models.CharField(
        max_length=50, unique=True, verbose_name=_("Name")
    )
    user = models.ForeignKey(
        User, related_name='companies', verbose_name=_("User")
    )

    class Meta:
        ordering = ['name', ]
        verbose_name = _("Company")
        verbose_name_plural = _("Companies")

    def __str__(self):
        return "%s" % self.name

    def get_absolute_url(self):
        return reverse_lazy('core:company_detail')

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
    def date_next_invoice(self):
        last_invoice = self.invoices.all().first()
        if last_invoice:
            next_ = last_invoice.date_creation + relativedelta(months=1)
        else:
            next_ = timezone.now()
        return next_.replace(hour=0, minute=0, second=0, microsecond=0)

    def generate_next_invoice(self):
        today = timezone.now() \
            .replace(hour=0, minute=0, second=0, microsecond=0)

        if today >= self.date_next_invoice:
            self.invoices.create(
                description="Monthly fee for %s." % self.name,
                subtotal=MONTHLY_FEE
            )

    @property
    def last_invoice(self):
        return self.invoices.all().first()


def post_save_company(sender, instance, created, **kwargs):
    if created:
        instance.user.profile.company = instance
        instance.user.profile.companies.add(instance)
        instance.user.profile.save()


def pre_delete_company(sender, instance, **kwargs):
    instance.twilio_delete()


signals.post_save.connect(post_save_company, sender=Company)
signals.pre_delete.connect(pre_delete_company, sender=Company)

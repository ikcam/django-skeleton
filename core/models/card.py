from django.db import models
from django.db.models import signals
from django.urls import reverse_lazy
from django.utils.translation import ugettext_lazy as _

from core.constants import (
    LEVEL_ERROR, LEVEL_SUCCESS, PROCESSOR_BRAINTREE, PROCESSOR_CULQI,
    PROCESSOR_STRIPE, PROCESSOR_DEFAULT
)
from core.mixins import AuditableMixin
from core.models import braintree, culqipy, stripe


class CardManager(models.Manager):
    def create_from_processor(self, **kwargs):
        return getattr(
            self, 'create_from_processor_{}'.format(PROCESSOR_DEFAULT)
        )(**kwargs)

    def create_from_processor_braintree(self, **kwargs):
        raise NotImplementedError(self.__class__.__name__)

    def create_from_processor_culqi(self, **kwargs):
        raise NotImplementedError(self.__class__.__name__)

    def create_from_processor_stripe(self, **kwargs):
        assert 'token' in kwargs, _("Token must be a positional argument.")
        assert kwargs['token'], _("A valid token must be provided.")

        if not self.instance.processor_sid:
            self.instance.processor_create()

        cus = stripe.Customer.retrieve(self.instance.processor_sid)
        try:
            card = cus.sources.create(source=kwargs['token'])
        except stripe.error.CardError as e:
            body = e.json_body
            err = body['error']
            return LEVEL_ERROR, _("Error: %s") % err['message']

        if card['object'] == 'card':
            return self.update_or_create(
                company=self.instance,
                api=PROCESSOR_DEFAULT,
                api_id=card['id'],
                defaults={
                    'brand': card['brand'],
                    'last_4': card['last4'],
                    'exp_month': card['exp_month'],
                    'exp_year': card['exp_year'],
                }
            )
        else:
            return LEVEL_ERROR, _("Error: %s") % card['message']


class Card(AuditableMixin):
    API_CHOICES = (
        (PROCESSOR_BRAINTREE, _("Braintree")),
        (PROCESSOR_CULQI, _("Culqi")),
        (PROCESSOR_STRIPE, _("Stripe")),
    )
    company = models.ForeignKey(
        'core.Company', editable=False, on_delete=models.CASCADE,
        db_index=True, verbose_name=_("company")
    )
    brand = models.CharField(
        max_length=20, verbose_name=_("brand")
    )
    last_4 = models.IntegerField(
        verbose_name=_("last 4")
    )
    exp_month = models.IntegerField(
        blank=True, null=True, verbose_name=_("expiration month")
    )
    exp_year = models.IntegerField(
        blank=True, null=True, verbose_name=_("expiration year")
    )
    api = models.SlugField(
        choices=API_CHOICES, editable=False, verbose_name=_("API")
    )
    api_id = models.CharField(
        max_length=100, unique=True, editable=False, verbose_name=_("API ID")
    )
    order = models.PositiveIntegerField(
        default=0, verbose_name=_("order")
    )
    objects = CardManager()

    class Meta:
        ordering = ['-date_creation', ]
        verbose_name = _("card")
        verbose_name_plural = _("cards")

    def __str__(self):
        return '**** **** **** {}'.format(self.last_4)

    @property
    def action_list(self):
        return ('delete', )

    def charge(self, **kwargs):
        return getattr(self, 'charge_{}'.format(self.api))(**kwargs)

    def charge_braintree(self, amount, description, **kwargs):
        charge = braintree.transaction.sale({
            'amount': amount,
            'payment_method_token': self.api_id,
            'customer_id': self.company.processor_sid,
        })
        if charge.is_success:
            return (
                PROCESSOR_BRAINTREE,
                charge.transaction.id,
                charge.transaction.amount
            )
        else:
            return ' '.join(
                [error.message for error in charge.errors.deep_errors]
            )

    def charge_culqi(self, amount, description, email, **kwargs):
        amount = int(amount * 100)

        dir_charge = {
          'amount': amount,
          'currency_code': 'USD',
          'email': email,
          'description': description,
          'source_id': self.api_id,
        }
        try:
            charge = culqipy.Charge.create(**dir_charge)

            if charge['object'] == 'error':
                return charge['merchant_message']

            return PROCESSOR_CULQI, charge['id'], float(charge['amount']/100)
        except Exception as e:
            return str(e)

    def charge_stripe(self, amount, description, **kwargs):
        amount = int(amount * 100)

        dir_charge = {
            'amount': amount,
            'currency': 'usd',
            'description': description,
            'customer': self.company.processor_sid,
            'source': self.api_id,
        }
        try:
            charge = stripe.Charge.create(**dir_charge)
            return PROCESSOR_STRIPE, charge['id'], float(charge['amount']/100)
        except stripe.error.CardError as e:
            body = e.json_body
            err = body['error']
            return str(err['message'])

    def get_absolute_url(self):
        return reverse_lazy('public:card_list')

    def processor_delete(self):
        assert self.company.processor_sid, _(
            "Company must have a processor SID."
        )
        assert self.api_id, _("Must have a processor SID.")

        try:
            cus = stripe.Customer.retrieve(self.company.processor_sid)
            card = cus.sources.retrieve(self.api_id)
            card.delete()
            return LEVEL_SUCCESS, _("Removed from processor successfully.")
        except Exception as e:
            return LEVEL_ERROR, _("Error: %s") % e


def pre_delete_card(instance, sender, **kwargs):
    if instance.api_id:
        instance.processor_delete()


signals.pre_delete.connect(pre_delete_card, sender=Card)

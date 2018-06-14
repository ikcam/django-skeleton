from django.db. models import signals
from django.db.models.manager import Manager
from django.urls import reverse_lazy
from django.utils.translation import ugettext_lazy as _

from core.constants import PERSON_CUSTOMER, PERSON_LEAD
from .person import Person


class CustomerManager(Manager):
    def get_queryset(self):
        qs = super().get_queryset()

        return qs.filter(
            type=PERSON_CUSTOMER
        )


class Customer(Person):
    class Meta:
        proxy = True
        verbose_name = _("Customer")
        verbose_name_plural = _("Customers")

    def get_absolute_url(self):
        return reverse_lazy('crm:customer_detail', args=[self.pk])

    @property
    def actions(self):
        return [
            (
                _("To customer"), 'customer', 'info', 'user',
                'crm:delete_customer'
            ),
            (
                _("Change"), 'change', 'success', 'pencil',
                'crm:change_customer'
            ),
            (
                _("Delete"), 'delete', 'danger', 'trash',
                'crm:delete_customer'
            ),
        ]

    def to_lead(self):
        self.type = PERSON_LEAD
        self.save(update_fields=['type'])
        return True

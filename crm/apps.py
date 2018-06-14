from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class CrmConfig(AppConfig):
    name = 'crm'
    verbose_name = _("CRM")

from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class PublicConfig(AppConfig):
    name = 'public'
    verbose_name = _("Public")

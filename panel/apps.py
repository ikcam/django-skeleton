from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class PanelConfig(AppConfig):
    name = 'panel'
    verbose_name = _("panel")

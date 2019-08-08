from django.apps import AppConfig
from django.db.models.signals import post_migrate
from django.utils.translation import ugettext_lazy as _


from core.management import create_default_company


class CoreConfig(AppConfig):
    name = 'core'
    verbose_name = _('Core')

    def ready(self):
        post_migrate.connect(create_default_company, sender=self)

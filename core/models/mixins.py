from django.db import models
from django.utils.translation import ugettext_lazy as _

from core.constants import LEVEL_ERROR, LEVEL_SUCCESS


def get_active_mixin(editable=False, default=True):
    class Model(models.Model):
        is_active = models.BooleanField(
            editable=editable, default=default, verbose_name=_("active")
        )

        class Meta:
            abstract = True

        def activate(self):
            if self.is_active:
                return LEVEL_ERROR, _("%s is active already.") % self

            self.is_active = True
            self.save(update_fields=['is_active'])
            return LEVEL_SUCCESS, _("%s has been activated successfully.") % (
                self
            )

        def deactivate(self):
            if not self.is_active:
                return LEVEL_ERROR, _("%s is inactive already.") % self

            self.is_active = False
            self.save(update_fields=['is_active'])
            return LEVEL_SUCCESS, _(
                "%s has been deactivated successfully."
            ) % self

        def toggle_active(self, **kwargs):
            return self.deactivate() if self.is_active else self.activate()

    return Model


class AuditableMixin(models.Model):
    date_creation = models.DateTimeField(
        auto_now_add=True, verbose_name=_("creation date")
    )
    date_modification = models.DateTimeField(
        auto_now=True, verbose_name=_("modification date")
    )

    class Meta:
        abstract = True

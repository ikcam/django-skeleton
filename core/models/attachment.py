from mimetypes import MimeTypes

from django.contrib.contenttypes.fields import GenericForeignKey
from django.db import models
from django.utils.translation import ugettext_lazy as _

from core.mixins import AuditableMixin


class Attachment(AuditableMixin):
    # Related model
    contenttype = models.ForeignKey(
        'contenttypes.ContentType', blank=True, null=True, editable=False,
        on_delete=models.SET_NULL, verbose_name=_("Content type")
    )
    object_id = models.PositiveIntegerField(
        blank=True, null=True, editable=False, verbose_name=_("Object ID")
    )
    model = GenericForeignKey('contenttype', 'object_id')
    # Model fields
    user = models.ForeignKey(
        'core.User', blank=True, null=True, editable=False,
        on_delete=models.SET_NULL, verbose_name=_("User")
    )
    file = models.FileField(
        upload_to='core/attachments/', verbose_name=_("File")
    )
    detail = models.TextField(
        blank=True, null=True, verbose_name=_("Detail")
    )

    class Meta:
        ordering = ['-date_creation', ]
        verbose_name = _("Attachment")
        verbose_name_plural = _("Attachments")

    def __str__(self):
        return "%s" % self.file.name

    def get_absolute_url(self):
        return self.parent.get_absolute_url()

    @property
    def actions(self):
        return (
            (
                _("Change"), 'change', 'success', 'pencil',
                'core:change_attachment'
            ),
            (
                _("Delete"), 'delete', 'danger', 'trash',
                'core:delete_attachment'
            ),
        )

    @property
    def mime_type(self):
        mime_type, empty = MimeTypes().guess_type(self.file.path)
        return mime_type

    @property
    def name(self):
        return self.file.name.split('/')[-1]

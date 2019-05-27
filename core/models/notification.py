import uuid

from django.contrib.contenttypes.fields import GenericForeignKey
from django.db import models
from django.urls import reverse_lazy
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from core.constants import LEVEL_ERROR, LEVEL_SUCCESS
from core.models.mixins import AuditableMixin


class NotificationManager(models.Manager):
    def set_all_read(self, company, user, *args, **kwargs):
        return self.filter(
            company=company,
            user=user,
            date_read__isnull=True
        ).update(date_read=timezone.now())


class Notification(AuditableMixin):
    id = models.UUIDField(
        default=uuid.uuid4, primary_key=True, editable=False,
        verbose_name=_("id")
    )
    company = models.ForeignKey(
        'core.Company', editable=False, on_delete=models.CASCADE,
        db_index=True, verbose_name=_("company")
    )
    user = models.ForeignKey(
        'core.User', editable=False, on_delete=models.CASCADE,
        db_index=True, verbose_name=_("user")
    )
    # Related model
    content_type = models.ForeignKey(
        'contenttypes.ContentType', editable=False,
        on_delete=models.CASCADE, db_index=True,
        verbose_name=_("content type")
    )
    object_id = models.CharField(
        blank=True, null=True, max_length=150, editable=False,
        verbose_name=_("object id")
    )
    model = GenericForeignKey('content_type', 'object_id')
    # Hidden fields
    date_read = models.DateTimeField(
        blank=True, null=True, editable=False, verbose_name=_("read date")
    )
    level = models.SlugField(
        blank=True, null=True, editable=False, verbose_name=_("level")
    )
    content = models.CharField(
        editable=False, max_length=250, verbose_name=_("content")
    )
    destination = models.URLField(
        editable=False, verbose_name=_("destination")
    )

    objects = NotificationManager()

    class Meta:
        ordering = ["-date_creation", ]
        verbose_name = _("notification")
        verbose_name_plural = _("notifications")

    def __str__(self):
        return "%s %s" % (self.model or self.contenttype, self.content)

    def get_absolute_url(self):
        return reverse_lazy('panel:notification_detail', args=[self.pk])

    def is_read(self):
        return True if self.date_read else False
    is_read.boolean = True

    @property
    def parent(self):
        return self.model if self.model else None

    def set_read(self):
        if self.is_read():
            return LEVEL_ERROR, _("Notification is read already.")
        self.date_read = timezone.now()
        self.save(update_fields=['date_read'])
        return LEVEL_SUCCESS, _("Notification has been marked as read.")

    def set_unread(self):
        if not self.is_read():
            return LEVEL_ERROR, _("Notification is unread already.")
        self.date_read = None
        self.save(update_fields=['date_read'])
        return LEVEL_SUCCESS, _("Notification has been marked as unread.")

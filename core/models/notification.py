from django.contrib.contenttypes.fields import GenericForeignKey
from django.db import models
from django.urls import reverse_lazy
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from core.constants import LEVEL_INFO, LEVEL_SUCCESS
from core.mixins import AuditableMixin


class Notification(AuditableMixin):
    company = models.ForeignKey(
        'core.Company', editable=False, on_delete=models.CASCADE,
        verbose_name=_("Company")
    )
    user = models.ForeignKey(
        'core.User', editable=False, on_delete=models.CASCADE,
        verbose_name=_("User")
    )
    # Related model
    contenttype = models.ForeignKey(
        'contenttypes.ContentType', editable=False,
        on_delete=models.CASCADE, verbose_name=_("Content type")
    )
    object_id = models.PositiveIntegerField(
        blank=True, null=True, editable=False, verbose_name=_("Object ID")
    )
    model = GenericForeignKey('contenttype', 'object_id')
    # Hidden fields
    date_read = models.DateTimeField(
        blank=True, null=True, editable=False, verbose_name=_("Read date")
    )
    level = models.SlugField(
        blank=True, null=True, editable=False, verbose_name=_("Level")
    )
    content = models.CharField(
        editable=False, max_length=250, verbose_name=_("Content")
    )
    destination = models.URLField(
        editable=False, verbose_name=_("Destination")
    )

    class Meta:
        ordering = ["-date_creation", ]
        verbose_name = _("Notification")
        verbose_name_plural = _("Notifications")

    def __str__(self):
        return "%s %s" % (self.model or self.contenttype, self.content)

    def get_absolute_url(self):
        return reverse_lazy('public:notification_detail', args=[self.pk])

    @property
    def is_read(self):
        return True if self.date_read else False

    @property
    def parent(self):
        if self.model:
            return self.model

    @classmethod
    def set_read_all(cls, user):
        user.notification_set.filter(
            company=user.company,
            date_read__isnull=True
        ).update(date_read=timezone.now())
        return (LEVEL_SUCCESS, _("All notifications were mark as read."))

    def set_read(self):
        if self.is_read:
            return (LEVEL_INFO, _("Notification was read already."))
        self.date_read = timezone.now()
        self.save(update_fields=['date_read'])
        return (LEVEL_SUCCESS, _("Notification has been marked as read."))

    def set_unread(self):
        if not self.is_read:
            return (LEVEL_INFO, _("Notification is unread already."))
        self.date_read = None
        self.save(update_fields=['date_read'])
        return (LEVEL_SUCCESS, _("Notification has been marked as unread."))

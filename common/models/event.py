from datetime import timedelta

from django.contrib.auth.models import ContentType, User
from django.contrib.contenttypes.fields import GenericForeignKey
from django.core.validators import validate_comma_separated_integer_list
from django.db import models
from django.template.loader import get_template
from django.urls import reverse_lazy
from django.utils import timezone
from django.utils.translation import activate, ugettext_lazy as _

from core.constants import (
    DIRECTION_OUTBOUND, EVENT_APPOINTMENT, EVENT_CALL, EVENT_JOB_START,
    EVENT_PRIVATE, EVENT_TASK, NOTIFY_0, NOTIFY_10, NOTIFY_30, NOTIFY_60,
    NOTIFY_1440
)
from core.mixins import AuditableMixin
from core.models import Company


class Event(AuditableMixin):
    NOTIFICATION_OPTIONS = (
        (NOTIFY_0, _("At time")),
        (NOTIFY_10, _("10 minutes before")),
        (NOTIFY_30, _("30 minutes before")),
        (NOTIFY_60, _("60 minutes before")),
        (NOTIFY_1440, _("24 hours before")),
    )
    TYPE_CHOICES = (
        (EVENT_APPOINTMENT, _("Appointment")),
        (EVENT_CALL, _("Call")),
        (EVENT_JOB_START, _("Job start")),
        (EVENT_PRIVATE, _("Private")),
        (EVENT_TASK, _("Task")),
    )

    company = models.ForeignKey(
        Company, editable=False, related_name='events',
        verbose_name=_("Company")
    )
    user = models.ForeignKey(
        User, blank=True, null=True, editable=False, related_name='events',
        verbose_name=_("User")
    )
    contenttype = models.ForeignKey(
        ContentType, blank=True, null=True, editable=False,
        verbose_name=_("Content type")
    )
    object_id = models.PositiveIntegerField(
        editable=False, blank=True, null=True, verbose_name=_("Object ID")
    )
    model = GenericForeignKey('contenttype', 'object_id')
    user = models.ForeignKey(
        User, editable=False, related_name='events',
        verbose_name=_("User")
    )
    share_with = models.ManyToManyField(
        User, blank=True, related_name='shared_events',
        verbose_name=_("Share with")
    )
    date_start = models.DateTimeField(
        blank=True, null=True, verbose_name=_("Start date")
    )
    date_finish = models.DateTimeField(
        blank=True, null=True, verbose_name=_("Finish date")
    )
    notify = models.CharField(
        max_length=50, default=NOTIFY_0,
        validators=[validate_comma_separated_integer_list],
        verbose_name=_("Notify")
    )
    notified = models.CharField(
        max_length=50, blank=True, null=True, editable=False,
        validators=[validate_comma_separated_integer_list],
        verbose_name=_("Notified")
    )
    type = models.SlugField(
        choices=TYPE_CHOICES, verbose_name=_("Type")
    )
    content = models.TextField(
        verbose_name=_("Content")
    )

    class Meta:
        ordering = ['-date_creation']
        verbose_name = _("Event")
        verbose_name_plural = _("Events")

    def __str__(self):
        return "%s" % self.subject

    def get_absolute_url(self):
        if self.model:
            return self.model.get_absolute_url()
        return reverse_lazy('common:event_change', args=[self.pk])

    def can_send(self, turn):
        if self.notification_sended(turn):
            return False
        if self.timeuntil <= int(turn):
            return True
        return False

    @property
    def date(self):
        return self.date_start or self.date_creation

    def get_notify_display(self, turn):
        return dict(self.NOTIFICATION_OPTIONS).get(int(turn))

    def get_notified_display(self, turn):
        return dict(self.NOTIFICATION_OPTIONS).get(int(turn))

    @property
    def notify_list(self):
        return self.notify.split(',')

    @property
    def notified_list(self):
        if self.notified:
            return self.notified.split(',')
        return []

    @property
    def notification_pending_list(self):
        if not self.notify:
            return []
        return list(set(self.notify_list) - set(self.notified_list))

    def notification_sended(self, turn):
        return str(turn) in self.notified_list

    @classmethod
    def send_schedule(cls):
        date_start = timezone.now() - timedelta(minutes=NOTIFY_30)

        qs = cls.objects.filter(
            user__isnull=False,
            date_start__gte=date_start
        )
        send = 0
        failed = 0

        for item in qs:
            for turn in item.notification_pending_list:
                if item.can_send(turn):
                    if item.send(turn):
                        send += 1
                    else:
                        failed += 1

        return dict(
            total=qs.count(),
            send=send,
            failed=failed
        )

    def send(self, turn=None):
        if not self.user:
            raise Exception(_("Event has no user."))

        cc = ''

        if self.share_with.all().count() > 0:
            cc = [user.email for user in self.share_with.all()]

        activate(self.company.language)

        html_template = get_template('common/event_email.html')
        content = html_template.render({
            'object': self,
            'turn': self.get_notify_display(turn),
        })
        subject = _("[%(company)s] Event reminder") % dict(
            company=self.company
        )

        message = self.company.messages.create(
            content=content,
            direction=DIRECTION_OUTBOUND,
            from_name=self.company.name,
            from_email=self.company.email,
            model=self,
            to_email=self.user.email,
            to_email_cc=','.join(cc),
            subject=subject,
            user=self.user,
        )
        message.send()
        return True

    @property
    def subject(self):
        if self.model:
            return "%(type)s - %(contenttype)s %(model)s" % dict(
                type=self.get_type_display(),
                contenttype=self.contenttype,
                model=self.model,
            )

        return "%(type)s" % dict(
            type=self.get_type_display()
        )

    @property
    def timeuntil(self):
        if not self.date_start:
            return None

        now = timezone.now()

        if now > self.date_start:
            return 0
        return int((self.date_start - now).total_seconds() / 60)

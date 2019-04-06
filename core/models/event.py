from datetime import timedelta
import uuid

from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.core.validators import validate_comma_separated_integer_list
from django.db import models
from django.template.loader import get_template
from django.urls import reverse_lazy
from django.utils import timezone
from django.utils.translation import activate, ugettext_lazy as _

from core.constants import (
    DIRECTION_OUTBOUND, EVENT_APPOINTMENT, EVENT_CALL, EVENT_JOB_START,
    EVENT_PRIVATE, EVENT_TASK, EVENT_APPOINTMENT_COLOR, EVENT_CALL_COLOR,
    EVENT_JOB_START_COLOR, EVENT_PRIVATE_COLOR, EVENT_TASK_COLOR, LEVEL_ERROR,
    NOTIFY_0, NOTIFY_10, NOTIFY_30, NOTIFY_60, NOTIFY_1440
)
from core.context_processors import settings as secure_settings
from core.models.mixins import AuditableMixin


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
    TYPE_COLORS = (
        (EVENT_APPOINTMENT, EVENT_APPOINTMENT_COLOR),
        (EVENT_CALL, EVENT_CALL_COLOR),
        (EVENT_JOB_START, EVENT_JOB_START_COLOR),
        (EVENT_PRIVATE, EVENT_PRIVATE_COLOR),
        (EVENT_TASK, EVENT_TASK_COLOR),
    )

    id = models.UUIDField(
        default=uuid.uuid4, primary_key=True, editable=False,
        verbose_name=_("id")
    )
    company = models.ForeignKey(
        'core.Company', editable=False, on_delete=models.CASCADE,
        db_index=True, verbose_name=_("company")
    )
    user = models.ForeignKey(
        'core.User', blank=True, null=True, on_delete=models.PROTECT,
        db_index=True, verbose_name=_("user")
    )
    content_type = models.ForeignKey(
        'contenttypes.ContentType', blank=True, null=True, editable=False,
        db_index=True, on_delete=models.CASCADE, verbose_name=_("content type")
    )
    object_id = models.PositiveIntegerField(
        editable=False, blank=True, null=True, verbose_name=_("object ID")
    )
    model = GenericForeignKey('content_type', 'object_id')
    share_with = models.ManyToManyField(
        'core.User', blank=True, related_name='shared_events',
        verbose_name=_("share with")
    )
    date_start = models.DateTimeField(
        blank=True, null=True, verbose_name=_("start date")
    )
    date_finish = models.DateTimeField(
        blank=True, null=True, verbose_name=_("finish date")
    )
    notify = models.CharField(
        max_length=50, default=NOTIFY_0,
        validators=[validate_comma_separated_integer_list],
        verbose_name=_("notify")
    )
    notified = models.CharField(
        max_length=50, blank=True, null=True, editable=False,
        validators=[validate_comma_separated_integer_list],
        verbose_name=_("notified")
    )
    is_public = models.BooleanField(
        default=False, verbose_name=_("public")
    )
    type = models.SlugField(
        choices=TYPE_CHOICES, verbose_name=_("type")
    )
    content = models.TextField(
        verbose_name=_("content")
    )

    class Meta:
        ordering = ['-date_creation']
        permissions = (
            ('view_all_event', 'Can view all Event'),
        )
        verbose_name = _("event")
        verbose_name_plural = _("events")

    def __str__(self):
        return "%s" % self.subject

    def get_absolute_url(self):
        return reverse_lazy('panel:event_change', args=[self.pk])

    def get_public_url(self):
        if not self.is_public:
            return
        return '{scheme}://{domain}{path}'.format(
            scheme='http' if settings.DEBUG else 'https',
            domain=self.company.domain,
            path=reverse_lazy(
                'public:event_public', args=[self.pk]
            )
        )

    @property
    def action_list(self):
        return ('change', 'delete')

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

    def get_type_color(self):
        return dict(self.TYPE_COLORS)[self.type]

    @property
    def google_calendar_url(self):
        start_string = self.date.strftime('%Y%m%dT%H%M%SZ')
        finish_string = (self.date_finish or self.date).strftime(
            '%Y%m%dT%H%M%SZ'
        )

        url = (
            'https://www.google.com/calendar/render?action=TEMPLATE'
            '&text={subject}&details={content}&'
            'dates={date_start}%2F{date_finish}'
        ).format(
            subject=self.subject,
            content=self.content,
            date_start=start_string,
            date_finish=finish_string
        )

        return url

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
    def check_all(cls):
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

    def send(self, turn=None, **kwargs):
        if not self.user:
            return LEVEL_ERROR, _("Event has no user.")

        cc = ''

        if self.share_with.all().exists():
            cc = [user.email for user in self.share_with.all()]

        activate(self.company.language)

        html_template = get_template('public/event_email.html')
        context = secure_settings()
        context['object'] = self
        context['turn'] = self.get_notify_display(turn)
        content = html_template.render(context)
        subject = _("[%(company)s] Event reminder") % dict(
            company=self.company
        )

        message = self.company.message_set.create(
            content=content,
            direction=DIRECTION_OUTBOUND,
            from_name=self.company.name,
            from_email=self.company.email,
            model=self,
            to_email=self.user.email,
            to_email_cc=','.join(cc),
            subject=subject,
        )
        return message.send()

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

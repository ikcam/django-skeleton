import re
import uuid

from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.core.mail import get_connection, EmailMultiAlternatives
from django.db import models
from django.template.loader import get_template
from django.urls import reverse_lazy
from django.utils import timezone
from django.utils.translation import activate, ugettext_lazy as _

from bs4 import BeautifulSoup

from core.constants import (
    DIRECTION_INBOUND, DIRECTION_OUTBOUND, HREF_REGEX, LEVEL_ERROR,
    LEVEL_SUCCESS, URL_REGEX
)
from core.models.mixins import AuditableMixin


class MessageManager(models.Manager):
    def read_all(self):
        return self.filter(
            direction=DIRECTION_INBOUND,
            date_read__isnull=True
        ).update(date_read=timezone.now())


class Message(AuditableMixin):
    DIRECTION_CHOICES = (
        (DIRECTION_INBOUND, _("Inbound")),
        (DIRECTION_OUTBOUND, _("Outbound")),
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
        'core.User', blank=True, null=True, editable=False,
        on_delete=models.SET_NULL, db_index=True,  verbose_name=_("user")
    )
    # Related model
    content_type = models.ForeignKey(
        'contenttypes.ContentType', blank=True, null=True, editable=False,
        on_delete=models.SET_NULL, db_index=True,
        verbose_name=_("content type")
    )
    object_id = models.PositiveIntegerField(
        blank=True, null=True, editable=False, verbose_name=_("object ID")
    )
    model = GenericForeignKey('content_type', 'object_id')
    # Hidden fields
    date_fail = models.DateTimeField(
        blank=True, null=True, editable=False, verbose_name=_("fail date")
    )
    date_read = models.DateTimeField(
        blank=True, null=True, editable=False, verbose_name=_("read date")
    )
    date_send = models.DateTimeField(
        blank=True, null=True, editable=False, verbose_name=_("send date")
    )
    direction = models.SlugField(
        choices=DIRECTION_CHOICES, default=DIRECTION_OUTBOUND, editable=False,
        verbose_name=_("direction")
    )
    token = models.CharField(
        max_length=150, blank=True, null=True, verbose_name=_("token")
    )
    # Email information
    from_email = models.EmailField(
        blank=True, verbose_name=_("from email")
    )
    from_name = models.CharField(
        max_length=50, blank=True, verbose_name=_("from name")
    )
    to_email = models.TextField(
        blank=True, verbose_name=_("to email")
    )
    to_email_cc = models.TextField(
        blank=True, verbose_name=_("to email cc")
    )
    to_email_bcc = models.TextField(
        blank=True, verbose_name=_("to email bcc")
    )
    reply_to_email = models.TextField(
        blank=True, verbose_name=_("reply to email")
    )
    subject = models.CharField(
        max_length=150, verbose_name=_("subject")
    )
    # Common
    content = models.TextField(
        verbose_name=_("content")
    )
    objects = MessageManager()

    class Meta:
        ordering = ["-date_creation", ]
        permissions = (
            ('send_message', 'Can send message'),
        )
        verbose_name = _("message")
        verbose_name_plural = _("messages")

    def __str__(self):
        if self.direction == DIRECTION_INBOUND:
            return "%s" % self.from_
        if self.direction == DIRECTION_OUTBOUND:
            return "%s" % self.to

    @property
    def content_html(self):
        return self.content if self.is_html() else ''

    @property
    def content_raw(self):
        if not self.is_html():
            return self.content

        content_html = BeautifulSoup(self.content, "html.parser")
        body = content_html.body

        if body:
            content_raw = body.get_text()
        else:
            content_raw = content_html.get_text()

        lines = []

        for line in content_raw.split('\n'):
            if line.strip():
                lines.append(line.strip())

        return '\n'.join(lines)

    @property
    def from_(self):
        return self.from_email

    def get_absolute_url(self):
        return reverse_lazy('panel:message_detail', args=[self.pk])

    def get_email_connection(self, fail_silently=False):
        if hasattr(self, '_email_connection'):
            return self._email_connection

        if self.company.mailgun_available:
            self._email_connection = get_connection(
                fail_silently=fail_silently,
                username=self.company.mailgun_email,
                password=self.company.mailgun_password,
            )
        else:
            self._email_connection = get_connection()
        return self._email_connection

    def is_fail(self):
        return True if self.date_fail else False
    is_fail.boolean = True

    def is_html(self):
        return bool(BeautifulSoup(self.content, "html.parser").find())
    is_html.boolean = True

    def is_read(self):
        return True if self.date_read else False
    is_read.boolean = True

    def is_send(self):
        return True if self.date_send else False
    is_send.boolean = True

    def report_bounce(self, data):
        self.date_fail = timezone.now()
        self.save(update_fields=['date_fail'])

        to_ = list()

        if self.user and self.user.email:
            to_.append(self.user.email)
        if self.company.email:
            to_.append(self.company.email)
        if not to_:
            return False

        activate(self.company.language)

        from_email = "%s <%s>" % (self.from_name, self.from_email)
        template_html = get_template('public/message_bounce.html')
        content_html = template_html.render({
            'object': self,
            'emails': data['emails']
        })
        content_raw = BeautifulSoup(content_html, "html.parser").get_text()

        subject = _(
            '[%(company)s] Message has bounce'
        ) % dict(
            company=self.company,
        )
        email = EmailMultiAlternatives(
            body=content_raw,
            from_email=from_email,
            subject=subject,
            to=self.from_email,
        )
        email.attach_alternative(content_html, 'text/html')
        return email.send() > 0

    def send(self):
        return self._send_email()

    def _send_email(self):
        if self.is_send():
            return LEVEL_ERROR, _("Message was sent already.")

        activate(self.company.language)
        content_raw, content_html = self.set_links()

        if content_html:
            content_html = self.set_pixel(content_html)

        from_email = "%s <%s>" % (self.from_name, self.from_email)
        headers = {
            'MyApp-ID': '{}'.format(self.pk)
        }

        email = EmailMultiAlternatives(
            bcc=self.to_email_bcc.split(',') if self.to_email_bcc else None,
            body=content_raw,
            cc=self.to_email_cc.split(',') if self.to_email_cc else None,
            connection=self.get_email_connection(),
            from_email=from_email,
            headers=headers,
            reply_to=(
                self.reply_to_email.split(',') if self.reply_to_email else None
            ),
            subject=self.subject,
            to=self.to_email.split(','),
        )

        if content_html:
            email.attach_alternative(content_html, 'text/html')

        if email.send() > 0:
            self.date_send = timezone.now()
            self.save(update_fields=['date_send'])
            return LEVEL_SUCCESS, _("Message sent successfully.")
        else:
            return LEVEL_ERROR, _("An error has ocurred.")

    def set_links(self):
        if self.is_html():
            content_html = self.content
            regex = re.compile(HREF_REGEX, re.IGNORECASE)
            founded = re.finditer(regex, content_html or '')

            for element in founded:
                href = str(element.group(0))
                destination = href.replace('href="', '')[:-1]

                link, created = self.link_set.get_or_create(
                    company=self.company,
                    destination=destination,
                )
                replace = href.replace(destination, link.get_public_url())
                content_html = content_html.replace(href, replace)
        else:
            content_html = None

        content_raw = self.content_raw
        regex = re.compile(URL_REGEX, re.IGNORECASE)
        founded = re.finditer(regex, content_raw or '')

        for element in founded:
            destination = str(element.group(0))

            link, created = self.link_set.get_or_create(
                company=self.company,
                destination=destination,
            )
            replace = href.replace(destination, link.get_public_url())
            content_raw = content_raw.replace(href, replace)

        return content_raw, content_html

    def set_pixel(self, content):
        bs_content = BeautifulSoup(content, "html.parser")
        pixel = bs_content.new_tag(
            'img',
            alt='x',
            height='1px',
            src='{scheme}://{domain}{path}'.format(
                scheme='http' if settings.DEBUG else 'https',
                domain=self.company.domain,
                path=reverse_lazy(
                    'public:message_pixel', args=[self.pk]
                )
            ),
            width='1px',
        )

        if bs_content.body:
            bs_content.body.insert(3, pixel)
        else:
            bs_content.append(pixel)

        return bs_content.prettify()

    def set_read(self):
        if self.is_read():
            return LEVEL_ERROR, _("Message was read already.")
        self.date_read = timezone.now()
        self.save(update_fields=['date_read'])
        return LEVEL_SUCCESS, _("Message has been marked as read.")

    def set_unread(self):
        if not self.is_read():
            return LEVEL_ERROR, _("Message is unread already.")
        self.date_read = None
        self.save(update_fields=['date_read'])
        return LEVEL_SUCCESS, _("Message has been marked as unread.")

    @property
    def status(self):
        if self.is_fail():
            return _("failed")
        elif self.is_read():
            return _("read")
        elif self.is_send():
            return _("send")
        else:
            return _("unsend")

    @property
    def to(self):
        return self.to_email

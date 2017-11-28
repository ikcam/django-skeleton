import hashlib
import random
import re

from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.core.mail import EmailMultiAlternatives
from django.db import models
from django.template.loader import get_template
from django.urls import reverse_lazy
from django.utils import timezone
from django.utils.translation import activate, ugettext_lazy as _

from bs4 import BeautifulSoup

from core.constants import (
    DIRECTION_INBOUND, DIRECTION_OUTBOUND, HREF_REGEX, URL_REGEX
)
from core.mixins import AuditableMixin
from core.models import Company
from common import tasks


class Message(AuditableMixin):
    DIRECTION_CHOICES = (
        (DIRECTION_INBOUND, _("Inbound")),
        (DIRECTION_OUTBOUND, _("Outbound")),
    )

    company = models.ForeignKey(
        Company, editable=False, related_name='messages',
        verbose_name=_("Company")
    )
    user = models.ForeignKey(
        User, blank=True, null=True, editable=False, related_name='messages',
        verbose_name=_("User")
    )
    # Related model
    contenttype = models.ForeignKey(
        ContentType, blank=True, null=True, editable=False,
        verbose_name=_("Content type")
    )
    object_id = models.PositiveIntegerField(
        blank=True, null=True, editable=False, verbose_name=_("Object ID")
    )
    model = GenericForeignKey('contenttype', 'object_id')
    # Hidden fields
    date_fail = models.DateTimeField(
        blank=True, null=True, editable=False, verbose_name=_("Fail date")
    )
    date_read = models.DateTimeField(
        blank=True, null=True, editable=False, verbose_name=_("Read date")
    )
    date_send = models.DateTimeField(
        blank=True, null=True, editable=False, verbose_name=_("Send date")
    )
    direction = models.SlugField(
        choices=DIRECTION_CHOICES, default=DIRECTION_OUTBOUND, editable=False,
        verbose_name=_("Direction")
    )
    token = models.CharField(
        max_length=150, blank=True, null=True, verbose_name=_("Token")
    )
    # Email information
    from_email = models.EmailField(
        blank=True, verbose_name=_("From email")
    )
    from_name = models.CharField(
        max_length=50, blank=True, verbose_name=_("From name")
    )
    to_email = models.TextField(
        blank=True, verbose_name=_("To email")
    )
    to_email_cc = models.TextField(
        blank=True, verbose_name=_("To email CC")
    )
    to_email_bcc = models.TextField(
        blank=True, verbose_name=_("To email BCC")
    )
    reply_to_email = models.TextField(
        blank=True, verbose_name=_("Reply to email")
    )
    subject = models.CharField(
        max_length=150, verbose_name=_("Subject")
    )
    # Common
    content = models.TextField(
        verbose_name=_("Content")
    )

    class Meta:
        ordering = ["-date_creation", ]
        permissions = (
            ('send_message', 'Can send message'),
        )
        verbose_name = _("Message")
        verbose_name_plural = _("Messages")

    def __str__(self):
        if self.direction == DIRECTION_INBOUND:
            return "%s" % self.from_
        if self.direction == DIRECTION_OUTBOUND:
            return "%s" % self.to

    def get_absolute_url(self):
        return reverse_lazy('common:message_detail', args=[self.pk, ])

    @property
    def content_html(self):
        if self.is_html:
            return self.content

    @property
    def content_raw(self):
        if not self.is_html:
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

    @property
    def is_fail(self):
        return True if self.date_fail else False

    @property
    def is_html(self):
        return bool(BeautifulSoup(self.content, "html.parser").find())

    @property
    def is_read(self):
        return True if self.date_read else False

    @property
    def is_send(self):
        return True if self.date_send else False

    def report_bounce(self, data):
        self.date_fail = timezone.now()
        self.save()

        to_ = list()

        if self.user and self.user.email:
            to_.append(self.user.email)
        if self.company.email:
            to_.append(self.company.email)
        if not to_:
            return False

        activate(self.company.language)

        from_email = "%s <%s>" % (self.from_name, self.from_email)
        template_html = get_template('common/mail/message_bounce.html')
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
        if self.date_send:
            return ('error', _("Email was sent already."))

        activate(self.company.language)
        content_raw, content_html = self.set_links()

        if content_html:
            content_html = self.set_pixel(content_html)

        from_email = "%s <%s>" % (self.from_name, self.from_email)
        headers = {
            'MyApp-ID': '{}-{}'.format(self.company.pk, self.pk)
        }

        email = EmailMultiAlternatives(
            bcc=self.to_email_bcc.split(','),
            body=content_raw,
            cc=self.to_email_cc.split(','),
            from_email=from_email,
            headers=headers,
            reply_to=self.reply_to_email.split(','),
            subject=self.subject,
            to=self.to_email.split(','),
        )

        if content_html:
            email.attach_alternative(content_html, 'text/html')

        if email.send() > 0:
            self.date_send = timezone.now()
            self.save()
            return ('success', _("Email sent successfully."))
        else:
            return ('error', _("An error has ocurred."))

    def set_links(self):
        if self.is_html:
            content_html = self.content
            regex = re.compile(HREF_REGEX, re.IGNORECASE)
            founded = re.finditer(regex, content_html or '')

            for element in founded:
                href = str(element.group(0))
                destination = href.replace('href="', '')[:-1]

                link, created = self.links.get_or_create(
                    company=self.company,
                    destination=destination,
                )
                link.token_generate()
                replace = href.replace(destination, link.get_public_url())
                content_html = content_html.replace(href, replace)
        else:
            content_html = None

        content_raw = self.content_raw
        regex = re.compile(URL_REGEX, re.IGNORECASE)
        founded = re.finditer(regex, content_raw or '')

        for element in founded:
            destination = str(element.group(0))

            link, created = self.links.get_or_create(
                company=self.company,
                destination=destination,
            )
            link.token_generate()
            replace = href.replace(destination, link.get_public_url())
            content_raw = content_raw.replace(href, replace)

        return content_raw, content_html

    def set_pixel(self, content):
        bs_content = BeautifulSoup(content, "html.parser")
        pixel = bs_content.new_tag(
            'img',
            alt='x',
            height='1px',
            src='{}{}'.format(
                self.company.domain,
                reverse_lazy(
                    'common:message_pixel', args=[self.set_token()]
                )
            ),
            width='1px',
        )

        if bs_content.body:
            bs_content.body.insert(3, pixel)
        else:
            bs_content.append(pixel)

        return bs_content.prettify()

    @classmethod
    def set_read_all(cls, company):
        return company.messages.filter(
            direction=DIRECTION_INBOUND,
            date_read__isnull=True
        ).update(date_read=timezone.now())

    def set_read(self):
        if self.is_read:
            return ('info', _("Message was read already."))
        self.date_read = timezone.now()
        self.save()
        return ('success', _("Message has been marked as read."))

    def set_token(self):
        if self.token:
            return self.token

        salt = hashlib.sha1(
            str(random.random()).encode("utf-8")
        ).hexdigest()[:5]

        self.token = hashlib.sha1(
            salt.encode("utf-8") + 'message-{}'.format(self.pk).encode("utf-8")
        ).hexdigest()
        self.save()

        return self.token

    def set_unread(self):
        if not self.is_read:
            return ('info', _("Message is unread already."))
        self.date_read = None
        self.save()
        return ('success', _("Message has been marked as unread."))

    @property
    def status(self):
        if self.is_fail:
            return _("Failed")
        elif self.is_read:
            return _("Read")
        elif self.is_send:
            return _("Send")
        else:
            return _("Unsend")

    @property
    def to(self):
        return self.to_email

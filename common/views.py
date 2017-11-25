from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.http import Http404, HttpResponse
from django.urls import reverse_lazy
from django.utils.translation import ugettext_lazy as _
from django.views.generic import DetailView, ListView
from django.views.generic.edit import CreateView, DeleteView, UpdateView

from boilerplate.mixins import (
    ActionListMixin, CreateMessageMixin, DeleteMessageMixin,
    UpdateMessageMixin, UserCreateMixin
)

from core.constants import PIXEL_GIF_DATA
from core.mixins import CompanyCreateMixin, CompanyQuerySetMixin
from .models import Event, Link, Message
from . import forms, tasks


class EventList(ActionListMixin, CompanyQuerySetMixin, ListView):
    action_list = (
        (_("Add"), 'add', 'primary', 'plus', 'common:add_event'),
    )
    model = Event
    paginate_by = 30
    permissions_required = 'common:view_event'

    def get_queryset(self):
        return self.model.objects.none()


class EventDetail(CompanyQuerySetMixin, DetailView):
    model = Event
    permissions_required = 'common:view_event'


class EventCreate(
    UserCreateMixin, CompanyCreateMixin, CreateMessageMixin, CreateView
):
    model = Event
    permissions_required = 'common:add_event'

    def get_form_class(self):
        return forms.get_event_form(self.company)


class EventUpdate(CompanyQuerySetMixin, UpdateMessageMixin, UpdateView):
    model = Event
    permissions_required = 'common:change_event'

    def get_form_class(self):
        return forms.get_event_form(self.company)


class EventDelete(CompanyQuerySetMixin, DeleteMessageMixin, DeleteView):
    model = Event
    permissions_required = 'common:delete_event'
    success_url = reverse_lazy('common:event_list')
    template_name_suffix = '_form'


class LinkList(CompanyQuerySetMixin, ActionListMixin, ListView):
    action_list = (
        (_("Add"), 'add', 'primary', 'plus', 'common:add_link'),
    )
    model = Link
    paginate_by = 30
    permissions_required = 'common:view_link'


class LinkDetail(CompanyQuerySetMixin, DetailView):
    model = Link
    permissions_required = 'common:view_link'


class LinkCreate(
    UserCreateMixin, CompanyCreateMixin, CreateMessageMixin, CreateView
):
    form_class = forms.LinkForm
    model = Link
    permissions_required = 'common:add_link'


class LinkUpdate(CompanyQuerySetMixin, UpdateMessageMixin, UpdateView):
    form_class = forms.LinkForm
    model = Link
    permissions_required = 'common:change_link'


class LinkDelete(CompanyQuerySetMixin, DeleteMessageMixin, DeleteView):
    model = Link
    permissions_required = 'common:delete_link'
    success_url = reverse_lazy('common:link_list')
    template_name_suffix = '_form'


class LinkPublicDirect(DetailView):
    model = Link

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(
            token__isnull=True
        )

    def get(self, request, *args, **kwargs):
        obj = self.get_object()
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')

        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')

        if settings.DEBUG:
            obj.visit_create(
                ip_address=ip
            )
        else:
            tasks.link_task.delay(
                task='visit_create',
                pk=obj.pk,
                data={'ip_address': ip}
            )
        response = HttpResponse("", status=302)
        response['Location'] = obj.destination
        return response


class LinkPublicToken(DetailView):
    model = Link

    def get_object(self):
        qs = self.get_queryset()
        return qs.get(token=self.kwargs['token'])

    def get(self, request, *args, **kwargs):
        obj = self.get_object()
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')

        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')

        if settings.DEBUG:
            obj.visit_create(
                ip_address=ip
            )
        else:
            tasks.customlink_task.delay(
                task='visit_create',
                pk=obj.pk,
                data={'ip_address': ip}
            )
        response = HttpResponse("", status=302)
        response['Location'] = obj.destination
        return response


class MessageList(CompanyQuerySetMixin, ListView):
    model = Message
    paginate_by = 30
    permissions_required = 'common:view_message'


class MessageDetail(CompanyQuerySetMixin, DetailView):
    model = Message
    permissions_required = 'common:view_message'


class MessageFrame(CompanyQuerySetMixin, DetailView):
    model = Message
    permissions_required = 'common:view_message'
    template_name_suffix = '_frame'


class MessagePixel(
    DetailView
):
    model = Message

    def get_object(self):
        try:
            qs = self.get_queryset()
            return qs.get(token=self.kwargs['token'])
        except ObjectDoesNotExist:
            raise Http404

    def get(self, *args, **kwargs):
        obj = self.get_object()
        obj.set_read()
        return HttpResponse(PIXEL_GIF_DATA, content_type='image/gif')

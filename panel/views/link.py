from django.conf import settings
from django.http import HttpResponse
from django.urls import reverse_lazy
from django.views.generic import (
    CreateView, DeleteView, DetailView, ListView, UpdateView
)

from boilerplate.mixins import (
    ActionListMixin, CreateMessageMixin, DeleteMessageMixin,
    UpdateMessageMixin, UserCreateMixin
)

from core import tasks
from core.models import Link
from core.views.mixins import CompanyCreateMixin, CompanyQuerySetMixin
from core.utils import get_client_ip
from panel import forms


class LinkListView(CompanyQuerySetMixin, ActionListMixin, ListView):
    action_list = ('add', )
    model = Link
    paginate_by = 30
    permission_required = 'core:view_link'
    template_name = 'panel/link/link_list.html'

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(message__isnull=True)


class LinkDetailView(CompanyQuerySetMixin, DetailView):
    model = Link
    permission_required = 'core:view_link'
    template_name = 'panel/link/link_detail.html'


class LinkCreateView(
    UserCreateMixin, CompanyCreateMixin, CreateMessageMixin, CreateView
):
    form_class = forms.LinkForm
    model = Link
    permission_required = 'core:add_link'
    template_name = 'panel/link/link_form.html'


class LinkUpdateView(CompanyQuerySetMixin, UpdateMessageMixin, UpdateView):
    form_class = forms.LinkForm
    model = Link
    permission_required = 'core:change_link'
    template_name = 'panel/link/link_form.html'


class LinkDeleteView(CompanyQuerySetMixin, DeleteMessageMixin, DeleteView):
    model = Link
    permission_required = 'core:delete_link'
    success_url = reverse_lazy('panel:link_list')
    template_name = 'panel/link/link_form.html'


class LinkPublicView(DetailView):
    model = Link

    def get_queryset(self):
        return super().get_queryset().filter(
            is_active=True
        )

    def get(self, request, *args, **kwargs):
        obj = self.get_object()
        ip = get_client_ip(request)
        task = tasks.link_task

        if not settings.DEBUG:
            task = task.delay

        task(
            company_id=obj.company.id,
            task='visit_create',
            pk=obj.pk,
            data={'ip_address': ip}
        )
        response = HttpResponse("", status=302)
        response['Location'] = obj.destination
        return response

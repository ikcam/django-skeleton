from django.conf import settings
from django.http import HttpResponse
from django.urls import reverse_lazy
from django.utils.translation import ugettext_lazy as _
from django.views.generic import (
    CreateView, DeleteView, DetailView, ListView, UpdateView
)

from boilerplate.mixins import (
    ActionListMixin, CreateMessageMixin, DeleteMessageMixin,
    UpdateMessageMixin, UserCreateMixin
)

from core.mixins import CompanyCreateMixin, CompanyQuerySetMixin
from core.models import Link
from core import tasks
from public import forms


class LinkListView(CompanyQuerySetMixin, ActionListMixin, ListView):
    action_list = (
        (_("Add"), 'add', 'primary', 'plus', 'common:add_link'),
    )
    model = Link
    paginate_by = 30
    permission_required = 'core:view_link'
    template_name = 'public/link_list.html'


class LinkDetailView(CompanyQuerySetMixin, DetailView):
    model = Link
    permission_required = 'core:view_link'
    template_name = 'public/link_detail.html'


class LinkCreateView(
    UserCreateMixin, CompanyCreateMixin, CreateMessageMixin, CreateView
):
    form_class = forms.LinkForm
    model = Link
    permission_required = 'core:add_link'
    template_name = 'public/link_form.html'


class LinkUpdateView(CompanyQuerySetMixin, UpdateMessageMixin, UpdateView):
    form_class = forms.LinkForm
    model = Link
    permission_required = 'core:change_link'
    template_name = 'public/link_form.html'


class LinkDeleteView(CompanyQuerySetMixin, DeleteMessageMixin, DeleteView):
    model = Link
    permission_required = 'core:delete_link'
    success_url = reverse_lazy('common:link_list')
    template_name = 'public/link_form.html'


class LinkPublicDirectView(DetailView):
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
            tasks.link_task(
                company_id=obj.company.id,
                task='visit_create',
                pk=obj.pk,
                data={'ip_address': ip}
            )
        else:
            tasks.link_task.delay(
                company_id=obj.company.id,
                task='visit_create',
                pk=obj.pk,
                data={'ip_address': ip}
            )
        response = HttpResponse("", status=302)
        response['Location'] = obj.destination
        return response


class LinkPublicTokenView(DetailView):
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
            tasks.link_task(
                company_id=obj.company.id,
                task='visit_create',
                pk=obj.pk,
                data={'ip_address': ip}
            )
        else:
            tasks.link_task.delay(
                company_id=obj.company.id,
                task='visit_create',
                pk=obj.pk,
                data={'ip_address': ip}
            )
        response = HttpResponse("", status=302)
        response['Location'] = obj.destination
        return response

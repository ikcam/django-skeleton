from django.urls import reverse_lazy
from django.views.generic import (
    CreateView, DeleteView, DetailView, ListView, UpdateView
)

from boilerplate.mixins import (
    ActionListMixin, CreateMessageMixin, DeleteMessageMixin,
    UpdateMessageMixin, UserCreateMixin
)

from core.models import Link
from core.views.mixins import CompanyCreateMixin, CompanyQuerySetMixin
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

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(message__isnull=True, visit__isnull=True)


class LinkDeleteView(CompanyQuerySetMixin, DeleteMessageMixin, DeleteView):
    model = Link
    permission_required = 'core:delete_link'
    success_url = reverse_lazy('panel:link_list')
    template_name = 'panel/link/link_form.html'

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(message__isnull=True, visit_set__isnull=True)

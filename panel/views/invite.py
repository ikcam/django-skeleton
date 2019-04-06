from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, DetailView, ListView

from boilerplate.mixins import (
    ActionListMixin, CreateMessageMixin, DeleteMessageMixin
)

from core import tasks
from core.models import Invite
from core.views.mixins import (
    CompanyCreateMixin, CompanyQuerySetMixin, ModelActionMixin
)
from panel import forms


class InviteListView(
    ActionListMixin, CompanyQuerySetMixin, ListView
):
    action_list = ('add', )
    model = Invite
    paginate_by = 30
    permission_required = 'core:view_invite'
    related_properties = ('user', )
    template_name = 'panel/invite/invite_list.html'


class InviteCreateView(
    CompanyCreateMixin, CreateMessageMixin, CreateView
):
    model = Invite
    permission_required = 'core:add_invite'
    success_url = reverse_lazy('panel:invite_list')
    template_name = 'panel/invite/invite_form.html'

    def get_form_class(self):
        return forms.get_invite_form(self.request.company)


class InviteDeleteView(
    CompanyQuerySetMixin, DeleteMessageMixin, DeleteView
):
    model = Invite
    permission_required = 'core:delete_invite'
    success_url = reverse_lazy('panel:invite_list')
    template_name = 'panel/invite/invite_form.html'

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(
            date_send__isnull=True
        )


class InviteSendView(
    ModelActionMixin, DetailView
):
    model_action = 'send'
    model = Invite
    permission_required = 'core:send_invite'
    success_url = reverse_lazy('panel:invite_list')
    task_module = tasks

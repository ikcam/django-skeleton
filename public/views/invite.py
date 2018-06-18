from django.urls import reverse_lazy
from django.utils.translation import ugettext_lazy as _
from django.views.generic import CreateView, DeleteView, DetailView, ListView

from boilerplate.mixins import (
    ActionListMixin, CreateMessageMixin, DeleteMessageMixin
)

from core import tasks
from core.mixins import (
    CompanyCreateMixin, CompanyQuerySetMixin, ModelActionMixin
)
from core.models import Invite
from public import forms


class InviteListView(
    ActionListMixin, CompanyQuerySetMixin, ListView
):
    action_list = ('add', )
    model = Invite
    paginate_by = 30
    permission_required = 'core:view_invite'
    related_properties = ('user', )
    template_name = 'public/invite_list.html'


class InviteCreateView(
    CompanyCreateMixin, CreateMessageMixin, CreateView
):
    model = Invite
    permission_required = 'core:add_invite'
    template_name = 'public/invite_form.html'

    def get_form_class(self):
        return forms.get_invite_form(self.company)


class InviteDeleteView(
    CompanyQuerySetMixin, DeleteMessageMixin, DeleteView
):
    model = Invite
    permission_required = 'core:delete_invite'
    success_url = reverse_lazy('public:invite_list')
    template_name = 'public/invite_form.html'

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
    task_module = tasks
    success_url = reverse_lazy('core:invite_list')

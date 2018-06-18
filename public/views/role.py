from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, ListView, UpdateView

from boilerplate.mixins import (
    ActionListMixin, CreateMessageMixin, DeleteMessageMixin, UpdateMessageMixin
)
from django_addanother.views import CreatePopupMixin

from core.mixins import (
    CompanyCreateMixin, CompanyQuerySetMixin
)
from core.models import Role
from public import forms


class RoleListView(
    ActionListMixin, CompanyQuerySetMixin, ListView
):
    action_list = ('add', )
    model = Role
    paginate_by = 30
    permission_required = 'core:view_role'
    template_name = 'public/role_list.html'


class RoleCreateView(
    CreatePopupMixin, CompanyCreateMixin, CreateMessageMixin, CreateView
):
    model = Role
    permission_required = 'core:view_role'
    template_name = 'public/role_form.html'

    def get_form_class(self):
        return forms.get_role_form(self.company)


class RoleUpdateView(
    CompanyQuerySetMixin, UpdateMessageMixin, UpdateView
):
    model = Role
    permission_required = 'core:change_role'
    template_name = 'public/role_form.html'

    def get_form_class(self):
        return forms.get_role_form(self.company)


class RoleDeleteView(
    CompanyQuerySetMixin, DeleteMessageMixin, DeleteView
):
    model = Role
    permission_required = 'core:delete_role'
    success_url = reverse_lazy('public:role_list')
    template_name = 'public/role_form.html'

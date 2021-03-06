from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, ListView, UpdateView

from boilerplate.mixins import (
    ActionListMixin, CreateMessageMixin, DeleteMessageMixin, UpdateMessageMixin
)
from django_addanother.views import CreatePopupMixin

from core.models import Role
from core.views.mixins import (
    CompanyCreateMixin, CompanyQuerySetMixin
)
from panel import forms


class RoleListView(
    ActionListMixin, CompanyQuerySetMixin, ListView
):
    action_list = ('add', )
    model = Role
    paginate_by = 30
    permission_required = 'core:view_role'
    template_name = 'panel/role/role_list.html'


class RoleCreateView(
    CreatePopupMixin, CompanyCreateMixin, CreateMessageMixin, CreateView
):
    model = Role
    permission_required = 'core:view_role'
    success_url = reverse_lazy('panel:role_list')
    template_name = 'panel/role/role_form.html'

    def get_form_class(self):
        return forms.get_role_form(self.request.company)


class RoleUpdateView(
    CompanyQuerySetMixin, UpdateMessageMixin, UpdateView
):
    model = Role
    permission_required = 'core:change_role'
    success_url = reverse_lazy('panel:role_list')
    template_name = 'panel/role/role_form.html'

    def get_form_class(self):
        return forms.get_role_form(self.request.company)


class RoleDeleteView(
    CompanyQuerySetMixin, DeleteMessageMixin, DeleteView
):
    model = Role
    permission_required = 'core:delete_role'
    success_url = reverse_lazy('panel:role_list')
    template_name = 'panel/role/role_form.html'

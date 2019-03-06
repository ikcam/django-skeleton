from django.contrib import messages
from django.contrib.auth.forms import SetPasswordForm
from django.urls import reverse_lazy
from django.utils.translation import ugettext_lazy as _
from django.shortcuts import redirect
from django.views.generic import CreateView, DetailView, ListView, UpdateView

from boilerplate.mixins import (
    ActionListMixin, CreateMessageMixin, UpdateMessageMixin
)

from core.mixins import (
    CompanyCreateMixin, CompanyQuerySetMixin, ModelActionMixin
)
from core.models import Colaborator, User
from public import forms


class UserListView(
    ActionListMixin, CompanyQuerySetMixin, ListView
):
    action_list = ('add', )
    model = User
    paginate_by = 30
    template_name = 'public/user_list.html'
    permission_required = 'core:view_user'

    def get_queryset(self):
        qs = super().get_queryset().filter(
            colaborator__company=self.company
        )
        if not self.request.user.is_superuser:
            qs = qs.filter(
                is_superuser=False
            )
        if not self.request.user.is_staff:
            qs = qs.filter(
                is_staff=False
            )
        return qs


class UserCreateView(
    CompanyCreateMixin, CreateMessageMixin, CreateView
):
    form_class = forms.UserCreateForm
    model = User
    template_name = 'public/user_form.html'
    success_url = reverse_lazy("public:user_list")
    permission_required = 'core:add_user'

    def form_valid(self, form):
        form.instance.first_name = form.cleaned_data.get('first_name')
        form.instance.last_name = form.cleaned_data.get('last_name')
        form.instance.email = form.cleaned_data.get('email')
        form.instance.company = self.company
        form.instance.language = self.company.language

        return super().form_valid(form)


class UserUpdateView(
    CompanyQuerySetMixin, UpdateMessageMixin, UpdateView
):
    form_class = forms.UserUpdateForm
    model = User
    permission_required = 'core:change_user'
    template_name = 'public/user_form.html'
    success_url = reverse_lazy("public:user_list")

    def get_queryset(self):
        qs = super().get_queryset().filter(
            colaborator__company=self.company
        )
        if not self.request.user.is_superuser:
            qs = qs.filter(
                is_superuser=False
            )
        if not self.request.user.is_staff:
            qs = qs.filter(
                is_staff=False
            )
        return qs


class UserPasswordView(
    CompanyQuerySetMixin, UpdateMessageMixin, UpdateView
):
    form_class = SetPasswordForm
    model = User
    permission_required = 'core:change_user'
    template_name = 'public/user_form.html'

    def get_form(self):
        kwargs = self.get_form_kwargs()
        kwargs.pop('instance')

        return self.get_form_class()(
            user=self.get_object(), **kwargs
        )


class UserPermissionsView(
    CompanyQuerySetMixin, UpdateMessageMixin, UpdateView
):
    model = Colaborator
    permission_required = 'core:change_user'
    success_url = reverse_lazy('core:user_list')
    template_name = 'public/user_form.html'

    def get_form_class(self):
        return forms.get_colaborator_form(self.company)


class UserRemoveView(
    ModelActionMixin, DetailView
):
    model_action = 'user.company_remove'
    model = Colaborator
    permission_required = 'core:remove_colaborator'
    require_confirmation = True
    success_url = reverse_lazy('public:user_list')
    template_name = 'public/user_form.html'

    def get_queryset(self):
        qs = super().get_queryset()
        if not self.request.user.is_superuser:
            qs = qs.filter(
                user__is_superuser=False
            )
        if not self.request.user.is_staff:
            qs = qs.filter(
                user__is_staff=False
            )
        return qs.exclude(pk=self.request.user.pk)

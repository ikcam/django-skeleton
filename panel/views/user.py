from django.contrib.auth.forms import SetPasswordForm
from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView, UpdateView

from boilerplate.mixins import (
    ActionListMixin, CreateMessageMixin, UpdateMessageMixin
)

from core.models import Colaborator, User
from core.views.mixins import (
    CompanyCreateMixin, CompanyQuerySetMixin, CompanyRequiredMixin
)
from panel import forms


class UserListView(
    ActionListMixin, CompanyRequiredMixin, ListView
):
    action_list = ('add', )
    model = User
    paginate_by = 30
    template_name = 'panel/user/user_list.html'
    permission_required = 'core:view_user'

    def get_queryset(self):
        qs = super().get_queryset().filter(
            colaborator__company=self.request.company
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
    template_name = 'panel/user/user_form.html'
    success_url = reverse_lazy("panel:user_list")
    permission_required = 'core:add_user'

    def form_valid(self, form):
        form.instance.first_name = form.cleaned_data.get('first_name')
        form.instance.last_name = form.cleaned_data.get('last_name')
        form.instance.email = form.cleaned_data.get('email')
        form.instance.company = self.request.company
        form.instance.language = self.request.company.language

        return super().form_valid(form)


class UserUpdateView(
    CompanyRequiredMixin, UpdateMessageMixin, UpdateView
):
    form_class = forms.UserUpdateForm
    model = User
    permission_required = 'core:change_user'
    template_name = 'panel/user/user_form.html'
    success_url = reverse_lazy("panel:user_list")

    def get_queryset(self):
        qs = super().get_queryset().filter(
            colaborator__company=self.request.company
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
    CompanyRequiredMixin, UpdateMessageMixin, UpdateView
):
    form_class = SetPasswordForm
    model = User
    permission_required = 'core:change_user'
    success_url = reverse_lazy('panel:user_list')
    template_name = 'panel/user/user_form.html'

    def get_queryset(self):
        qs = super().get_queryset().filter(
            colaborator__company=self.request.company
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
    success_url = reverse_lazy('panel:user_list')
    template_name = 'public/user_form.html'

    def get_form_class(self):
        return forms.get_colaborator_form(self.request.company)

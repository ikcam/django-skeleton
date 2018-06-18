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
    model = Colaborator
    paginate_by = 30
    template_name = 'public/user_list.html'
    permission_required = 'core:view_colaborator'


class UserCreateView(
    CompanyCreateMixin, CreateMessageMixin, CreateView
):
    form_class = forms.UserCreateForm
    model = User
    template_name = 'public/user_form.html'
    success_url = reverse_lazy("public:user_list")
    permission_required = 'core:add_colaborator'

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
    form_class = forms.UserChangeForm
    model = User
    permission_required = 'auth:change_colaborator'
    template_name = 'public/user_form.html'
    success_url = reverse_lazy("public:user_list")


class UserPasswordView(
    CompanyQuerySetMixin, UpdateMessageMixin, UpdateView
):
    form_class = SetPasswordForm
    model = User
    permission_required = 'core:change_colaborator'
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
    model = Colaborator
    permission_required = 'core:delete_colaborator'
    require_confirmation = True
    template_name = 'public/user_form.html'

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.all().exclude(pk=self.request.user.pk)

    def post(self, request, *args, **kwargs):
        obj = self.get_object()
        company = self.request.user.company

        obj.company_remove(company, request.user)

        messages.success(
            request,
            _(
                "%(object)s has been removed "
                "from your company %(company)s."
            ) % dict(
                object=obj,
                company=company
            )
        )
        return redirect(reverse_lazy('core:user_list'))

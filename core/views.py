from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.contrib import messages
from django.urls import reverse_lazy
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect
from django.utils.translation import ugettext_lazy as _
from django.views.generic import DetailView, TemplateView
from django.views.generic.edit import CreateView, DeleteView, UpdateView

from boilerplate.mixins import (
    CreateMessageMixin, DeleteMessageMixin, UpdateMessageMixin, UserCreateMixin
)

from . import forms, tasks
from .mixins import (
    CompanyCreateMixin, CompanyQuerySetMixin, CompanyRequiredMixin
)
from .models import Company, Invite


class Index(TemplateView):
    template_name = 'core/index.html'


class CompanyDetail(
    CompanyRequiredMixin, DetailView
):
    model = Company

    def get_object(self):
        if (
            self.company.user == self.request.user or
            self.request.user.is_staff
        ):
            return self.company

        raise PermissionDenied


class CompanyCreate(
    LoginRequiredMixin, UserCreateMixin, CreateMessageMixin, CreateView
):
    form_class = forms.CompanyForm
    model = Company


class CompanyUpdate(
    CompanyRequiredMixin, UpdateMessageMixin, UpdateView
):
    form_class = forms.CompanyForm
    model = Company

    def get_object(self):
        qs = self.get_queryset()
        obj = qs.get(pk=self.request.user.profile.company.pk)

        if obj.user == self.request.user:
            return obj

        raise PermissionDenied


class CompanySwitch(
    CompanyRequiredMixin, DetailView
):
    model = Company
    success_url = reverse_lazy('core:index')

    def get(self, request, *args, **kwargs):
        obj = self.get_object()
        request.user.profile.company_switch(obj)
        messages.success(
            request,
            _("You have saccessfully switched to: %s") % obj
        )
        return redirect(self.get_success_url())

    def get_success_url(self):
        next_ = self.request.GET.get('next', None)

        return next_ or self.success_url


class InviteCreate(
    CompanyCreateMixin, CreateMessageMixin, CreateView
):
    form_class = forms.InviteForm
    model = Invite
    success_url = reverse_lazy('core:company_detail')

    def dispatch(self, request, *args, **kwargs):
        response = super().dispatch(request, *args, **kwargs)

        if self.company.user != request.user:
            raise PermissionDenied

        return response


class InviteDelete(
    CompanyQuerySetMixin, DeleteMessageMixin, DeleteView
):
    model = Invite
    success_url = reverse_lazy('core:company_detail')
    template_name_suffix = '_form'

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(
            company__user=self.request.user
        )


class InviteSend(
    CompanyQuerySetMixin, DetailView
):
    model = Invite

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(
            company__user=self.request.user
        )

    def get(self, request, *args, **kwargs):
        obj = self.get_object()

        if settings.DEBUG:
            obj.send()
        else:
            tasks.invite_task.delay(obj.pk, 'send')

        return redirect(reverse_lazy('core:company_detail'))


class UserRemove(
    CompanyRequiredMixin, DetailView
):
    model = User
    template_name_suffix = '_form'

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(
            profile__company__user=self.request.user
        ).exclude(pk=self.request.user.pk)

    def post(self, request, *args, **kwargs):
        obj = self.get_object()
        company = self.request.user.profile.company

        obj.profile.company_remove(company, self.request.user)

        messages.success(
            request,
            _("%s has been removed from your company %s.") % (
                obj,
                company
            )
        )
        return redirect(reverse_lazy('core:company_detail'))

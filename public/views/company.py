from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.http import Http404
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import (
    CreateView, DetailView, FormView, ListView, UpdateView
)

from boilerplate.mixins import (
    CreateMessageMixin, UpdateMessageMixin, UserCreateMixin
)

from core.mixins import CompanyRequiredMixin
from core.models import Company, Invoice
from public import forms


class CompanyActivateView(
    LoginRequiredMixin, FormView
):
    form_class = forms.CulqiTokenForm
    model = Invoice
    template_name = 'public/company_activate.html'

    def get_queryset(self):
        qs = self.model.objects.all()

        return qs.filter(
            company__is_active=False
        )

    def get_object(self):
        if not self.request.user.is_authenticated:
            raise Http404

        company = self.request.user.company

        if not company or not company.last_invoice:
            raise PermissionDenied

        if not company.is_active and company.last_invoice.is_payed:
            company.activate()

        try:
            return self.get_queryset().get(
                pk=company.last_invoice.pk
            )
        except Invoice.DoesNotExist:
            raise PermissionDenied

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['object'] = self.get_object()
        return context

    def form_valid(self, form):
        obj = self.get_object()
        obj.create_payment_from_culqi(**form.cleaned_data)

        return super().form_valid(form)


class CompanyDetailView(
    CompanyRequiredMixin, DetailView
):
    model = Company
    permission_required = 'core:view_company'
    template_name = 'public/company_detail.html'

    def get_object(self):
        if (
            self.company.user == self.request.user or
            self.request.user.is_staff
        ):
            return self.company

        raise PermissionDenied


class CompanyChooseView(
    LoginRequiredMixin, ListView
):
    model = Company
    template_name = 'public/company_choose.html'

    def get_queryset(self):
        return self.request.user.companies.all()


class CompanyCreateView(
    LoginRequiredMixin, UserCreateMixin, CreateMessageMixin, CreateView
):
    form_class = forms.CompanyCreateForm
    model = Company
    template_name = 'public/company_create.html'


class CompanySwitchView(
    LoginRequiredMixin, DetailView
):
    model = Company
    success_url = reverse_lazy('public:dashboard')

    def get(self, request, *args, **kwargs):
        super().get(request, *args, **kwargs)

        level, message = request.user.company_switch(self.object)
        getattr(messages, level)(request, message)

        return redirect(self.get_success_url())

    def get_success_url(self):
        next_ = self.request.GET.get('next', None)
        return next_ or self.success_url


class CompanyUpdateView(
    CompanyRequiredMixin, UpdateMessageMixin, UpdateView
):
    form_class = forms.CompanyForm
    model = Company
    permission_required = 'core:change_company'
    template_name = 'public/company_form.html'

    def get_form_class(self):
        user = self.request.user
        if (
            (user.is_superuser or user.is_staff) and
            user.has_perm('core:change_company')
        ):
            return forms.CompanyAdminForm
        return self.form_class

    def get_object(self):
        return self.request.user.company

from django.http import Http404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import DetailView, UpdateView

from boilerplate.mixins import UpdateMessageMixin

from core.models import Company
from core.views.mixins import CompanyRequiredMixin
from panel import forms


class CompanyActivateView(LoginRequiredMixin, DetailView):
    model = Company
    permission_required = 'core:view_company'
    template_name = 'panel/company/company_activate.html'

    def get(self, request, *args, **kwargs):
        if request.company.is_active:
            raise Http404
        return super().get(request, *args, **kwargs)

    def get_object(self):
        return self.request.company


class CompanyDetailView(CompanyRequiredMixin, DetailView):
    model = Company
    permission_required = 'core:view_company'
    template_name = 'panel/company/company_detail.html'

    def get_object(self):
        return self.request.company


class CompanyUpdateView(UpdateMessageMixin, CompanyRequiredMixin, UpdateView):
    form_class = forms.CompanyForm
    model = Company
    permission_required = 'core:change_company'
    success_url = reverse_lazy('panel:company_detail')
    template_name = 'panel/company/company_form.html'

    def get_object(self):
        return self.request.company

from django.http import Http404
from django.views.generic import ListView, FormView

from core.mixins import CompanyQuerySetMixin

from core.models import Invoice
from public import forms


class InvoiceListView(
    CompanyQuerySetMixin, ListView
):
    model = Invoice
    paginate_by = 30
    permission_required = 'core:view_invoice'
    template_name = 'public/invoice_list.html'


class InvoiceDetailView(
    CompanyQuerySetMixin, FormView
):
    form_class = forms.CulqiTokenForm
    model = Invoice
    template_name = 'public/invoice_detail.html'
    permission_required = 'core:view_invoice'

    def get_object(self):
        try:
            obj = self.get_queryset().get(
                company=self.company,
                pk=self.kwargs['pk']
            )
            return obj
        except self.model.DoesNotExist:
            raise Http404

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['object'] = self.get_object()
        return context

    def form_valid(self, form):
        obj = self.get_object()
        obj.create_payment_from_culqi(**form.cleaned_data)

        return super().form_valid(form)

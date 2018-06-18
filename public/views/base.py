from django.shortcuts import redirect
from django.views.generic import TemplateView

from core.mixins import CompanyRequiredMixin


class IndexView(TemplateView):
    template_name = 'public/index.html'


class DashboardView(CompanyRequiredMixin, TemplateView):
    raise_exception = True
    template_name = 'public/dashboard.html'

    def get_context_data(self, **kwargs):
        kwargs['hide_page_header'] = True
        return super().get_context_data(**kwargs)

    def handle_no_permission(self, msg=None):
        return redirect('public:company_choose')

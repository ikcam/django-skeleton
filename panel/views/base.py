from django.views.generic import TemplateView

from core.views.mixins import CompanyRequiredMixin


class IndexView(CompanyRequiredMixin, TemplateView):
    template_name = 'panel/index.html'

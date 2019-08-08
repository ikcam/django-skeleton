from django.contrib.auth import logout as auth_logout
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from django.views.generic import TemplateView

from core.views.mixins import CompanyRequiredMixin


class IndexView(CompanyRequiredMixin, TemplateView):
    template_name = 'panel/index.html'

    def handle_no_permission(self):
        if (
            not self.request.user.is_authenticated or
            not hasattr(self.request.user, 'is_staff')
        ):
            auth_logout(self.request)
            return HttpResponseRedirect(reverse_lazy('panel:account_login'))
        return super().handle_no_permission()

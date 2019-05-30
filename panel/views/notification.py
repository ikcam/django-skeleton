from django.shortcuts import HttpResponseRedirect
from django.views.generic import DetailView, ListView

from core.models import Notification
from core.views.mixins import CompanyQuerySetMixin


class NotificationDetailView(CompanyQuerySetMixin, DetailView):
    model = Notification

    def get(self, request, *args, **kwargs):
        obj = self.get_object()
        obj.set_read()
        return HttpResponseRedirect(obj.destination)


class NotificationListView(CompanyQuerySetMixin, ListView):
    model = Notification
    paginate_by = 30

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(user=self.request.user)

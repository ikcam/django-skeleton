from django.shortcuts import HttpResponseRedirect
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import DetailView, ListView

from core.models import Notification
from core.views.mixins import CompanyQuerySetMixin


class NotificationDetailView(CompanyQuerySetMixin, DetailView):
    model = Notification

    def get(self, request, *args, **kwargs):
        obj = self.get_object()
        obj.set_read()
        return HttpResponseRedirect(obj.destination)


class NotificationListView(CompanyQuerySetMixin, DetailView):
    model = Notification
    paginate_by = 30

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(user=self.request.user)


class NotificationReadAllView(CompanyQuerySetMixin, ListView):
    model = Notification
    success_url = reverse_lazy('account:user_detail')

    def get(self, request, *args, **kwargs):
        qs = self.get_queryset()
        qs.filter(date_read__isnull=True).update(date_read=timezone.now())

        next_ = request.GET.get('next')
        if next_:
            return HttpResponseRedirect(next_)
        else:
            return HttpResponseRedirect(self.success_url)

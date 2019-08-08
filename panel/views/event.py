from django.urls import reverse_lazy
from django.views.generic import (
    CreateView, DeleteView, DetailView, ListView, UpdateView
)

from boilerplate.mixins import (
    ActionListMixin, CreateMessageMixin, DeleteMessageMixin,
    UpdateMessageMixin, UserCreateMixin
)

from core.views.mixins import CompanyCreateMixin, CompanyQuerySetMixin
from core.models import Event
from panel import forms


class EventListView(ActionListMixin, CompanyQuerySetMixin, ListView):
    action_list = ('add', )
    model = Event
    paginate_by = 30
    permission_required = 'core:view_event'
    template_name = 'panel/event/event_list.html'

    def get_queryset(self):
        return self.model.objects.none()


class EventDetailView(CompanyQuerySetMixin, DetailView):
    model = Event
    permission_required = 'core:view_event'
    template_name = 'panel/event/event_detail.html'


class EventCreateView(
    UserCreateMixin, CompanyCreateMixin, CreateMessageMixin, CreateView
):
    model = Event
    permission_required = 'core:add_event'
    template_name = 'panel/event/event_form.html'

    def get_form_class(self):
        return forms.get_event_form(self.request.company)


class EventUpdateView(CompanyQuerySetMixin, UpdateMessageMixin, UpdateView):
    model = Event
    permission_required = 'core:change_event'
    template_name = 'panel/event/event_form.html'

    def get_form_class(self):
        return forms.get_event_form(self.request.company)


class EventDeleteView(CompanyQuerySetMixin, DeleteMessageMixin, DeleteView):
    model = Event
    permission_required = 'core:delete_event'
    success_url = reverse_lazy('panel:event_list')
    template_name = 'panel/event/event_form.html'


class EventPublicView(DetailView):
    model = Event
    template_name = 'public/event_public.html'

    def get_queryset(self, queryset=None):
        qs = super().get_queryset(queryset)
        return qs.filter(
            company=self.request.company,
            is_public=True,
        )

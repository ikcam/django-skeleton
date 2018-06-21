from django.http import Http404
from django.urls import reverse_lazy
from django.views.generic import (
    CreateView, DeleteView, DetailView, ListView, UpdateView
)

from boilerplate.mixins import (
    ActionListMixin, CreateMessageMixin, DeleteMessageMixin,
    UpdateMessageMixin, UserCreateMixin
)

from core.mixins import CompanyCreateMixin, CompanyQuerySetMixin
from core.models import Company, Event
from public import forms


class EventListView(ActionListMixin, CompanyQuerySetMixin, ListView):
    action_list = ('add', )
    model = Event
    paginate_by = 30
    permission_required = 'core:view_event'
    template_name = 'public/event_list.html'

    def get_queryset(self):
        return self.model.objects.none()


class EventDetailView(CompanyQuerySetMixin, DetailView):
    model = Event
    permission_required = 'core:view_event'
    template_name = 'public/event_detail.html'


class EventCreateView(
    UserCreateMixin, CompanyCreateMixin, CreateMessageMixin, CreateView
):
    model = Event
    permission_required = 'core:add_event'
    template_name = 'public/event_form.html'

    def get_form_class(self):
        return forms.get_event_form(self.company)


class EventUpdateView(CompanyQuerySetMixin, UpdateMessageMixin, UpdateView):
    model = Event
    permission_required = 'core:change_event'
    template_name = 'public/event_form.html'

    def get_form_class(self):
        return forms.get_event_form(self.company)


class EventDeleteView(CompanyQuerySetMixin, DeleteMessageMixin, DeleteView):
    model = Event
    permission_required = 'core:delete_event'
    success_url = reverse_lazy('public:event_list')
    template_name = 'public/event_form.html'


class EventPublicView(DetailView):
    model = Event
    template_name_suffix = '_public'

    def get_company(self):
        try:
            return Company.objects.get(
                slug=self.kwargs['slug']
            )
        except Company.DoesNotExist:
            raise Http404

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(
            company=self.get_company(),
            is_public=True,
        )

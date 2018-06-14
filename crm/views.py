from django.views.generic import (
    CreateView, DeleteView, DetailView, ListView, TemplateView, UpdateView
)
from django.urls import reverse_lazy
from django.utils.translation import ugettext_lazy as _

from boilerplate.mixins import (
    ActionListMixin, CreateMessageMixin, DeleteMessageMixin,
    UpdateMessageMixin, UserCreateMixin
)
from django_addanother.views import CreatePopupMixin

from core.mixins import (
    CompanyCreateMixin, CompanyQuerySetMixin, CompanyRequiredMixin
)
from . import forms, models


class AppView(CompanyRequiredMixin, TemplateView):
    template_name = 'crm/app.html'


class CustomerListView(
    ActionListMixin, CompanyQuerySetMixin, ListView
):
    action_list = (
        (_("Add"), 'add', 'primary', 'plus', 'crm:add_customer'),
    )
    model = models.Customer
    paginate_by = 30
    permission_required = 'crm:view_customer'


class CustomerDetailView(
    CompanyQuerySetMixin, DetailView
):
    model = models.Customer
    permission_required = 'crm:view_customer'


class CustomerCreateView(
    CreatePopupMixin, UserCreateMixin, CompanyCreateMixin, CreateMessageMixin,
    CreateView
):
    model = models.Customer
    permission_required = 'crm:add_customer'

    def get_form_class(self):
        return forms.get_customer_model_form(self.company)


class CustomerUpdateView(
    CompanyQuerySetMixin, UpdateMessageMixin, UpdateView
):
    model = models.Customer
    permission_required = 'crm:change_customer'

    def get_form_class(self):
        return forms.get_customer_model_form(self.company)


class CustomerDeleteView(
    CompanyQuerySetMixin, DeleteMessageMixin, DeleteView
):
    model = models.Customer
    permission_required = 'crm:delete_customer'
    success_url = reverse_lazy('crm:customer_list')
    template_name_suffix = '_form'


class JobDescriptionListView(
    ActionListMixin, CompanyQuerySetMixin, ListView
):
    action_list = (
        (_("Add"), 'add', 'primary', 'plus', 'crm:add_jobdescription'),
    )
    model = models.JobDescription
    paginate_by = 30
    permission_required = 'crm:view_jobdescription'


class JobDescriptionDetailView(
    CompanyQuerySetMixin, DetailView
):
    model = models.JobDescription
    permission_required = 'crm:view_jobdescription'


class JobDescriptionCreateView(
    CreatePopupMixin, CompanyCreateMixin, CreateMessageMixin, CreateView
):
    model = models.JobDescription
    permission_required = 'crm:add_jobdescription'

    def get_form_class(self):
        return forms.get_jobdescription_model_form(self.company)


class JobDescriptionUpdateView(
    CompanyQuerySetMixin, UpdateMessageMixin, UpdateView
):
    model = models.JobDescription
    permission_required = 'crm:change_jobdescription'

    def get_form_class(self):
        return forms.get_jobdescription_model_form(self.company)


class JobDescriptionDeleteView(
    CompanyQuerySetMixin, DeleteMessageMixin, DeleteView
):
    model = models.JobDescription
    permission_required = 'crm:delete_jobdescription'
    success_url = reverse_lazy('crm:jobdescription_list')
    template_name_suffix = '_form'


class OpportunityListView(
    ActionListMixin, CompanyQuerySetMixin, ListView
):
    action_list = (
        (_("Add"), 'add', 'primary', 'plus', 'crm:add_customer'),
    )
    model = models.Opportunity
    paginate_by = 30
    permission_required = 'crm:view_customer'


class OpportunityDetailView(
    CompanyQuerySetMixin, DetailView
):
    model = models.Opportunity
    permission_required = 'crm:view_opportunity'


class OpportunityCreateView(
    CreatePopupMixin, UserCreateMixin, CompanyCreateMixin, CreateMessageMixin,
    CreateView
):
    model = models.Opportunity
    permission_required = 'crm:add_opportunity'

    def get_form_class(self):
        return forms.get_opportunity_model_form(self.company)


class OpportunityUpdateView(
    CompanyQuerySetMixin, UpdateMessageMixin, UpdateView
):
    model = models.Opportunity
    permission_required = 'crm:change_opportunity'

    def get_form_class(self):
        return forms.get_opportunity_model_form(self.company)


class OpportunityDeleteView(
    CompanyQuerySetMixin, DeleteMessageMixin, DeleteView
):
    model = models.Opportunity
    permission_required = 'crm:delete_opportunity'
    success_url = reverse_lazy('crm:opportunity_list')
    template_name_suffix = '_form'


class SourceListView(
    ActionListMixin, CompanyQuerySetMixin, ListView
):
    action_list = (
        (_("Add"), 'add', 'primary', 'plus', 'crm:add_source'),
    )
    model = models.Source
    paginate_by = 30
    permission_required = 'crm:view_source'


class SourceDetailView(
    CompanyQuerySetMixin, DetailView
):
    model = models.Source
    permission_required = 'crm:view_source'


class SourceCreateView(
    CreatePopupMixin, CompanyCreateMixin, CreateMessageMixin, CreateView
):
    model = models.Source
    permission_required = 'crm:add_source'

    def get_form_class(self):
        return forms.get_source_model_form(self.company)


class SourceUpdateView(
    CompanyQuerySetMixin, UpdateMessageMixin, UpdateView
):
    model = models.Source
    permission_required = 'crm:change_source'

    def get_form_class(self):
        return forms.get_source_model_form(self.company)


class SourceDeleteView(
    CompanyQuerySetMixin, DeleteMessageMixin, DeleteView
):
    model = models.Source
    permission_required = 'crm:delete_source'
    success_url = reverse_lazy('crm:source_list')
    template_name_suffix = '_form'


class StatusListView(
    ActionListMixin, CompanyQuerySetMixin, ListView
):
    action_list = (
        (_("Add"), 'add', 'primary', 'plus', 'crm:add_status'),
    )
    model = models.Status
    paginate_by = 30
    permission_required = 'crm:view_status'


class StatusDetailView(
    CompanyQuerySetMixin, DetailView
):
    model = models.Status
    permission_required = 'crm:view_status'


class StatusCreateView(
    CreatePopupMixin, CompanyCreateMixin, CreateMessageMixin, CreateView
):
    model = models.Status
    permission_required = 'crm:add_status'

    def get_form_class(self):
        return forms.get_status_model_form(self.company)


class StatusUpdateView(
    CompanyQuerySetMixin, UpdateMessageMixin, UpdateView
):
    model = models.Status
    permission_required = 'crm:change_status'

    def get_form_class(self):
        return forms.get_status_model_form(self.company)


class StatusDeleteView(
    CompanyQuerySetMixin, DeleteMessageMixin, DeleteView
):
    model = models.Status
    permission_required = 'crm:delete_status'
    success_url = reverse_lazy('crm:status_list')
    template_name_suffix = '_form'

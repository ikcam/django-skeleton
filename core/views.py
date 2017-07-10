from django.contrib import messages
from django.contrib.auth.forms import SetPasswordForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.core.exceptions import PermissionDenied
from django.http import Http404
from django.urls import reverse_lazy
from django.shortcuts import redirect
from django.utils.translation import ugettext_lazy as _
from django.views.generic import DetailView, ListView, TemplateView
from django.views.generic.edit import (
    CreateView, DeleteView, FormView, UpdateView
)

from boilerplate.mixins import (
    ActionListMixin, CreateMessageMixin, DeleteMessageMixin,
    ExtraFormsAndFormsetsMixin, UpdateMessageMixin, UserCreateMixin
)

from account.forms import UserCreateForm, UserProfileForm
from account.models import Colaborator
from .mixins import (
    CompanyCreateMixin, CompanyQuerySetMixin, CompanyRequiredMixin
)
from .models import Company, Invite, Invoice
from . import forms, tasks


class Index(TemplateView):
    template_name = 'core/index.html'

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated and request.user.profile.company:
            return redirect(reverse_lazy('core:dashboard'))

        return super().get(request, *args, **kwargs)


class Dashboard(LoginRequiredMixin, TemplateView):
    raise_exception = False
    template_name = 'core/dashboard.html'

    def get(self, request, *args, **kwargs):
        if not request.user.profile.company:
            return redirect(reverse_lazy('core:company_add'))

        return super().get(request, *args, **kwargs)


class CompanyActivate(
    LoginRequiredMixin, FormView
):
    form_class = forms.CulqiTokenForm
    model = Invoice
    template_name = 'core/company_activate.html'

    def get_queryset(self):
        qs = self.model.objects.all()

        return qs.filter(
            company__is_active=False
        )

    def get_object(self):
        if not self.request.user.is_authenticated:
            raise Http404

        company = self.request.user.profile.company

        if not company or not company.last_invoice:
            raise PermissionDenied

        if not company.is_active and company.last_invoice.is_payed:
            company.activate()

        qs = self.get_queryset()

        try:
            return qs.get(
                pk=company.last_invoice.pk
            )
        except Exception:
            raise PermissionDenied

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['object'] = self.get_object()
        return context

    def form_valid(self, form):
        obj = self.get_object()

        obj.create_payment_from_culqi(
            **form.cleaned_data
        )

        return super().form_valid(form)


class CompanyDetail(
    CompanyRequiredMixin, DetailView
):
    model = Company
    permissions_required = 'core:view_company'

    def get_object(self):
        if (
            self.company.user == self.request.user or
            self.request.user.is_staff
        ):
            return self.company

        raise PermissionDenied


class CompanyCreate(
    LoginRequiredMixin, UserCreateMixin, CreateMessageMixin, CreateView
):
    form_class = forms.CompanyCreateForm
    model = Company
    template_name = 'core/company_create.html'


class CompanyUpdate(
    CompanyRequiredMixin, UpdateMessageMixin, UpdateView
):
    form_class = forms.CompanyForm
    model = Company
    permissions_required = 'core:change_company'

    def get_object(self):
        qs = self.get_queryset()
        obj = qs.get(pk=self.request.user.profile.company.pk)

        if obj.user == self.request.user:
            return obj

        raise PermissionDenied


class CompanyChoose(
    LoginRequiredMixin, ListView
):
    model = Company
    template_name = 'core/company_choose.html'

    def get_queryset(self):
        return self.request.user.profile.companies.all()


class CompanySwitch(
    LoginRequiredMixin, DetailView
):
    model = Company
    success_url = reverse_lazy('core:index')

    def get(self, request, *args, **kwargs):
        obj = self.get_object()
        request.user.profile.company_switch(obj)
        messages.success(
            request,
            _("You have saccessfully switched to: %s") % obj
        )
        return redirect(self.get_success_url())

    def get_success_url(self):
        next_ = self.request.GET.get('next', None)

        return next_ or self.success_url


class InvoiceList(
    CompanyQuerySetMixin, ListView
):
    model = Invoice
    paginate_by = 30
    permissions_required = 'core:view_invoice'


class InvoiceDetail(
    CompanyQuerySetMixin, FormView
):
    form_class = forms.CulqiTokenForm
    model = Invoice
    success_url = reverse_lazy('core:invoice_list')
    template_name = 'core/invoice_detail.html'
    permissions_required = 'core:view_invoice'

    def get_object(self):
        try:
            obj = self.model.objects.get(
                company=self.company,
                pk=self.kwargs['pk']
            )
        except Exception:
            raise Http404

        return obj

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['object'] = self.get_object()
        return context

    def form_valid(self, form):
        obj = self.get_object()

        obj.create_payment_from_culqi(
            **form.cleaned_data
        )

        return super().form_valid(form)


class InviteList(
    ActionListMixin, CompanyQuerySetMixin, ListView
):
    action_list = (
        (_("Add"), 'add', 'primary', 'plus'),
    )
    model = Invite
    paginate_by = 30
    permissions_required = 'core:view_invite'


class InviteCreate(
    CompanyCreateMixin, CreateMessageMixin, CreateView
):
    form_class = forms.InviteForm
    model = Invite
    permissions_required = 'core:add_invite'
    success_url = reverse_lazy('core:invite_list')


class InviteDelete(
    CompanyQuerySetMixin, DeleteMessageMixin, DeleteView
):
    model = Invite
    success_url = reverse_lazy('core:company_detail')
    template_name_suffix = '_form'
    permissions_required = 'core:delete_invite'

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(
            company__user=self.request.user
        )


class InviteSend(
    CompanyQuerySetMixin, DetailView
):
    model_action = 'send'
    model = Invite
    permissions_required = 'core:add_invite'
    task_module = tasks
    success_url = reverse_lazy('core:invite_list')


class UserList(
    CompanyRequiredMixin, ListView
):
    model = User
    paginate_by = 30
    template_name = 'core/user_list.html'
    permissions_required = 'auth:view_user'

    def get_queryset(self):
        return self.company.users_all.all()


class UserCreate(
    CompanyRequiredMixin, CreateMessageMixin, CreateView
):
    form_class = UserCreateForm
    model = User
    template_name = 'core/user_form.html'
    success_url = reverse_lazy("core:user_list")
    permissions_required = 'auth:add_user'

    def form_valid(self, form):
        form.instance.first_name = form.cleaned_data.get('first_name')
        form.instance.last_name = form.cleaned_data.get('last_name')
        form.instance.email = form.cleaned_data.get('email')

        response = super().form_valid(form)

        if not hasattr(self, 'object'):
            raise Exception("An error has ocurred.")

        self.object.profile.company = self.company
        self.object.profile.save()
        self.object.profile.colaborator_set.create(company=self.company)

        return response


class UserUpdate(
    CompanyRequiredMixin, ExtraFormsAndFormsetsMixin, UpdateMessageMixin,
    UpdateView
):
    extra_form_list = (
        ('profile', 'user', UserProfileForm),
    )
    form_class = forms.UserChangeForm
    model = User
    permissions_required = 'auth:change_user'
    template_name = 'core/user_form.html'
    success_url = reverse_lazy("core:user_list")


class UserPassword(
    CompanyRequiredMixin, UpdateMessageMixin, UpdateView
):
    form_class = SetPasswordForm
    model = User
    permissions_required = 'auth:change_user'
    template_name = 'core/user_form.html'

    def get_form(self):
        kwargs = self.get_form_kwargs()
        kwargs.pop('instance')

        return self.get_form_class()(
            user=self.get_object(), **kwargs
        )


class UserPermissions(
    CompanyQuerySetMixin, UpdateMessageMixin, UpdateView
):
    form_class = forms.ColaboratorForm
    model = Colaborator
    permissions_required = 'auth:change_user'
    success_url = reverse_lazy('core:user_list')
    template_name = 'core/user_form.html'


class UserRemove(
    CompanyRequiredMixin, DetailView
):
    model = User
    permissions_required = 'auth:delete_user'
    template_name = 'core/user_form.html'

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.all().exclude(pk=self.request.user.pk)

    def post(self, request, *args, **kwargs):
        obj = self.get_object()
        company = self.request.user.profile.company

        obj.profile.company_remove(company, request.user)

        messages.success(
            request,
            _(
                "%(object)s has been removed "
                "from your company %(company)s."
            ) % dict(
                object=obj,
                company=company
            )
        )
        return redirect(reverse_lazy('core:user_list'))

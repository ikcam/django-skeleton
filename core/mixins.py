from django.contrib import messages
from django.conf import settings
from django.db import models
from django.core.exceptions import ImproperlyConfigured, PermissionDenied
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from django.utils.translation import ugettext_lazy as _


class AuditableMixin(models.Model):
    date_creation = models.DateTimeField(
        auto_now_add=True, verbose_name=_("Creation date")
    )
    date_modification = models.DateTimeField(
        auto_now=True, verbose_name=_("Modification date")
    )
    is_active = models.BooleanField(
        default=True, editable=False, verbose_name=_("Active")
    )

    class Meta:
        abstract = True

    def activate(self):
        if self.is_active:
            raise Exception(_("Instance is active."))

        self.is_active = True
        self.save()

    def deactivate(self):
        if not self.is_active:
            raise Exception(_("Instance is inactive."))

        self.is_active = False
        self.save()


class CompanyRequiredMixin:
    allow_staff = True
    company = None
    company_field = 'company'
    permissions_required = None
    raise_exception = True

    def handle_no_permission(self, msg=None):
        if self.raise_exception:
            raise PermissionDenied(msg)

        redirect_url = settings.LOGIN_URL + '?next=' + self.request.path

        return HttpResponseRedirect(redirect_url)

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        elif not self.request.user.profile.company:
            return self.handle_no_permission()

        self.company = self.request.user.profile.company

        if not self.company.is_active:
            return HttpResponseRedirect(reverse_lazy('core:company_activate'))

        if (
            self.company.last_invoice and
            not self.company.last_invoice.is_payed
        ):
            messages.warning(
                request,
                _(
                    'You have a pending invoice, please go to '
                    '"Company" > "Invoices" and pay your last invoice.'
                )
            )

        permissions_required = self.get_permissions_required()

        if permissions_required and isinstance(permissions_required, tuple):
            if not request.user.has_company_perms(permissions_required):
                return self.handle_no_permission()
        elif permissions_required:
            if not request.user.has_company_perm(permissions_required):
                return self.handle_no_permission()

        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['company'] = self.company

        return context

    def get_company_field(self):
        return self.company_field

    def get_permissions_required(self):
        return self.permissions_required


class CompanyQuerySetMixin(CompanyRequiredMixin):
    raise_exception = True
    related_properties = None
    prefetch_properties = None

    def get_prefetch_properties(self):
        return self.related_properties

    def get_related_properties(self):
        return self.related_properties

    def get_queryset(self):
        if not self.company:
            raise Exception(_("Company must be set."))

        qs = super().get_queryset()
        qs = qs.filter(**{
            self.get_company_field(): self.company
        })

        related_properties = self.get_related_properties()
        if related_properties:
            if not isinstance(related_properties, tuple):
                raise Exception("`related_properties` must be a tuple")
            qs = qs.select_related(*related_properties)

        prefetch_properties = self.get_prefetch_properties()
        if prefetch_properties:
            if not isinstance(prefetch_properties, tuple):
                raise Exception("`prefetch_properties` must be a tuple")
            qs = qs.prefetch_related(*prefetch_properties)

        return qs


class CompanyCreateMixin(CompanyRequiredMixin):
    def form_valid(self, form):
        if not self.company:
            raise Exception(_("Company must be set."))

        setattr(form.instance, 'company', self.company)
        return super().form_valid(form)


class FillFromRequest:
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        values = self.request.GET.dict()

        for value in values:
            if value in context['form'].fields.keys():
                context['form'].fields[value].initial = values[value]

        return context


class FilterMixin(CompanyQuerySetMixin):
    filter_class = None

    def get_filter_class(self):
        return self.filter_class

    def get_filter(self):
        if self.get_filter_class():
            qs = super().get_queryset()
            qs = self.get_filter_class()(self.request.GET, qs)

            return qs

    def get_queryset(self):
        if self.get_filter_class():
            return self.get_filter().qs
        return super().get_queryset()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = self.get_filter().form

        return context


class ModelActionMixin(CompanyQuerySetMixin):
    model_action = None
    failure_message = _("An error has ocurred, try again later.")
    require_confirmation = False
    success_message = _("Action was performed successfully.")
    success_url = None
    task_module = None
    template_name_suffix = '_action'

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()

        if self.get_require_confirmation():
            return super().get(request, *args, **kwargs)

        response = self.run_action()

        return HttpResponseRedirect(self.get_success_url(response))

    def get_action_kwargs(self):
        return None

    def get_model_action(self):
        if not self.model_action:
            raise ImproperlyConfigured("model_action is required.")
        return self.model_action

    def get_require_confirmation(self):
        return self.require_confirmation

    def get_failure_message(self):
        return self.failure_message % dict(
            object=self.object,
        )

    def get_success_message(self):
        return self.success_message % dict(
            object=self.object,
        )

    def get_success_url(self, response=None):
        if response is False:
            messages.error(
                self.request,
                self.get_failure_message()
            )
        else:
            messages.success(
                self.request,
                self.get_success_message()
            )

        if self.success_url:
            return self.success_url

        return self.object.get_absolute_url()

    def get_task_module(self):
        return self.task_module

    def post(self, request, *args, **kwargs):
        response = self.run_action()

        return HttpResponseRedirect(self.get_success_url(response))

    def run_action(self):
        model_action = self.get_model_action()

        if not hasattr(self.object, model_action):
            raise ImproperlyConfigured(
                "Instance has no action %(action)s." % dict(
                    action=model_action,
                )
            )

        action = getattr(self.object, model_action)

        if not callable(action):
            raise ImproperlyConfigured("Is %(action)s callable?") % dict(
                action=model_action
            )

        task_module = self.get_task_module()
        kwargs = self.get_action_kwargs()

        if settings.DEBUG or not task_module:
            return action(**kwargs)
        else:
            task_name = '{}_task'.format(self.model.__name__.lower())
            task = getattr(task_module, task_name)
            return task.delay(self.object.pk, model_action, kwargs)


class UserQuerySetMixin(CompanyQuerySetMixin):
    user_field = 'user'

    def get_queryset(self):
        qs = super().get_queryset()

        return qs.filter(**{
            self.get_user_field(): self.request.user
        })

    def get_user_field(self):
        return self.user_field

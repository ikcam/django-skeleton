from django.contrib import messages
from django.conf import settings
from django.db import models
from django.core.exceptions import ImproperlyConfigured, PermissionDenied
from django.http import HttpResponseRedirect
from django.shortcuts import redirect
from django.utils.translation import ugettext_lazy as _
from django.views.generic.edit import FormMixin


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
    company = None
    company_field = 'company'
    permission_required = None
    raise_exception = True

    def dispatch(self, request, *args, **kwargs):
        user = request.user

        if not user.is_authenticated:
            return self.handle_no_permission()
        elif not user.company:
            return self.handle_no_permission()

        if not user.company_profile.is_active:
            user.company = None
            user.save()
            return redirect('core:company_choose')

        self.company = user.company

        if not self.company:
            return redirect('core:company_choose')
        elif not self.company.is_active:
            return redirect('core:company_activate')

        permission_required = self.get_permission_required()

        if permission_required and isinstance(permission_required, tuple):
            if not user.has_company_perms(permission_required):
                return self.handle_no_permission()
        elif permission_required:
            if not user.has_company_perm(permission_required):
                return self.handle_no_permission()

        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        kwargs['company'] = self.company
        kwargs['companies_available'] = (
            self.request.user.companies_available()
        )
        kwargs['notifications_unread'] = (
            self.request.user.notifications_unread()
        )

        return super().get_context_data(**kwargs)

    def get_company_field(self):
        return self.company_field

    def get_permission_required(self):
        return self.permission_required

    def handle_no_permission(self, msg=None):
        if self.raise_exception:
            raise PermissionDenied(msg)

        redirect_url = settings.LOGIN_URL + '?next=' + self.request.path

        return HttpResponseRedirect(redirect_url)


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

        if (
            hasattr(form, 'valid_for_company') and
            not form.valid_for_company(self.company)
        ):
            return self.form_invalid(form)

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
        if 'form' not in kwargs:
            kwargs['form'] = self.get_filter().form
        return super().get_context_data(**kwargs)


class ModelActionMixin(CompanyQuerySetMixin, FormMixin):
    form_class = None
    model_action = None
    failure_message = _("An error has ocurred, try again later.")
    require_confirmation = False
    success_message = _("Action was performed successfully.")
    success_url = None
    task_module = None
    template_name_suffix = '_action'

    def get(self, request, *args, **kwargs):
        try:
            self.object = self.get_object()
        except AttributeError:
            self.object = None

        if self.get_form_class() or self.get_require_confirmation():
            return super().get(request, *args, **kwargs)

        response = self.run_action()

        return HttpResponseRedirect(self.get_success_url(response))

    def get_action_kwargs(self, **kwargs):
        data = {}
        if 'form' in kwargs and hasattr(kwargs['form'], 'cleaned_data'):
            data.update(kwargs['form'].cleaned_data)
        return data

    def get_failure_message(self):
        return self.failure_message % dict(
            object=self.object,
        )

    def get_form(self, form_class=None):
        if form_class is None:
            form_class = self.get_form_class()

        if form_class:
            return form_class(**self.get_form_kwargs())

    def get_model_action(self):
        if not self.model_action:
            raise ImproperlyConfigured("model_action is required.")
        return self.model_action

    def get_require_confirmation(self):
        return self.require_confirmation

    def get_success_message(self):
        return self.success_message % dict(
            object=self.object,
        )

    def get_success_url(self, response=None):
        try:
            level, content = response
            getattr(messages, level)(self.request, content)
        except Exception:
            if settings.DEBUG:
                raise

        if self.success_url:
            return self.success_url

        return self.object.get_absolute_url()

    def get_task_module(self):
        return self.task_module

    def post(self, request, *args, **kwargs):
        try:
            self.object = self.get_object()
        except AttributeError:
            self.object = None

        form = self.get_form()

        if form and not form.is_valid():
            return self.form_invalid(form)

        response = self.run_action(form=form)

        return HttpResponseRedirect(self.get_success_url(response))

    def run_action(self, form=None):
        model_action = self.get_model_action()

        if self.object:
            if not hasattr(self.object, model_action):
                raise ImproperlyConfigured(
                    "Instance has no action %(action)s." % dict(
                        action=model_action,
                    )
                )
        else:
            if not hasattr(self.model, model_action):
                raise ImproperlyConfigured(
                    "Model has no action %(action)s." % dict(
                        action=model_action,
                    )
                )

        kwargs = self.get_action_kwargs(form=form)
        task_module = self.get_task_module()

        if not task_module:
            if self.object:
                task = getattr(self.object, model_action)
            else:
                task = getattr(self.model, model_action)
            return task(**kwargs)

        task_name = '{}_task'.format(self.model.__name__.lower())
        task = getattr(task_module, task_name)

        if not settings.DEBUG:
            print('\n\n\n\nAFJAIPOFJAOPSFJPSA')
            task = getattr(task, 'delay')

        if self.object:
            if kwargs:
                return task(
                    company_id=self.company.id,
                    user_id=self.request.user.id,
                    task=model_action,
                    pk=self.object.pk,
                    data=kwargs,
                )
            else:
                return task(
                    company_id=self.company.id,
                    user_id=self.request.user.id,
                    task=model_action,
                    pk=self.object.pk,
                )
        else:
            if kwargs:
                return task(
                    company_id=self.company.id,
                    user_id=self.request.user.id,
                    task=model_action,
                    data=kwargs,
                )
            else:
                return task(
                    company_id=self.company.id,
                    user_id=self.request.user.id,
                    task=model_action,
                )


class UserQuerySetMixin(CompanyQuerySetMixin):
    user_field = 'user'

    def get_queryset(self):
        qs = super().get_queryset()

        return qs.filter(**{
            self.get_user_field(): self.request.user
        })

    def get_user_field(self):
        return self.user_field

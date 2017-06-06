from django.conf import settings
from django.db import models
from django.core.exceptions import PermissionDenied
from django.http import HttpResponseRedirect
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
    company = None
    company_field = 'company'
    raise_exception = False

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

        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['company'] = self.company

        return context

    def get_company_field(self):
        return self.company_field


class CompanyQuerySetMixin(CompanyRequiredMixin):
    raise_exception = True

    def get_queryset(self):
        if not self.company:
            raise Exception(_("Company must be set."))

        qs = super().get_queryset()
        return qs.filter(**{
            self.get_company_field(): self.company
        })


class CompanyCreateMixin(CompanyRequiredMixin):
    def form_valid(self, form):
        if not self.company:
            raise Exception(_("Company must be set."))

        setattr(form.instance, 'company', self.company)
        return super().form_valid(form)

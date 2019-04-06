from django.contrib.auth.views import (
    LoginView, LogoutView, PasswordResetView, PasswordResetDoneView,
    PasswordResetConfirmView, PasswordResetCompleteView, PasswordChangeView,
    PasswordChangeDoneView
)
from django.urls import reverse_lazy
from django.utils.translation import ugettext_lazy as _
from django.views.generic import DetailView, UpdateView

from boilerplate.mixins import UpdateMessageMixin

from core.models import User
from core.views.mixins import CompanyRequiredMixin
from panel import forms


class AccountDetailView(CompanyRequiredMixin, DetailView):
    model = User
    template_name = 'panel/account/account_detail.html'

    def get_object(self):
        return self.request.user


class AccountLoginView(LoginView):
    redirect_authenticated_user = True
    success_url = reverse_lazy('panel:index')
    template_name = 'panel/account/account_login.html'

    def get_success_url(self):
        url = self.get_redirect_url()
        return url or self.success_url


class AccountLogoutView(LogoutView):
    next_page = reverse_lazy('panel:account_login')
    template_name = 'panel/account/account_logout.html'


class AccountPasswordResetView(PasswordResetView):
    email_template_name = 'panel/account/account_password_reset_email.txt'
    html_email_template_name = (
        'panel/account/account_password_reset_email.html'
    )
    subject_template_name = 'panel/account/account_password_reset_subject.txt'
    success_url = reverse_lazy('panel:account_password_reset_done')
    template_name = 'panel/account/account_password_reset_form.html'


class AccountPasswordResetDoneView(PasswordResetDoneView):
    template_name = 'panel/account/account_password_reset_done.html'


class AccountPasswordResetConfirmView(PasswordResetConfirmView):
    post_reset_login = True
    success_url = reverse_lazy('panel:account_password_reset_complete')
    template_name = 'panel/account/account_password_reset_confirm.html'


class AccountPasswordResetCompleteView(PasswordResetCompleteView):
    template_name = 'panel/account/account_password_reset_complete.html'


class AccountPasswordChangeView(PasswordChangeView):
    success_url = reverse_lazy('panel:account_password_change_done')
    template_name = 'panel/account/account_password_change_form.html'


class AccountPasswordChangeDoneView(PasswordChangeDoneView):
    template_name = 'panel/account/account_password_change_done.html'


class AccountUpdateView(UpdateMessageMixin, UpdateView):
    success_message = _("Your account has been update successfully.")
    form_class = forms.AccountChangeForm
    model = User
    success_url = reverse_lazy('panel:account_detail')
    template_name = 'panel/account/account_form.html'

    def get_object(self):
        return self.request.user

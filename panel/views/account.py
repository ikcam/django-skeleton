from django.contrib.auth.views import (
    LoginView, LogoutView, PasswordResetView, PasswordResetDoneView,
    PasswordResetConfirmView, PasswordResetCompleteView, PasswordChangeView,
    PasswordChangeDoneView
)
from django.core.exceptions import PermissionDenied, ValidationError
from django.http import HttpResponseForbidden, HttpResponseRedirect
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from django.views.decorators.debug import sensitive_post_parameters
from django.utils.http import urlsafe_base64_decode
from django.utils.translation import ugettext_lazy as _
from django.views.generic import CreateView, DetailView, UpdateView


from boilerplate.mixins import UpdateMessageMixin

from core.models import Invite, User
from core.tokens import default_token_generator
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


INTERNAL_INVITE_URL_TOKEN = 'from-invite'
INTERNAL_INVITE_SESSION_TOKEN = '_invite_use_token'


class AccountSignupInviteView(CreateView):
    form_class = forms.AccountSignupInviteForm
    model = User
    template_name = 'panel/account/account_signup.html'
    token_generator = default_token_generator
    success_url = reverse_lazy('panel:account_login')

    @method_decorator(sensitive_post_parameters())
    @method_decorator(never_cache)
    def dispatch(self, *args, **kwargs):
        assert 'uidb64' in kwargs and 'token' in kwargs

        self.validlink = False
        self.invite = self.get_invite(kwargs['uidb64'])

        if self.invite is not None:
            token = kwargs['token']
            if token == INTERNAL_INVITE_URL_TOKEN:
                session_token = self.request.session.get(
                    INTERNAL_INVITE_SESSION_TOKEN)
                if self.token_generator.check_token(
                    self.invite, session_token
                ):
                    # If the token is valid, display the password reset form.
                    self.validlink = True
                    return super().dispatch(*args, **kwargs)
            else:
                if self.token_generator.check_token(self.invite, token):
                    # Store the token in the session and redirect to the
                    # password reset form at a URL without the token. That
                    # avoids the possibility of leaking the token in the
                    # HTTP Referer header.
                    self.request.session[INTERNAL_INVITE_SESSION_TOKEN] = token
                    redirect_url = self.request.path.replace(
                        token, INTERNAL_INVITE_URL_TOKEN)
                    return HttpResponseRedirect(redirect_url)

        # Display the "Invalid invitation link" page.
        raise PermissionDenied

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['invite'] = self.invite
        return kwargs

    def get_invite(self, uidb64):
        try:
            # urlsafe_base64_decode() decodes to bytestring
            uid = urlsafe_base64_decode(uidb64).decode()
            invite = Invite._default_manager.get(
                is_active=True, pk=uid, user=None
            )
        except (
            TypeError, ValueError, OverflowError, Invite.DoesNotExist,
            ValidationError
        ):
            invite = None
        return invite

import logging

from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.models import User
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ObjectDoesNotExist, PermissionDenied
from django.http import Http404
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from django.views.generic import DetailView
from django.views.generic.edit import CreateView, UpdateView

from boilerplate.mixins import (
    CreateMessageMixin, NoLoginRequiredMixin, UpdateMessageMixin
)

from core.models import Invite
from . import forms
from .models import Profile


logger = logging.getLogger(__name__)


class Activate(NoLoginRequiredMixin, DetailView):
    def get_token(self):
        if 'token' in self.kwargs:
            return self.kwargs['token']
        raise Http404

    def get_object(self):
        token = self.get_token()

        try:
            return Profile.objects.get(
                activation_key=token,
                user__is_active=False,
            )
        except ObjectDoesNotExist:
            raise Http404

    def get(self, request, *args, **kwargs):
        obj = self.get_object()

        if timezone.now() > obj.date_key_expiration:
            obj.key_generate()

            messages.error(
                request,
                _(
                    "Your activation key has expired. "
                    "A new token has been generated and sended to your email."
                )
            )
        else:
            response = obj.key_deactivate()

            if response:
                messages.success(
                    request,
                    _("Your account is activated now. You can login now.")
                )
            else:
                messages.error(
                    request,
                    _("An error has ocurred.")
                )

        return redirect(reverse_lazy('account:login'))


class ProfileDetail(LoginRequiredMixin, DetailView):
    model = User
    template_name = 'account/profile_detail.html'

    def get_object(self):
        return self.request.user


class ProfileUpdate(LoginRequiredMixin, UpdateMessageMixin, UpdateView):
    form_class = forms.UserUpdateForm
    model = User
    success_message = _("Your profile has been updated successfully.")
    success_url = reverse_lazy("account:profile_detail")
    template_name = 'account/profile_form.html'

    def get_object(self):
        return self.request.user


class SignUp(NoLoginRequiredMixin, CreateMessageMixin, CreateView):
    form_class = forms.SignUpForm
    model = User
    success_url = reverse_lazy('account:login')
    success_message = _(
        'Please check your email and activate your account. '
        'Then you will be able to login.'
    )
    template_name = 'registration/signup.html'


class SignUpInvite(
    CreateMessageMixin, CreateView
):
    form_class = forms.SignUpInviteForm
    model = User
    success_url = reverse_lazy('account:login')
    success_message = _(
        'Please check your email and activate your account. '
        'Then you will be able to login.'
    )
    template_name = 'registration/signup.html'

    def dispatch(self, request, *args, **kwargs):
        invite = self.get_invite()
        company = self.get_company()

        if (
            request.user.is_authenticated and
            request.user.email == invite.email
        ):
            request.user.profile.company = company
            request.user.profile.companies.add(company)
            request.user.profile.save()

            invite.is_active = False
            invite.user = request.user
            invite.save()

            messages.success(
                request,
                _("%s has been added to your company list.") % company
            )
            return redirect(reverse_lazy('core:index'))
        elif request.user.is_authenticated:
            logout(request)

        return super().dispatch(request, *args, **kwargs)

    def get_invite(self):
        queryset = Invite.objects.filter(
            is_active=True,
            user__isnull=True,
        )
        try:
            return queryset.get(
                pk=self.kwargs['pk'],
                activation_key=self.kwargs['token']
            )
        except Exception as e:
            logger.info(e)
            raise PermissionDenied

    def get_company(self):
        invite = self.get_invite()
        return invite.company

    def form_valid(self, form):
        invite = self.get_invite()
        setattr(form.instance, 'email', invite.email)
        setattr(form.instance, 'is_active', True)
        response = super().form_valid(form)

        self.object.profile.company = self.get_company()
        self.object.profile.companies.add(self.get_company())
        self.object.profile.save()

        invite.is_active = False
        invite.user = self.object
        invite.save()

        return response

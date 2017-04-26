from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ObjectDoesNotExist
from django.http import Http404
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from django.views.generic import DetailView
from django.views.generic.edit import CreateView, UpdateView

from boilerplate.mixins import NoLoginRequiredMixin, UpdateMessageMixin

from . import forms
from .models import Profile


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
    template_name = 'account/profile_form.html'

    def get_object(self):
        return self.request.user


class SignUp(NoLoginRequiredMixin, CreateView):
    form_class = forms.SignUpForm
    model = User
    success_url = reverse_lazy('account:login')
    template_name = 'registration/signup.html'

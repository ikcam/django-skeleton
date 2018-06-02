import logging

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import get_user_model, login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ObjectDoesNotExist, PermissionDenied
from django.http import Http404, HttpResponse
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.utils.translation import ugettext_lazy as _
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import DetailView, ListView, RedirectView, View
from django.views.generic.edit import CreateView, UpdateView

from boilerplate.mixins import (
    CreateMessageMixin, ExtraFormsAndFormsetsMixin, NoLoginRequiredMixin,
    UpdateMessageMixin
)
from facebook import auth_url, GraphAPI, parse_signed_request

from core.mixins import CompanyQuerySetMixin
from core.models import Invite
from . import forms
from .models import Notification

UserModel = get_user_model()


class Activate(NoLoginRequiredMixin, DetailView):
    def get_token(self):
        if 'token' in self.kwargs:
            return self.kwargs['token']
        raise Http404

    def get_object(self):
        token = self.get_token()

        try:
            return UserModel.objects.get(
                activation_key=token,
                is_active=False,
            )
        except UserModel.DoesNotExist:
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

        return redirect('account:login')


class LoginFacebookView(View):
    success_url = reverse_lazy('core:dashboard')

    def get(self, request, *args, **kwargs):
        code = request.GET.get('code', None)

        if not code:
            url = auth_url(
                app_id=settings.FB_APP_ID,
                canvas_url='{}{}'.format(
                    settings.SITE_URL,
                    reverse_lazy('account:login_facebook'),
                ),
                perms=[
                    'public_profile',
                    'email',
                ]
            )
            return redirect(url)

        graph = GraphAPI()
        result = graph.get_access_token_from_code(
            code=code,
            redirect_uri='{}{}'.format(
                settings.SITE_URL,
                reverse_lazy('account:login_facebook'),
            ),
            app_id=settings.FB_APP_ID,
            app_secret=settings.FB_APP_SECRET
        )
        access_token = result['access_token']
        graph = GraphAPI(access_token)
        fb_user = graph.get_object(
            'me', fields='id, email, first_name, last_name'
        )

        if request.user.is_authenticated:
            user = request.user

            # Check if another user with that ID exists
            if (
                UserModel.objects
                    .exclude(pk=user.pk)
                    .filter(facebook_id=fb_user.get('id'))
                    .exists()
            ):
                messages.error(
                    request,
                    _(
                        "Another user is registered with that "
                        "Facebook account already."
                    )
                )
                return redirect('account:user_detail')
            elif (
                user.facebook_id and
                user.facebook_id == fb_user.get('id')
            ):
                login(request, user)
                return redirect(self.success_url)
            else:
                user.facebook_id = fb_user.get('id')
                user.facebook_access_token = access_token
                user.save(
                    update_fields=['facebook_id', 'facebook_access_token']
                )
        else:
            # Get or create the user
            try:
                user = UserModel.objects.get(
                    facebook_id=fb_user.get('id')
                )
            except ObjectDoesNotExist:
                user = UserModel.objects.create(
                    first_name=fb_user.get('first_name'),
                    last_name=fb_user.get('last_name'),
                    email=fb_user.get('email'),
                    password='temp',
                    username=fb_user.get('id'),
                )
                password = UserModel.objects.make_random_password()
                user.facebook_id = fb_user.get('id')
                user.access_token = access_token
                user.set_password(password)
                user.save()

            login(request, user)
        return redirect(self.success_url)


@method_decorator(csrf_exempt, name='dispatch')
class LogoutFacebookView(View):
    def dispatch(self, request, *args, **kwargs):
        signed_request = request.POST.get('signed_request')

        data = parse_signed_request(
            signed_request, settings.FB_APP_SECRET
        )

        try:
            user = UserModel.objects.get(facebook_id=data['user_id'])
        except UserModel.DoesNotExist:
            raise PermissionDenied

        user.facebook_id = None
        user.facebook_access_token = None
        user.save()

        return HttpResponse('', content_type='text/plain')


class NotificationDetail(CompanyQuerySetMixin, DetailView):
    model = Notification

    def get(self, request, *args, **kwargs):
        obj = self.get_object()
        obj.set_read()
        return redirect(obj.destination)


class NotificationReadAll(CompanyQuerySetMixin, ListView):
    model = Notification
    success_url = reverse_lazy('account:user_detail')

    def get(self, request, *args, **kwargs):
        qs = self.get_queryset()
        qs.filter(date_read__isnull=True).update(date_read=timezone.now())

        next_ = request.GET.get('next')
        if next_:
            return redirect(next_)
        else:
            return redirect(self.success_url)


class UserDetail(LoginRequiredMixin, DetailView):
    model = UserModel
    template_name = 'account/user_detail.html'

    def get_object(self):
        return self.request.user


class UserPassword(LoginRequiredMixin, RedirectView):
    permanent = False
    pattern_name = 'account:password_change'


class UserUpdate(
    ExtraFormsAndFormsetsMixin, LoginRequiredMixin, UpdateMessageMixin,
    UpdateView
):
    form_class = forms.UserUpdateForm
    model = UserModel
    success_message = _("Your profile has been updated successfully.")
    success_url = reverse_lazy("account:user_detail")
    template_name = 'account/user_form.html'

    def get_object(self):
        return self.request.user


class SignUp(NoLoginRequiredMixin, CreateMessageMixin, CreateView):
    form_class = forms.SignUpForm
    model = UserModel
    success_url = reverse_lazy('account:login')
    success_message = _(
        'Please check your email and activate your account. '
        'Then you will be able to login.'
    )
    template_name = 'registration/signup.html'

    def form_valid(self, form):
        form.instance.first_name = form.cleaned_data.get('first_name')
        form.instance.last_name = form.cleaned_data.get('last_name')
        form.instance.email = form.cleaned_data.get('email')
        return super().form_valid(form)


class SignUpInvite(
    CreateMessageMixin, CreateView
):
    form_class = forms.SignUpInviteForm
    model = UserModel
    success_url = reverse_lazy('account:login')
    success_message = _(
        'Please check your email and activate your account. '
        'Then you will be able to login.'
    )
    template_name = 'registration/signup.html'

    def dispatch(self, request, *args, **kwargs):
        invite = self.get_invite()
        company = self.get_company()
        user = request.user

        if (
            user.is_authenticated and
            user.email == invite.email
        ):
            user.company = company
            user.save(update_fields=['company'])
            user.companies.create(
                company=company
            )

            invite.is_active = False
            invite.user = user
            invite.save(update_fields=['is_active', 'user'])

            messages.success(
                request,
                _("%s has been added to your company list.") % company
            )
            return redirect(reverse_lazy('core:index'))
        elif request.user.is_authenticated:
            logout(request)

        return super().dispatch(request, *args, **kwargs)

    def get_invite(self):
        logger = logging.getLogger(__name__)

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

        form.instance.first_name = form.cleaned_data.get('first_name')
        form.instance.last_name = form.cleaned_data.get('last_name')

        setattr(form.instance, 'email', invite.email)
        setattr(form.instance, 'is_active', True)
        response = super().form_valid(form)

        company = self.get_company()

        self.object.company = company
        self.object.language = company.language
        self.object.save(update_fields=['company', 'language'])
        self.object.companies.create(
            company=company
        )

        invite.is_active = False
        invite.user = self.object
        invite.save(update_fields=['is_active', 'user'])

        return response

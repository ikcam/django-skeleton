from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.http import HttpResponse
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.utils.translation import ugettext_lazy as _
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import (
    CreateView, DetailView, RedirectView, UpdateView, View
)

from boilerplate.mixins import (
    CreateMessageMixin, NoLoginRequiredMixin, UpdateMessageMixin
)
from facebook import auth_url, GraphAPI, parse_signed_request

from core.models import Invite, User
from public import forms


class AccountActivateView(NoLoginRequiredMixin, DetailView):
    model = User
    slug_field = 'activation_key'
    slug_url_kwarg = 'token'

    def get_queryset(self):
        return super().get_queryset().filter(is_active=False)

    def get(self, request, *args, **kwargs):
        super().get(request, *args, **kwargs)

        if not self.object.can_activate():
            self.object.key_generate()

            messages.error(
                request,
                _(
                    "Your activation key has expired. "
                    "A new token has been generated and sended to your email."
                )
            )
        else:
            if self.object.key_deactivate():
                messages.success(
                    request,
                    _("Your account is activated now. You can login now.")
                )
            else:
                messages.error(
                    request,
                    _("An error has ocurred.")
                )

        return redirect('public:account_login')


class AccountDetailView(LoginRequiredMixin, DetailView):
    model = User
    template_name = 'public/account_detail.html'

    def get_object(self):
        return self.request.user


class AccountLoginFacebookView(View):
    success_url = reverse_lazy('public:dashboard')

    def get(self, request, *args, **kwargs):
        code = request.GET.get('code', None)

        if not code:
            url = auth_url(
                app_id=settings.FB_APP_ID,
                canvas_url='{}{}'.format(
                    settings.SITE_URL,
                    reverse_lazy('public:login_facebook'),
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
                reverse_lazy('public:login_facebook'),
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
                User.objects
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
                return redirect('public:user_detail')
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
                user = User.objects.get(
                    facebook_id=fb_user.get('id')
                )
            except User.DoesNotExist:
                user = User.objects.create(
                    first_name=fb_user.get('first_name'),
                    last_name=fb_user.get('last_name'),
                    email=fb_user.get('email'),
                    password='temp',
                    username=fb_user.get('id'),
                )
                password = User.objects.make_random_password()
                user.facebook_id = fb_user.get('id')
                user.access_token = access_token
                user.set_password(password)
                user.save()

            login(request, user)
        return redirect(self.success_url)


@method_decorator(csrf_exempt, name='dispatch')
class AccountLogoutFacebookView(View):
    def dispatch(self, request, *args, **kwargs):
        signed_request = request.POST.get('signed_request')

        data = parse_signed_request(
            signed_request, settings.FB_APP_SECRET
        )

        try:
            user = User.objects.get(facebook_id=data['user_id'])
        except User.DoesNotExist:
            raise PermissionDenied

        user.facebook_id = None
        user.facebook_access_token = None
        user.save(update_fields=['facebook_id', 'facebook_access_token'])

        return HttpResponse('', content_type='text/plain')


class AccountPasswordView(LoginRequiredMixin, RedirectView):
    permanent = False
    pattern_name = 'public:account_password_change'


class AccountSignUpView(NoLoginRequiredMixin, CreateMessageMixin, CreateView):
    form_class = forms.SignUpForm
    model = User
    success_url = reverse_lazy('public:login')
    success_message = _(
        'Please check your email and activate your account. '
        'Then you will be able to login.'
    )
    template_name = 'public/signup.html'

    def form_valid(self, form):
        form.instance.first_name = form.cleaned_data.get('first_name')
        form.instance.last_name = form.cleaned_data.get('last_name')
        form.instance.email = form.cleaned_data.get('email')
        form.instance.is_active = False
        return super().form_valid(form)


class AccountSignUpInviteView(
    CreateMessageMixin, CreateView
):
    form_class = forms.SignUpInviteForm
    model = User
    success_url = reverse_lazy('public:account_login')
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

            invite.is_active = False
            invite.user = user
            invite.save(update_fields=['is_active', 'user'])

            messages.success(
                request,
                _("%s has been added to your company list.") % company
            )
            return redirect('public:index')
        elif request.user.is_authenticated:
            messages.error(
                request,
                _("Your other session was closed to use this invitation.")
            )
            logout(request)

        return super().dispatch(request, *args, **kwargs)

    def get_invite(self):
        try:
            return Invite.objects.get(
                activation_key=self.kwargs['token'],
                is_active=True,
                pk=self.kwargs['pk'],
                user__isnull=True,
            )
        except Exception as e:
            raise PermissionDenied

    def get_company(self):
        invite = self.get_invite()
        return invite.company

    def form_valid(self, form):
        invite = self.get_invite()
        company = self.get_company()

        form.instance.first_name = form.cleaned_data.get('first_name')
        form.instance.last_name = form.cleaned_data.get('last_name')
        setattr(form.instance, 'email', invite.email)
        setattr(form.instance, 'is_active', True)
        setattr(form.instance, 'company', company)
        setattr(form.instance, 'language', company.language)

        response = super().form_valid(form)

        self.object.roles = invite.roles
        self.object.save()

        invite.is_active = False
        invite.user = self.object
        invite.save(update_fields=['is_active', 'user'])

        return response


class AccountUpdateView(
    LoginRequiredMixin, UpdateMessageMixin, UpdateView
):
    form_class = forms.AccountUpdateForm
    model = User
    success_message = _("Your profile has been updated successfully.")
    success_url = reverse_lazy("public:account_detail")
    template_name = 'public/account_form.html'

    def get_object(self):
        return self.request.user

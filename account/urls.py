from django.conf.urls import url
from django.contrib.auth import views as auth_views
from django.utils.translation import ugettext_lazy as _
from django.urls import reverse_lazy

from . import autocomplete, views

urlpatterns = [
    # Autocomplete
    url(
        _(r'^groups/autocomplete/$'),
        autocomplete.GroupAutocomplete.as_view(),
        name='group_autocomplete'
    ),
    url(
        _(r'^permissions/autocomplete/$'),
        autocomplete.PermissionAutocomplete.as_view(),
        name='permission_autocomplete'
    ),
    url(
        _(r'^users/autocomplete/$'),
        autocomplete.UserAutocomplete.as_view(),
        name='user_autocomplete'
    ),
    # Views
    url(
        _(r'^$'),
        views.ProfileDetail.as_view(),
        name='profile_detail'
    ),
    url(
        _(r'^change/$'),
        views.ProfileUpdate.as_view(),
        name='profile_update'
    ),
    url(
        _(r'^activate/(?P<token>[0-9A-Za-z_\-]+)/$'),
        views.Activate.as_view(),
        name='activate'
    ),
    url(
        _(r"^login/$"),
        auth_views.LoginView.as_view(
            template_name='registration/login.html'
        ),
        name="login"
    ),
    url(
        _(r'^logout/$'),
        auth_views.LogoutView.as_view(),
        name='logout'
    ),
    url(
        _(r'^password-change/$'),
        auth_views.PasswordChangeView.as_view(
            template_name='registration/password_change.html',
            success_url=reverse_lazy('account:password_change_done')
        ),
        name='password_change'
    ),
    url(
        _(r'^password-change/done/$'),
        auth_views.PasswordChangeDoneView.as_view(
            template_name='registration/password_done.html'
        ),
        name='password_change_done'
    ),
    url(
        _(r'^password-reset/$'),
        auth_views.PasswordResetView.as_view(
            template_name='registration/reset_form.html',
            email_template_name='registration/password_email.html',
            html_email_template_name='registration/password_email_html.html',
            success_url=reverse_lazy('account:password_reset_done'),
            subject_template_name='registration/password_subject.txt',
        ),
        name='password_reset'
    ),
    url(
        _(r'^password-reset/done/$'),
        auth_views.PasswordResetDoneView.as_view(
            template_name='registration/reset_done.html'
        ),
        name='password_reset_done'
    ),
    url(
        _(
            r'^reset/(?P<uidb64>[0-9A-Za-z_\-]+)/'
            r'(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$'
        ),
        auth_views.PasswordResetConfirmView.as_view(
            template_name='registration/reset_confirm.html',
            success_url=reverse_lazy('account:password_reset_complete')
        ),
        name='password_reset_confirm'
    ),
    url(
        _(r'^reset/done/$'),
        auth_views.PasswordResetCompleteView.as_view(
            template_name='registration/reset_complete.html'
        ),
        name='password_reset_complete'
    ),
    url(
        _(r'^signup/$'), views.SignUp.as_view(), name='signup'
    ),
]

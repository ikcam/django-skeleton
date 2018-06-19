from django.contrib.auth import views as auth_views
from django.urls import path, reverse_lazy
from django.utils.translation import ugettext_lazy as _

from . import autocomplete, views


urlpatterns = [
    path(
        '',
        views.IndexView.as_view(),
        name='index'
    ),
    path(
        'dashboard/',
        views.DashboardView.as_view(),
        name='dashboard'
    ),
    # Account - account - account
    path(
        _('account/activate/<token>/'),
        views.AccountActivateView.as_view(),
        name='activate'
    ),
    path(
        _('account/'),
        views.AccountDetailView.as_view(),
        name='account_detail'
    ),
    path(
        _('account/login/facebook/'),
        views.AccountLoginFacebookView.as_view(),
        name='login_facebook'
    ),
    path(
        _('account/logout/facebook/'),
        views.AccountLogoutFacebookView.as_view(),
        name='logout_facebook'
    ),
    path(
        _('account/password/'),
        views.AccountPasswordView.as_view(),
        name='account_password'
    ),
    path(
        _('account/signup/'),
        views.AccountSignUpView.as_view(
            template_name='registration/signup.html'
        ),
        name='account_signup'
    ),
    path(
        _('account/signup/invite/<int:pk>/<token>/'),
        views.AccountSignUpInviteView.as_view(),
        name='account_signup_invite'
    ),
    path(
        _('account/change/'),
        views.AccountUpdateView.as_view(),
        name='account_change'
    ),
    path(
        _('account/login/'),
        auth_views.LoginView.as_view(
            template_name='registration/login.html'
        ),
        name='account_login'
    ),
    path(
        _('account/logout/'),
        auth_views.LogoutView.as_view(),
        name='account_logout'
    ),
    path(
        _('account/password-change/'),
        auth_views.PasswordChangeView.as_view(
            template_name='registration/password_change.html',
            success_url=reverse_lazy('public:account_password_change_done'),
        ),
        name='account_password_change'
    ),
    path(
        _('account_password-change/done/'),
        auth_views.PasswordChangeDoneView.as_view(
            template_name='registration/password_done.html'
        ),
        name='account_password_change_done'
    ),
    path(
        _('account/password-reset/'),
        auth_views.PasswordResetView.as_view(
            template_name='registration/reset_form.html',
            email_template_name='registration/password_email.html',
            html_email_template_name='registration/password_email_html.html',
            success_url=reverse_lazy('public:account_password_reset_done'),
            subject_template_name='registration/password_subject.txt',
        ),
        name='account_password_reset'
    ),
    path(
        _('account/password-reset/done/'),
        auth_views.PasswordResetDoneView.as_view(
            template_name='registration/reset_done.html'
        ),
        name='account_password_reset_done'
    ),
    path(
        _('account/reset/<uidb64>/<token>/'),
        auth_views.PasswordResetConfirmView.as_view(
            template_name='registration/reset_confirm.html',
            success_url=reverse_lazy('public:account_password_reset_complete'),
        ),
        name='account_password_reset_confirm'
    ),
    path(
        _('account/reset/done/'),
        auth_views.PasswordResetCompleteView.as_view(
            template_name='registration/reset_complete.html'
        ),
        name='account_password_reset_complete'
    ),
    # Company - company - company
    path(
        _('company/activate/'),
        views.CompanyActivateView.as_view(),
        name='company_activate'
    ),
    path(
        _('company/choose/'),
        views.CompanyChooseView.as_view(),
        name='company_choose'
    ),
    path(
        _('company/add/'),
        views.CompanyCreateView.as_view(),
        name='company_add'
    ),
    path(
        _('company/'),
        views.CompanyDetailView.as_view(),
        name='company_detail'
    ),
    path(
        _('company/change/'),
        views.CompanyUpdateView.as_view(),
        name='company_change'
    ),
    path(
        _('company/switch/<int:pk>/'),
        views.CompanySwitchView.as_view(),
        name='company_switch'
    ),
    # Event - events - event
    path(
        _('events/'),
        views.EventListView.as_view(),
        name='event_list'
    ),
    path(
        _('events/add/'),
        views.EventCreateView.as_view(),
        name='event_add'
    ),
    path(
        _('events/<int:pk>/'),
        views.EventDetailView.as_view(),
        name='event_detail'
    ),
    path(
        _('events/<int:pk>/change/'),
        views.EventUpdateView.as_view(),
        name='event_change'
    ),
    path(
        _('events/<int:pk>/delete/'),
        views.EventDeleteView.as_view(),
        name='event_delete'
    ),
    path(
        _('events/<slug>/<int:pk>/'),
        views.EventPublicView.as_view(),
        name='event_public'
    ),
    # Invite - invites - invite
    path(
        _('company/invites/'),
        views.InviteListView.as_view(),
        name='invite_list'
    ),
    path(
        _('company/invites/add/'),
        views.InviteCreateView.as_view(),
        name='invite_add'
    ),
    path(
        _('company/invites/<int:pk>/delete/'),
        views.InviteDeleteView.as_view(),
        name='invite_delete'
    ),
    path(
        _('company/invites/<int:pk>/send/'),
        views.InviteSendView.as_view(),
        name='invite_send'
    ),
    # Invoice - invoices - invoice
    path(
        _('company/invoices/'),
        views.InvoiceListView.as_view(),
        name='invoice_list'
    ),
    path(
        _('company/invoices/<int:pk>/'),
        views.InvoiceDetailView.as_view(),
        name='invoice_detail'
    ),
    # Link - links - link
    path(
        _('links/'),
        views.LinkListView.as_view(),
        name='link_list'
    ),
    path(
        _('links/add/'),
        views.LinkCreateView.as_view(),
        name='link_add'
    ),
    path(
        _('links/<int:pk>/'),
        views.LinkDetailView.as_view(),
        name='link_detail'
    ),
    path(
        _('links/<int:pk>/change/'),
        views.LinkUpdateView.as_view(),
        name='link_change'
    ),
    path(
        _('links/<int:pk>/delete/'),
        views.LinkDeleteView.as_view(),
        name='link_delete'
    ),
    path(
        _('ld/<int:pk>/'),
        views.LinkPublicDirectView.as_view(),
        name='link_public_direct'
    ),
    path(
        _('lt/<token>/'),
        views.LinkPublicTokenView.as_view(),
        name='link_public_token'
    ),
    # Message - messages - message
    path(
        _('messages/'),
        views.MessageListView.as_view(),
        name='message_list'
    ),
    path(
        _('messages/<int:pk>/'),
        views.MessageDetailView.as_view(),
        name='message_detail'
    ),
    path(
        _('messages/<int:pk>/frame/'),
        views.MessageFrameView.as_view(),
        name='message_frame'
    ),
    path(
        _('messages/pixel/<token>/'),
        views.MessagePixelView.as_view(),
        name='message_pixel'
    ),
    # Notification
    path(
        _('notifications/read-all/'),
        views.NotificationReadAllView.as_view(),
        name='notification_readall'
    ),
    path(
        _('notifications/<int:pk>/'),
        views.NotificationDetailView.as_view(),
        name='notification_detail'
    ),
    # Role - roles - role
    path(
        _('company/roles/autocomplete/'),
        autocomplete.RoleAutocomplete.as_view(),
        name='role_autocomplete'
    ),
    path(
        _('company/roles/'),
        views.RoleListView.as_view(),
        name='role_list'
    ),
    path(
        _('company/roles/add/'),
        views.RoleCreateView.as_view(),
        name='role_add'
    ),
    path(
        _('company/roles/<int:pk>/change/'),
        views.RoleUpdateView.as_view(),
        name='role_change'
    ),
    path(
        _('company/roles/<int:pk>/delete/'),
        views.RoleDeleteView.as_view(),
        name='role_delete'
    ),
    # User - users - user
    path(
        _('company/users/'),
        views.UserListView.as_view(),
        name='user_list'
    ),
    path(
        _('company/users/add/'),
        views.UserCreateView.as_view(),
        name='user_add'
    ),
    path(
        _('company/users/<int:pk>/change/'),
        views.UserUpdateView.as_view(),
        name='user_change'
    ),
    path(
        _('company/users/<int:pk>/password/'),
        views.UserPasswordView.as_view(),
        name='user_password'
    ),
    path(
        _('company/users/<int:pk>/permissions/'),
        views.UserPermissionsView.as_view(),
        name='user_permissions'
    ),
    path(
        _('company/users/<int:pk>/remove/'),
        views.UserRemoveView.as_view(),
        name='user_remove'
    ),
    # Autocomplete
    path(
        _('countries/autocomplete/'),
        autocomplete.CountryAutocomplete.as_view(),
        name='country_autocomplete'
    ),
    path(
        _('languages/autocomplete/'),
        autocomplete.LanguageAutocomplete.as_view(),
        name='language_autocomplete'
    ),
    path(
        _('model-autocomplete/'),
        autocomplete.ModelAutocomplete.as_view(),
        name='model_autocomplete'
    ),
    path(
        _('permissions/autocomplete/'),
        autocomplete.PermissionAutocomplete.as_view(),
        name='permission_autocomplete'
    ),
    path(
        _('timezones/autocomplete/'),
        autocomplete.TimezoneAutocomplete.as_view(),
        name='timezone_autocomplete'
    ),
    path(
        _('users/autocomplete/'),
        autocomplete.UserAutocomplete.as_view(),
        name='user_autocomplete'
    ),
    path(
        _('users/other/autocomplete/'),
        autocomplete.UserOtherAutocomplete.as_view(),
        name='user_other_autocomplete'
    ),
]

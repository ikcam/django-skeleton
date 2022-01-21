from django.urls import path
from django.utils.translation import ugettext_lazy as _

from panel import views

urlpatterns = [
]


urlpatterns += [
    path(
        '',
        views.IndexView.as_view(),
        name='index'
    ),
    path(
        _('account/'),
        views.AccountDetailView.as_view(),
        name='account_detail'
    ),
    path(
        _('account/login/'),
        views.AccountLoginView.as_view(),
        name='account_login'
    ),
    path(
        _('account/logout/'),
        views.AccountLogoutView.as_view(),
        name='account_logout'
    ),
    path(
        _('account/password/done/'),
        views.AccountPasswordChangeDoneView.as_view(),
        name='account_password_change_done'
    ),
    path(
        _('account/password/'),
        views.AccountPasswordChangeView.as_view(),
        name='account_password_change'
    ),
    path(
        _('account/password-reset/complete/'),
        views.AccountPasswordResetCompleteView.as_view(),
        name='account_password_reset_complete'
    ),
    path(
        _('account/password-reset/<uidb64>/<token>/'),
        views.AccountPasswordResetConfirmView.as_view(),
        name='account_password_reset_confirm'
    ),
    path(
        _('account/password-reset/done/'),
        views.AccountPasswordResetDoneView.as_view(),
        name='account_password_reset_done'
    ),
    path(
        _('account/password-reset/'),
        views.AccountPasswordResetView.as_view(),
        name='account_password_reset'
    ),
    path(
        _('account/change/'),
        views.AccountUpdateView.as_view(),
        name='account_change'
    ),
    path(
        _('account/signup/<uidb64>/<token>/'),
        views.AccountSignupInviteView.as_view(),
        name='account_signup_invite'
    ),
    # Company
    path(
        _('company/'),
        views.CompanyDetailView.as_view(),
        name='company_detail'
    ),
    path(
        _('company/activate/'),
        views.CompanyActivateView.as_view(),
        name='company_activate'
    ),
    path(
        _('company/change/'),
        views.CompanyUpdateView.as_view(),
        name='company_change'
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
        _('events/<pk>/'),
        views.EventDetailView.as_view(),
        name='event_detail'
    ),
    path(
        _('events/<pk>/change/'),
        views.EventUpdateView.as_view(),
        name='event_change'
    ),
    path(
        _('events/<pk>/delete/'),
        views.EventDeleteView.as_view(),
        name='event_delete'
    ),
    path(
        _('events/<pk>/'),
        views.EventPublicView.as_view(),
        name='event_public'
    ),
    # Invite - invites - invite
    path(
        _('invites/'),
        views.InviteListView.as_view(),
        name='invite_list'
    ),
    path(
        _('invites/add/'),
        views.InviteCreateView.as_view(),
        name='invite_add'
    ),
    path(
        _('invites/<int:pk>/delete/'),
        views.InviteDeleteView.as_view(),
        name='invite_delete'
    ),
    path(
        _('invites/<int:pk>/send/'),
        views.InviteSendView.as_view(),
        name='invite_send'
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
        _('links/<pk>/'),
        views.LinkDetailView.as_view(),
        name='link_detail'
    ),
    path(
        _('links/<pk>/change/'),
        views.LinkUpdateView.as_view(),
        name='link_change'
    ),
    path(
        _('links/<pk>/delete/'),
        views.LinkDeleteView.as_view(),
        name='link_delete'
    ),
    # Message - messages - message
    path(
        _('messages/'),
        views.MessageListView.as_view(),
        name='message_list'
    ),
    path(
        _('messages/<pk>/'),
        views.MessageDetailView.as_view(),
        name='message_detail'
    ),
    path(
        _('messages/<pk>/frame/'),
        views.MessageFrameView.as_view(),
        name='message_frame'
    ),
    # Notification
    path(
        _('notifications/'),
        views.NotificationListView.as_view(),
        name='notification_list'
    ),
    path(
        _('notifications/<pk>/'),
        views.NotificationDetailView.as_view(),
        name='notification_detail'
    ),
    # Role - roles - role
    path(
        _('roles/'),
        views.RoleListView.as_view(),
        name='role_list'
    ),
    path(
        _('roles/add/'),
        views.RoleCreateView.as_view(),
        name='role_add'
    ),
    path(
        _('roles/<int:pk>/change/'),
        views.RoleUpdateView.as_view(),
        name='role_change'
    ),
    path(
        _('roles/<int:pk>/delete/'),
        views.RoleDeleteView.as_view(),
        name='role_delete'
    ),
    # User - users - user
    path(
        _('users/'),
        views.UserListView.as_view(),
        name='user_list'
    ),
    path(
        _('users/add/'),
        views.UserCreateView.as_view(),
        name='user_add'
    ),
    path(
        _('users/<int:pk>/change/'),
        views.UserUpdateView.as_view(),
        name='user_change'
    ),
    path(
        _('users/<int:pk>/delete/'),
        views.UserDeleteView.as_view(),
        name='user_delete'
    ),
    path(
        _('users/<int:pk>/password/'),
        views.UserPasswordView.as_view(),
        name='user_password'
    ),
    path(
        _('users/<int:pk>/permissions/'),
        views.UserPermissionsView.as_view(),
        name='user_permissions'
    ),
]
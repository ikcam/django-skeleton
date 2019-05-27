from panel.views.base import IndexView
from panel.views.account import (
    AccountDetailView,
    AccountLoginView,
    AccountLogoutView,
    AccountPasswordChangeDoneView,
    AccountPasswordChangeView,
    AccountPasswordResetCompleteView,
    AccountPasswordResetConfirmView,
    AccountPasswordResetDoneView,
    AccountPasswordResetView,
    AccountUpdateView,
    AccountSignupInviteView
)
from panel.views.company import (
    CompanyActivateView,
    CompanyDetailView,
    CompanyUpdateView
)
from panel.views.event import (
    EventListView,
    EventDetailView,
    EventCreateView,
    EventUpdateView,
    EventDeleteView,
    EventPublicView
)
from panel.views.invite import (
    InviteCreateView,
    InviteDeleteView,
    InviteListView,
    InviteSendView
)
from panel.views.link import (
    LinkListView,
    LinkDetailView,
    LinkCreateView,
    LinkUpdateView,
    LinkDeleteView,
    LinkPublicView
)
from panel.views.message import (
    MessageDetailView,
    MessageFrameView,
    MessageListView
)
from panel.views.notification import (
    NotificationDetailView,
    NotificationListView,
    NotificationReadAllView
)
from panel.views.role import (
    RoleCreateView,
    RoleDeleteView,
    RoleListView,
    RoleUpdateView
)
from panel.views.user import (
    UserCreateView,
    UserDeleteView,
    UserListView,
    UserPasswordView,
    UserPermissionsView,
    UserUpdateView
)


__all__ = [
    'IndexView',
    'AccountDetailView',
    'AccountLoginView',
    'AccountLogoutView',
    'AccountPasswordChangeDoneView',
    'AccountPasswordChangeView',
    'AccountPasswordResetCompleteView',
    'AccountPasswordResetConfirmView',
    'AccountPasswordResetDoneView',
    'AccountPasswordResetView',
    'AccountUpdateView',
    'AccountSignupInviteView',
    'CompanyActivateView',
    'CompanyDetailView',
    'CompanyUpdateView',
    'EventListView',
    'EventDetailView',
    'EventCreateView',
    'EventUpdateView',
    'EventDeleteView',
    'EventPublicView',
    'InviteCreateView',
    'InviteDeleteView',
    'InviteListView',
    'InviteSendView',
    'LinkListView',
    'LinkDetailView',
    'LinkCreateView',
    'LinkUpdateView',
    'LinkDeleteView',
    'LinkPublicView',
    'MessageDetailView',
    'MessageFrameView',
    'MessageListView',
    'MessagePixelView',
    'NotificationDetailView',
    'NotificationListView',
    'NotificationReadAllView',
    'RoleCreateView',
    'RoleDeleteView',
    'RoleListView',
    'RoleUpdateView',
    'UserCreateView',
    'UserDeleteView',
    'UserListView',
    'UserPasswordView',
    'UserPermissionsView',
    'UserUpdateView'
]

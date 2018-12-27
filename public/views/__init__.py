from public.views.base import IndexView, DashboardView
from public.views.account import (
    AccountActivateView,
    AccountDetailView,
    AccountLoginFacebookView,
    AccountLogoutFacebookView,
    AccountPasswordView,
    AccountSignUpView,
    AccountSignUpInviteView,
    AccountUpdateView
)
from public.views.company import (
    CompanyDetailView,
    CompanyCreateView,
    CompanyUpdateView,
    CompanyActivateView,
    CompanyChooseView,
    CompanySwitchView
)
from public.views.event import (
    EventListView,
    EventDetailView,
    EventCreateView,
    EventUpdateView,
    EventDeleteView,
    EventPublicView
)
from public.views.invoice import (
    InvoiceListView,
    InvoiceDetailView
)
from public.views.link import (
    LinkListView,
    LinkDetailView,
    LinkCreateView,
    LinkUpdateView,
    LinkDeleteView,
    LinkPublicDirectView,
    LinkPublicTokenView
)
from public.views.message import (
    MessageListView,
    MessageDetailView,
    MessageFrameView,
    MessagePixelView
)
from public.views.notification import (
    NotificationDetailView,
    NotificationReadAllView
)
from public.views.invite import (
    InviteListView,
    InviteCreateView,
    InviteDeleteView,
    InviteSendView
)
from public.views.role import (
    RoleListView,
    RoleCreateView,
    RoleUpdateView,
    RoleDeleteView
)
from public.views.user import (
    UserListView,
    UserCreateView,
    UserUpdateView,
    UserPasswordView,
    UserPermissionsView,
    UserRemoveView
)


__all__ = [
    'IndexView',
    'AccountActivateView',
    'AccountDetailView',
    'AccountLoginFacebookView',
    'AccountLogoutFacebookView',
    'AccountPasswordView',
    'AccountSignUpView',
    'AccountSignUpInviteView',
    'CompanyDetailView',
    'CompanyCreateView',
    'CompanyUpdateView',
    'CompanyActivateView',
    'CompanyChooseView',
    'EventListView',
    'EventDetailView',
    'EventCreateView',
    'EventUpdateView',
    'EventDeleteView',
    'InvoiceListView',
    'LinkListView',
    'LinkDetailView',
    'LinkCreateView',
    'LinkUpdateView',
    'LinkDeleteView',
    'LinkPublicDirectView',
    'MessageListView',
    'MessageDetailView',
    'MessageFrameView',
    'NotificationDetailView',
    'InviteListView',
    'InviteCreateView',
    'InviteDeleteView',
    'RoleListView',
    'RoleCreateView',
    'RoleUpdateView',
    'UserListView',
    'UserCreateView',
    'UserUpdateView',
    'UserPasswordView',
    'UserPermissionsView',
]

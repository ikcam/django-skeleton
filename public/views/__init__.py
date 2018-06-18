from .base import IndexView, DashboardView  # NOQA
from .account import (  # NOQA
    AccountActivateView,
    AccountDetailView,
    AccountLoginFacebookView,
    AccountLogoutFacebookView,
    AccountPasswordView,
    AccountSignUpView,
    AccountSignUpInviteView,
    AccountUpdateView
)
from .company import (  # NOQA
    CompanyDetailView,
    CompanyCreateView,
    CompanyUpdateView,
    CompanyActivateView,
    CompanyChooseView,
    CompanySwitchView
)
from .event import (  # NOQA
    EventListView,
    EventDetailView,
    EventCreateView,
    EventUpdateView,
    EventDeleteView,
    EventPublicView
)
from .invoice import (  # NOQA
    InvoiceListView,
    InvoiceDetailView
)
from .link import (  # NOQA
    LinkListView,
    LinkDetailView,
    LinkCreateView,
    LinkUpdateView,
    LinkDeleteView,
    LinkPublicDirectView,
    LinkPublicTokenView
)
from .message import (  # NOQA
    MessageListView,
    MessageDetailView,
    MessageFrameView,
    MessagePixelView
)
from .notification import (  # NOQA
    NotificationDetailView,
    NotificationReadAllView
)
from .invite import (  # NOQA
    InviteListView,
    InviteCreateView,
    InviteDeleteView,
    InviteSendView
)
from .role import (  # NOQA
    RoleListView,
    RoleCreateView,
    RoleUpdateView,
    RoleDeleteView
)
from .user import (  # NOQA
    UserListView,
    UserCreateView,
    UserUpdateView,
    UserPasswordView,
    UserPermissionsView,
    UserRemoveView
)

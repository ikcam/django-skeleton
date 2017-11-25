from rest_framework_nested import routers

from .account import views as account_views
from .common import views as common_views

router = routers.DefaultRouter()

""" Account """
router.register(r'account/me', account_views.MeViewSet)
router.register(r'account/users', account_views.UserViewSet)

""" Common """
router.register(r'common/events', common_views.EventViewSet)
router.register(r'common/links', common_views.LinkViewSet)
link_router = routers.NestedSimpleRouter(
    router, r'common/links', lookup='parent'
)
link_router.register(
    r'visits', common_views.VisitViewSet,
    base_name='link_visit'
)
router.register(r'common/messages', common_views.MessageViewSet)
message_router = routers.NestedSimpleRouter(
    router, r'common/messages', lookup='parent'
)
message_router.register(
    r'links', common_views.LinkViewSet,
    base_name='message_link'
)

nested_routers = (link_router.urls + message_router.urls)

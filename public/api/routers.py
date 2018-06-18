from rest_framework_nested import routers

from . import views


router = routers.DefaultRouter()
router.register(r'events', views.EventViewSet)
router.register(r'links', views.LinkViewSet)
router.register(r'messages', views.MessageViewSet)
router.register(r'notifications', views.NotificationViewSet)


link_router = routers.NestedSimpleRouter(
    router, r'links', lookup='parent'
)
link_router.register(r'visits', views.VisitViewSet, 'link_visit')

message_router = routers.NestedSimpleRouter(
    router, r'messages', lookup='parent'
)
message_router.register(r'links', views.LinkViewSet, 'message_link')

nested_routers = (link_router.urls + message_router.urls)

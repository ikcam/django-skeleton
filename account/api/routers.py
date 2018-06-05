from rest_framework_nested import routers

from . import views


router = routers.DefaultRouter()
router.register(r'notifications', views.NotificationViewSet)

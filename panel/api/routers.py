from rest_framework_nested import routers
from panel.api import views

router = routers.DefaultRouter()
router.register(r'events', views.EventViewSet)

from rest_framework_nested import routers

from .account import views as account_views

router = routers.DefaultRouter()

""" Account """
router.register(r'account/me', account_views.MeViewSet)
router.register(r'account/users', account_views.UserViewSet)


nested_routers = ()

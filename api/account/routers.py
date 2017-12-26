from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework_nested import routers

from . import views


router = routers.DefaultRouter()
router.register(r'login', ObtainAuthToken, 'login')
router.register(r'notifications', views.NotificationViewSet)
router.register(r'profile', views.ProfileViewSet)
router.register(r'signup', views.SignUpView)
router.register(r'password-reset', views.PasswordResetView, 'password_reset')
router.register(
    r'reset/(?P<uidb64>[0-9A-Za-z_\-]+)/'
    r'(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})',
    views.PasswordResetConfirmView,
    'password_reset_confirm'
)

nested_routers = []

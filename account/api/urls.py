from django.urls import path

from rest_framework.authtoken.views import ObtainAuthToken

from .routers import router
from . import views


urlpatterns = [
    path(
        'login/',
        ObtainAuthToken.as_view(),
        name='login'
    ),
    path(
        'password-reset/',
        views.PasswordResetView.as_view(),
        name='password_reset'
    ),
    path(
        'reset/<uidb64>/<token>/',
        views.PasswordResetConfirmView.as_view(),
        name='password_reset_confirm'
    ),
    path(
        'user/',
        views.UserViewSet.as_view({
            'get': 'retrieve',
            'post': 'create',
            'put': 'update',
            'patch': 'update',
        }),
        name='user'
    )
] + router.urls

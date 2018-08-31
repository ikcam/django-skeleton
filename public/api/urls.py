from django.urls import path

from rest_framework.authtoken import views as auth_views

from .routers import nested_routers, router
from . import views


urlpatterns = [
    path(
        'account/',
        views.UserViewSet.as_view({
            'get': 'retrieve',
            'post': 'create',
            'put': 'update',
            'patch': 'update',
        }),
        name='account'
    ),
    path(
        'account/login/',
        auth_views.obtain_auth_token,
        name='account_login'
    )
] + router.urls + nested_routers

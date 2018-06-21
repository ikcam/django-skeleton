from django.urls import path

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
    )
] + router.urls + nested_routers

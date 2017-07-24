from django.conf.urls import url

from rest_framework.authtoken import views

from .account import views as account_views
from .routers import nested_routers, router


urlpatterns = [
    url(r'^auth/', views.obtain_auth_token),
    url(r'^account/password_reset/$', account_views.password_reset),
    url(r'^account/signup/$', account_views.signup),
] + router.urls + nested_routers

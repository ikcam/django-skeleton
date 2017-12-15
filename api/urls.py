from django.urls import path

from rest_framework.authtoken import views

from .account import views as account_views
from .routers import nested_routers, router


urlpatterns = [
    path(
        'account/login/',
        views.obtain_auth_token
    ),
    path(
        'account/signup/',
        account_views.SignUpView.as_view()
    ),
    path(
        'account/password-reset/',
        account_views.PasswordResetView.as_view()
    ),
    path(
        'account/reset/<uidb64>/<token>/',
        account_views.PasswordResetConfirmView.as_view()
    ),
] + router.urls

if nested_routers:
    urlpatterns += nested_routers

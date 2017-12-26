from django.urls import path, include


urlpatterns = [
    path(
        'account/',
        include(('api.account.urls', 'account'), namespace='account')
    ),
    path(
        'common/',
        include(('api.common.urls', 'common'), namespace='common')
    ),
]

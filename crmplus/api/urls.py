from django.urls import path, include


urlpatterns = [
    path(
        'account/',
        include(('account.api.urls', 'account'), namespace='account')
    ),
    path(
        'common/',
        include(('common.api.urls', 'common'), namespace='common')
    ),
]

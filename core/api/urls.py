from django.urls import path, include


urlpatterns = [
    path(
        'panel/',
        include(
            ('panel.api.urls', 'panel'),
            namespace='panel'
        )
    ),
]

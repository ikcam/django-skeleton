from django.urls import path, include


urlpatterns = [
    path(
        '',
        include(
            ('public.api.urls', 'public'),
            namespace='public'
        )
    ),
]

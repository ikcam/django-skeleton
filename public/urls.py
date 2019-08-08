from django.urls import path

from public import views


urlpatterns = [
    path(
        '',
        views.IndexView.as_view(),
        name='index'
    ),
    path(
        'm/p/<pk>/',
        views.MessagePixelView.as_view(),
        name='message_pixel'
    ),
    path(
        'l/<pk>/',
        views.LinkDetailView.as_view(),
        name='link_detail'
    )
]

from django.urls import path
from django.utils.translation import gettext_lazy as _

from . import autocomplete, views


urlpatterns = [
    # autocomplete
    path(
        _('model-autocomplete/'),
        autocomplete.ModelAutocomplete.as_view(),
        name='model_autocomplete'
    ),
    # Event - events - event
    path(
        _('events/'),
        views.EventList.as_view(),
        name='event_list'
    ),
    path(
        _('events/add/'),
        views.EventCreate.as_view(),
        name='event_add'
    ),
    path(
        _('events/<int:pk>/'),
        views.EventDetail.as_view(),
        name='event_detail'
    ),
    path(
        _('events/<int:pk>/change/'),
        views.EventUpdate.as_view(),
        name='event_change'
    ),
    path(
        _('events/<int:pk>/delete/'),
        views.EventDelete.as_view(),
        name='event_delete'
    ),
    # Link - links - link
    path(
        _('links/'),
        views.LinkList.as_view(),
        name='link_list'
    ),
    path(
        _('links/add/'),
        views.LinkCreate.as_view(),
        name='link_add'
    ),
    path(
        _('links/<int:pk>/'),
        views.LinkDetail.as_view(),
        name='link_detail'
    ),
    path(
        _('links/<int:pk>/change/'),
        views.LinkUpdate.as_view(),
        name='link_change'
    ),
    path(
        _('links/<int:pk>/delete/'),
        views.LinkDelete.as_view(),
        name='link_delete'
    ),
    path(
        _('ld/<int:pk>/'),
        views.LinkPublicDirect.as_view(),
        name='link_public_direct'
    ),
    path(
        _('lt/<token>/'),
        views.LinkPublicToken.as_view(),
        name='link_public_token'
    ),
    # Message - messages - message
    path(
        _('messages/'),
        views.MessageList.as_view(),
        name='message_list'
    ),
    path(
        _('messages/<int:pk>/'),
        views.MessageDetail.as_view(),
        name='message_detail'
    ),
    path(
        _('messages/<int:pk>/frame/'),
        views.MessageFrame.as_view(),
        name='message_frame'
    ),
    path(
        _('messages/pixel/<token>/'),
        views.MessagePixel.as_view(),
        name='message_pixel'
    ),
]

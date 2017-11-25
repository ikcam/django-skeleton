from django.conf.urls import url
from django.utils.translation import ugettext_lazy as _

from . import autocomplete, views


urlpatterns = [
    # autocomplete
    url(
        r'^model-autocomplete/$',
        autocomplete.ModelAutocomplete.as_view(),
        name='model_autocomplete'
    ),
    # Event - events - event
    url(
        _(r'^events/$'),
        views.EventList.as_view(),
        name='event_list'
    ),
    url(
        _(r'^events/add/$'),
        views.EventCreate.as_view(),
        name='event_add'
    ),
    url(
        _(r'^events/(?P<pk>[0-9]+)/$'),
        views.EventDetail.as_view(),
        name='event_detail'
    ),
    url(
        _(r'^events/(?P<pk>[0-9]+)/change/$'),
        views.EventUpdate.as_view(),
        name='event_change'
    ),
    url(
        _(r'^events/(?P<pk>[0-9]+)/delete/$'),
        views.EventDelete.as_view(),
        name='event_delete'
    ),
    # Link - links - link
    url(
        _(r'^links/$'),
        views.LinkList.as_view(),
        name='link_list'
    ),
    url(
        _(r'^links/add/$'),
        views.LinkCreate.as_view(),
        name='link_add'
    ),
    url(
        _(r'^links/(?P<pk>[0-9]+)/$'),
        views.LinkDetail.as_view(),
        name='link_detail'
    ),
    url(
        _(r'^links/(?P<pk>[0-9]+)/change/$'),
        views.LinkUpdate.as_view(),
        name='link_change'
    ),
    url(
        _(r'^links/(?P<pk>[0-9]+)/delete/$'),
        views.LinkDelete.as_view(),
        name='link_delete'
    ),
    url(
        _(r'^ld/(?P<pk>[0-9]+)/$'),
        views.LinkPublicDirect.as_view(),
        name='link_public_direct'
    ),
    url(
        _(r'^lt/(?P<token>[0-9A-Za-z_\-]+)/$'),
        views.LinkPublicToken.as_view(),
        name='link_public_token'
    ),
    # Message - messages - message
    url(
        _(r'^messages/$'),
        views.MessageList.as_view(),
        name='message_list'
    ),
    url(
        _(r'^messages/(?P<pk>[0-9]+)/$'),
        views.MessageDetail.as_view(),
        name='message_detail'
    ),
    url(
        _(r'^messages/(?P<pk>[0-9]+)/frame/$'),
        views.MessageFrame.as_view(),
        name='message_frame'
    ),
    url(
        _(r'^messages/pixel/(?P<token>[0-9A-Za-z_\-]+)/$'),
        views.MessagePixel.as_view(),
        name='message_pixel'
    ),
]

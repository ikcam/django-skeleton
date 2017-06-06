from django.conf.urls import url
from django.utils.translation import ugettext_lazy as _

from . import views


urlpatterns = [
    url(
        _(r'^$'),
        views.Index.as_view(),
        name='index'
    ),
    # Company
    url(
        _(r'^company/$'),
        views.CompanyDetail.as_view(),
        name='company_list'
    ),
    url(
        _(r'^company/$'),
        views.CompanyDetail.as_view(),
        name='company_detail'
    ),
    url(
        _(r'^company/add/$'),
        views.CompanyCreate.as_view(),
        name='company_add'
    ),
    url(
        _(r'^company/change/$'),
        views.CompanyUpdate.as_view(),
        name='company_change'
    ),
    url(
        _(r'^company/switch/(?P<pk>[0-9]+)/$'),
        views.CompanySwitch.as_view(),
        name='company_switch'
    ),
    # Invites - invites - invite
    url(
        _(r'^company/invites/add/$'),
        views.InviteCreate.as_view(),
        name='invite_add'
    ),
    url(
        _(r'^company/invites/(?P<pk>[0-9]+)/delete/$'),
        views.InviteDelete.as_view(),
        name='invite_delete'
    ),
    url(
        _(r'^company/invites/(?P<pk>[0-9]+)/send/$'),
        views.InviteSend.as_view(),
        name='invite_send'
    ),
    url(
        _(r'^company/users/(?P<pk>[0-9]+)/remove/$'),
        views.UserRemove.as_view(),
        name='user_remove'
    ),
]

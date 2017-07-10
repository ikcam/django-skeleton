from django.conf.urls import url
from django.utils.translation import ugettext_lazy as _

from . import views


urlpatterns = [
    url(
        _(r'^$'),
        views.Index.as_view(),
        name='index'
    ),
    url(
        _(r'^dashboard/$'),
        views.Dashboard.as_view(),
        name='dashboard'
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
        _(r'^company/activate/$'),
        views.CompanyActivate.as_view(),
        name='company_activate'
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
        _(r'^company/choose/$'),
        views.CompanyChoose.as_view(),
        name='company_choose'
    ),
    url(
        _(r'^company/switch/(?P<pk>[0-9]+)/$'),
        views.CompanySwitch.as_view(),
        name='company_switch'
    ),
    # Invoice - invoices - invoice
    url(
        _(r'^company/invoices/$'),
        views.InvoiceList.as_view(),
        name='invoice_list'
    ),
    url(
        _(r'^company/invoices/(?P<pk>[0-9]+)/$'),
        views.InvoiceDetail.as_view(),
        name='invoice_detail'
    ),
    # Invite - invites - invite
    url(
        _(r'^company/invites/$'),
        views.InviteList.as_view(),
        name='invite_list'
    ),
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
    # User - users - user
    url(
        _(r'^company/users/$'),
        views.UserList.as_view(),
        name='user_list'
    ),
    url(
        _(r'^company/users/add/$'),
        views.UserCreate.as_view(),
        name='user_add'
    ),
    url(
        _(r'^company/users/(?P<pk>[0-9]+)/change/$'),
        views.UserUpdate.as_view(),
        name='user_change'
    ),
    url(
        _(r'^company/users/(?P<pk>[0-9]+)/password/$'),
        views.UserPassword.as_view(),
        name='user_password'
    ),
    url(
        _(r'^company/users/(?P<pk>[0-9]+)/permissions/$'),
        views.UserPermissions.as_view(),
        name='user_permissions'
    ),
    url(
        _(r'^company/users/(?P<pk>[0-9]+)/remove/$'),
        views.UserRemove.as_view(),
        name='user_remove'
    ),
]

from django.conf import settings
from django.urls import include, path
from django.conf.urls.i18n import i18n_patterns
from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from django.views.i18n import JavaScriptCatalog


urlpatterns = [
    path('i18n/', include('django.conf.urls.i18n')),
    path('ckeditor/', include('ckeditor_uploader.urls')),
    path('jsi18n/', JavaScriptCatalog.as_view(), name='javascript-catalog'),
]

if settings.DEBUG:
    from django.conf.urls.static import static

    import debug_toolbar

    urlpatterns += [
        path('__debug__/', include(debug_toolbar.urls))
    ]
    urlpatterns += static(
        settings.MEDIA_URL, document_root=settings.MEDIA_ROOT
    )
    urlpatterns += static(
        settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0]
    )

urlpatterns += i18n_patterns(
    path('jsi18n/', JavaScriptCatalog.as_view(), name='javascript-catalog'),
    path(
        _('admin/'),
        admin.site.urls
    ),
    path(
        _('account/'),
        include(('account.urls', 'account'), namespace='account')
    ),
    path(
        '',
        include(('core.urls', 'core'), namespace='core')
    ),
    path(
        '',
        include(('crm.urls', 'crm'), namespace='crm')
    ),
    # Common and API at the end
    path(
        _('common/'),
        include(('common.urls', 'common'), namespace='common')
    ),
    path(
        _('api/'),
        include(('crmplus.api.urls', 'api'), namespace='api')
    ),
)

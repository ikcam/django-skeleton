from django.conf import settings
from django.urls import include, path
from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from django.views.i18n import JavaScriptCatalog


urlpatterns = [
    path('jsi18n/',
         JavaScriptCatalog.as_view(),
         name='javascript-catalog'
         ),
    path(
        _('admin/'),
        admin.site.urls
    ),
    path(
        _('api/'),
        include(('core.api.urls', 'api'), namespace='api')
    ),
    path(
        _('panel/'),
        include(('panel.urls', 'panel'), namespace='panel')
    ),
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

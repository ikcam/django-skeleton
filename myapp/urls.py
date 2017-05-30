from django.conf import settings
from django.conf.urls import include, url
from django.conf.urls.i18n import i18n_patterns
from django.contrib import admin
from django.utils.translation import ugettext_lazy as _


urlpatterns = [
    url(r'^i18n/', include('django.conf.urls.i18n')),
    url(r'^ckeditor/', include('ckeditor_uploader.urls')),
]

if settings.DEBUG:
    import debug_toolbar

    urlpatterns = [
        url(r'^__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns

urlpatterns += i18n_patterns(
    url(_(r'^'), include('core.urls', namespace='core')),
    url(_(r'^admin/'), admin.site.urls),
    url(_(r'^account/'), include('account.urls', namespace='account')),
)

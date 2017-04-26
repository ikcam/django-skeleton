from django.conf.urls import url
from django.utils.translation import ugettext_lazy as _

from . import views


urlpatterns = [
    url(_(r'^$'), views.Index.as_view(), name='index'),
]

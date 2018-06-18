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

]

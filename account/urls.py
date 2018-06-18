from django.urls import path
from django.contrib.auth import views as auth_views
from django.utils.translation import ugettext_lazy as _
from django.urls import reverse_lazy

from . import autocomplete, views

urlpatterns = [
    # Autocomplete
    path(
        _('groups/autocomplete/'),
        autocomplete.GroupAutocomplete.as_view(),
        name='group_autocomplete'
    ),
    path(
        _('permissions/autocomplete/'),
        autocomplete.PermissionAutocomplete.as_view(),
        name='permission_autocomplete'
    ),
    path(
        _('users/autocomplete/'),
        autocomplete.UserAutocomplete.as_view(),
        name='user_autocomplete'
    ),
    path(
        _('users/other/autocomplete/'),
        autocomplete.UserOtherAutocomplete.as_view(),
        name='user_other_autocomplete'
    ),
    
]

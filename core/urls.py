from django.urls import path
from django.utils.translation import gettext_lazy as _

from . import autocomplete, views


urlpatterns = [
    # Country
    path(
        _('countries/autocomplete/'),
        autocomplete.CountryAutocomplete.as_view(),
        name='country_autocomplete'
    ),
    # Language
    path(
        _('languages/autocomplete/'),
        autocomplete.LanguageAutocomplete.as_view(),
        name='language_autocomplete'
    ),
    # Timezone
    path(
        _('timezones/autocomplete/'),
        autocomplete.TimezoneAutocomplete.as_view(),
        name='timezone_autocomplete'
    ),
    # Company
    path(
        _('company/'),
        views.CompanyDetail.as_view(),
        name='company_list'
    ),
    
    path(
        _('company/roles/autocomplete/'),
        autocomplete.RoleAutocomplete.as_view(),
        name='role_autocomplete'
    ),

]

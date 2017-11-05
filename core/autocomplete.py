import json
import pytz

from django.conf import settings
from django.http import HttpResponse

from dal import autocomplete
from django_countries import countries

from .models import Role


class CountryAutocomplete(autocomplete.Select2ListView):
    def get(self, request, *args, **kwargs):
        results = self.get_list()

        if self.q:
            results = [
                (code, name) for code, name in results
                if self.q.lower() in name.lower()
            ]

        return HttpResponse(json.dumps({
            'results': [dict(id=code, text=name) for code, name in results]
        }), content_type='application/json')

    def get_list(self):
        return list(countries)


class LanguageAutocomplete(autocomplete.Select2ListView):
    def get(self, request, *args, **kwargs):
        results = self.get_list()

        if self.q:
            results = [
                (code, name) for code, name in results
                if self.q.lower() in name.lower()
            ]

        return HttpResponse(json.dumps({
            'results': [
                dict(id=code, text=u'%s' % name) for code, name in results
            ]
        }), content_type='application/json')

    def get_list(self):
        return settings.LANGUAGES


class RoleAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        if (
            not self.request.user.is_authenticated or
            not self.request.user.profile.company
        ):
            return Role.objects.none()

        qs = Role.objects.filter(
            company=self.request.user.profile.company,
        )

        if self.q:
            qs = qs.filter(name__icontains=self.q)

        return qs


class TimezoneAutocomplete(autocomplete.Select2ListView):
    def get(self, request, *args, **kwargs):
        results = self.get_list()

        if self.q:
            results = [
                (code, name) for code, name in results
                if self.q.lower() in name.lower()
            ]

        return HttpResponse(json.dumps({
            'results': [
                dict(id=code, text=u'%s' % name) for code, name in results
            ]
        }), content_type='application/json')

    def get_list(self):
        return [(c, c) for c in pytz.common_timezones]

import json
import pytz

from django.conf import settings
from django.contrib.auth.models import Permission
from django.db.models import Q
from django.http import HttpResponse

from dal import autocomplete
from django_countries import countries
from queryset_sequence import QuerySetSequence

from core.mixins import CompanyRequiredMixin
from core.models import User


class CountryAutocomplete(
    autocomplete.Select2ListView
):
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


class LanguageAutocomplete(
    autocomplete.Select2ListView
):
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


class ModelAutocomplete(
    CompanyRequiredMixin, autocomplete.Select2QuerySetSequenceView
):
    def get_queryset(self):
        """Reconfigure."""
        messages = self.company.message_set.all()

        if self.q:
            messages = messages.filter(to_email__icontains=self.q)

        qs = QuerySetSequence(messages)
        qs = self.mixup_querysets(qs)

        return qs


class PermissionAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        if (
            not self.request.user.is_authenticated or
            not self.request.user.company
        ):
            return Permission.objects.none()

        qs = Permission.objects.all().exclude(
            content_type__app_label__in=(
                'admin', 'authtoken', 'contenttypes', 'sessions',
            )
        ).exclude(
            content_type__model__in=(
                'colaborator', 'group', 'logentry', 'payment', 'permission',
            )
        ).exclude(
            codename__in=(
                'add_invoice', 'change_invoice', 'delete_invoice',
                'add_company', 'delete_company'
            )
        )

        if self.q:
            qs = qs.filter(
                Q(name__icontains=self.q) |
                Q(content_type__app_label__icontains=self.q) |
                Q(content_type__model__icontains=self.q)
            )

        return qs


class RoleAutocomplete(
    CompanyRequiredMixin, autocomplete.Select2QuerySetView
):
    def get_queryset(self):
        qs = self.company.role_set.all()

        if self.q:
            qs = qs.filter(name__icontains=self.q)

        return qs


class TimezoneAutocomplete(
    autocomplete.Select2ListView
):
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


class UserAutocomplete(
    CompanyRequiredMixin, autocomplete.Select2QuerySetView
):
    def get_queryset(self):
        qs = User.objects.filter(
            companies=self.company
        )

        if self.q:
            qs = qs.filter(
                Q(username__istartswith=self.q) |
                Q(first_name__icontains=self.q) |
                Q(last_name__icontains=self.q)
            )

        return qs


class UserOtherAutocomplete(
    CompanyRequiredMixin, autocomplete.Select2QuerySetView
):
    def get_queryset(self):
        qs = User.objects.filter(
            companies=self.company
        ).exclude(pk=self.request.user.pk)

        if self.q:
            qs = qs.filter(
                Q(username__istartswith=self.q) |
                Q(first_name__icontains=self.q) |
                Q(last_name__icontains=self.q)
            )

        return qs

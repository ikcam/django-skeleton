from django import forms
from django.core.validators import EMPTY_VALUES
from django.db.models import Q
from django.utils.translation import ugettext_lazy as _

import django_filters

from core.models import Event, Notification


class EventFilterSet(django_filters.FilterSet):
    date_since = django_filters.DateTimeFilter(
        label=_("Since date"), method='filter_date_since',
        widget=forms.DateInput(attrs={'type': 'date-local'})
    )
    date_until = django_filters.DateTimeFilter(
        label=_("Until date"), method='filter_date_until',
        widget=forms.DateInput(attrs={'type': 'date-local'})
    )

    class Meta:
        fields = ('date_since', 'date_until')
        model = Event

    def filter_date_since(self, queryset, name, value):
        if value in EMPTY_VALUES:
            return queryset

        return queryset.filter(
            Q(date_creation__gte=value) |
            Q(date_start__gte=value)
        )

    def filter_date_until(self, queryset, name, value):
        if value in EMPTY_VALUES:
            return queryset

        return queryset.filter(
            Q(date_creation__lte=value) |
            Q(date_start__lte=value)
        )


class NotificationFilterSet(django_filters.FilterSet):
    is_read = django_filters.BooleanFilter(
        label=_("Read"), method='filter_is_read'
    )

    class Meta:
        fields = ('is_read', )
        model = Notification

    def filter_is_read(self, queryset, name, value):
        if value in EMPTY_VALUES:
            return queryset

        return queryset.filter(
            date_read__isnull=not value
        )
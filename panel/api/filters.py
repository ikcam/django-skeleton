from django.db.models import Q

import django_filters

from core import models as core


class EventFilterSet(django_filters.FilterSet):
    date_since = django_filters.DateTimeFilter(
        method='filter_date_since'
    )
    date_until = django_filters.DateTimeFilter(
        method='filter_date_until'
    )

    class Meta:
        fields = ('date_since', 'date_until')
        model = core.Event

    def filter_date_since(self, queryset, name, value):
        return queryset.filter(
            Q(date_creation__gte=value) |
            Q(date_start__gte=value)
        )

    def filter_date_until(self, queryset, name, value):
        return queryset.filter(
            Q(date_creation__lte=value) |
            Q(date_start__lte=value)
        )

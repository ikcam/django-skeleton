from django.core.validators import EMPTY_VALUES
from django.utils.translation import ugettext_lazy as _

import django_filters

from account.models import Notification


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

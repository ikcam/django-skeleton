from core import models as core

from core.api.mixins import CompanyViewSet
from panel.api import serializers, filters


class EventViewSet(CompanyViewSet):
    filter_class = filters.EventFilterSet
    model = core.Event
    permissions_required = 'core:view_event'
    queryset = model.objects.all()
    serializer_class = serializers.EventModelSerializer

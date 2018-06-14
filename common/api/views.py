from rest_framework import viewsets

from myapp.api.mixins import CompanyQuerySetMixin, NestedReadOnlyViewset
from common.models import Event, Link, Message, Visit
from . import filters, serializers


class EventViewSet(CompanyQuerySetMixin, viewsets.ReadOnlyModelViewSet):
    filter_class = filters.EventFilterSet
    model = Event
    permissions_required = 'common:view_event'
    queryset = Event.objects.all()
    serializer_class = serializers.EventModelSerializer


class MessageViewSet(CompanyQuerySetMixin, viewsets.ReadOnlyModelViewSet):
    model = Message
    permissions_required = 'common:view_message'
    queryset = Message.objects.all()
    serializer_class = serializers.MessageModelSerializer


class LinkViewSet(NestedReadOnlyViewset, viewsets.ReadOnlyModelViewSet):
    model = Link
    permissions_required = 'common:view_link'
    queryset = Link.objects.all()
    serializer_class = serializers.LinkModelSerializer


class VisitViewSet(NestedReadOnlyViewset, viewsets.ReadOnlyModelViewSet):
    company_fields = 'link__company'
    model = Visit
    permissions_required = 'common:view_visit'
    queryset = Visit.objects.all()
    serializer_class = serializers.VisitModelSerializer

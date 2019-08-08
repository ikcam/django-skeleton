from django.utils.translation import ugettext_lazy as _

from rest_framework import response, status
from rest_framework.decorators import action

from core import models as core
from core.api.mixins import (
    CompanyReadOnlyViewSet, CompanyViewSet, NestedReadOnlyViewset
)
from core.constants import LEVEL_SUCCESS
from panel.api import serializers, filters


class EventViewSet(CompanyViewSet):
    filter_class = filters.EventFilterSet
    model = core.Event
    permissions_required = 'core:view_event'
    queryset = model.objects.all()
    serializer_class = serializers.EventSerializer


class LinkViewSet(NestedReadOnlyViewset):
    model = core.Link
    parent_model = core.Message
    parent_relation_field = 'message'
    permission_required = 'core:view_link'
    queryset = model.objects.all()
    serializer_class = serializers.LinkSerializer


class MessageViewSet(CompanyReadOnlyViewSet):
    model = core.Message
    permission_required = 'core:view_message'
    queryset = model.objects.all()


class NotificationViewSet(CompanyViewSet):
    filter_class = filters.NotificationFilterSet
    model = core.Notification
    queryset = model.objects.all()
    bypass_permissions = True
    serializer_class = serializers.NotificationSerializer

    def delete(self, *args, **kwargs):
        return response.Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(user=self.request.user)

    def update(self, *args, **kwargs):
        return response.Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    @action(methods=['post'], detail=False, url_path='set-all-read')
    def set_all_read(self, request, *args, **kwargs):
        self.model.objects.set_all_read(
            company=request.company,
            user=request.user
        )

        return response.Response(
            dict(detail=_("All notifications were marked as read.")),
            status=status.HTTP_202_ACCEPTED
        )

    @action(methods=['post'], detail=True, url_path='set-read')
    def set_read(self, request, *args, **kwargs):
        obj = self.get_object()
        level, msg = obj.set_read()

        return response.Response(
            dict(detail=msg),
            status=(
                status.HTTP_202_ACCEPTED
                if level is LEVEL_SUCCESS else status.HTTP_400_BAD_REQUEST
            )
        )


class VisitViewSet(NestedReadOnlyViewset):
    company_field = 'link__company'
    model = core.Visit
    parent_model = core.Link
    parent_relation_field = 'link'
    permission_required = 'core:view_visit'
    queryset = model.objects.all()
    serializer_class = serializers.VisitSerializer

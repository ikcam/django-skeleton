from rest_framework import mixins, status, viewsets
from rest_framework.response import Response
from rest_framework.decorators import action

from core.models import Event, Link, Message, Notification, User, Visit
from core.api.mixins import (
    CompanyReadOnlyViewSet, CompanyViewSet, NestedReadOnlyViewset
)
from . import filters, serializers


class EventViewSet(CompanyViewSet):
    filter_class = filters.EventFilterSet
    model = Event
    permissions_required = 'common:view_event'
    queryset = Event.objects.all()
    serializer_class = serializers.EventModelSerializer


class LinkViewSet(NestedReadOnlyViewset):
    model = Link
    permissions_required = 'common:view_link'
    queryset = Link.objects.all()
    serializer_class = serializers.LinkModelSerializer


class MessageViewSet(CompanyReadOnlyViewSet):
    model = Message
    permissions_required = 'common:view_message'
    queryset = Message.objects.all()
    serializer_class = serializers.MessageModelSerializer


class NotificationViewSet(CompanyReadOnlyViewSet):
    filter_class = filters.NotificationFilterSet
    model = Notification
    queryset = Notification.objects.all()
    serializer_class = serializers.NotificationModelSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(
            user=self.request.user
        )


class UserViewSet(
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    viewsets.GenericViewSet
):
    model = User
    queryset = User.objects.all()

    def get_object(self):
        return self.request.user

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return serializers.UserCreateSerializer
        elif self.request.method in ('PUT', 'PATCH'):
            return serializers.UserUpdateSerializer
        elif self.request.method == 'GET':
            return serializers.UserDetailSerializer

    @action(
        detail=False,
        methods=['post'],
        url_path='password-change',
        url_name='password_change'
    )
    def password_change(self, request):
        serializer_class = serializers.PasswordChangeSerializer
        serializer = serializer_class(data=request.data)
        if serializer.is_valid():
            return Response({'status': 'password set'})
        else:
            return Response(
                serializer.errors, status=status.HTTP_400_BAD_REQUEST
            )


class VisitViewSet(NestedReadOnlyViewset):
    company_fields = 'link__company'
    model = Visit
    permissions_required = 'common:view_visit'
    queryset = Visit.objects.all()
    serializer_class = serializers.VisitModelSerializer

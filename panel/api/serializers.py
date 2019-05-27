from rest_framework import serializers

from core.api.serializers import ActionSerializer
from core import models as core


class EventSerializer(ActionSerializer):
    user = serializers.StringRelatedField()
    type_color = serializers.SerializerMethodField()

    class Meta:
        fields = (
            'id', 'user', 'share_with', 'date', 'date_creation',
            'date_start', 'date_finish', 'subject', 'content', 'type',
            'type_color', 'is_public', 'action_list'
        )
        model = core.Event

    def get_type_color(self, obj):
        return obj.get_type_color()


class LinkSerializer(ActionSerializer):
    class Meta:
        fields = (
            'id', 'destination', 'date_creation', 'is_open', 'total_visits',
            'action_list'
        )
        model = core.Link


class NotificationSerializer(ActionSerializer):
    class Meta:
        fields = '__all__'
        model = core.Notification


class VisitSerializer(ActionSerializer):
    class Meta:
        fields = '__all__'
        model = core.Visit

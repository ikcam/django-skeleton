from rest_framework import serializers

from api.serializers import ActionSerializer
from common.models import Event, Link, Message, Visit


class EventModelSerializer(ActionSerializer):
    user = serializers.StringRelatedField()

    class Meta:
        fields = (
            'id', 'user', 'share_with', 'date', 'date_creation',
            'date_start', 'date_finish', 'subject', 'content', 'type',
            'is_public', 'actions'
        )
        model = Event


class LinkModelSerializer(ActionSerializer):
    class Meta:
        fields = (
            'id', 'date_creation', 'message', 'user', 'token', 'destination',
            'is_open', 'total_visits', 'actions'
        )
        model = Link


class MessageModelSerializer(ActionSerializer):
    class Meta:
        fields = (
            'id', 'contenttype', 'model', 'status', 'direction',
            'date_creation', 'date_modification', 'from_email', 'from_name',
            'to_email', 'to_email_cc', 'reply_to_email', 'subject', 'content',
            'actions'
        )
        model = Message


class VisitModelSerializer(ActionSerializer):
    class Meta:
        fields = (
            'id', 'date_creation', 'link', 'ip_address', 'actions'
        )
        model = Visit

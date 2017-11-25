from api.serializers import ActionSerializer
from common.models import Link, Message, Visit


class LinkModelSerializer(ActionSerializer):
    class Meta:
        fields = (
            'id', 'message', 'user', 'token', 'destination', 'is_open',
            'total_visits', 'actions'
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
            'id', 'link', 'ip_address', 'actions'
        )
        model = Visit

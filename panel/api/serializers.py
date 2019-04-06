from rest_framework import serializers

from core.api.serializers import ActionSerializer
from core import models as core


class EventModelSerializer(ActionSerializer):
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

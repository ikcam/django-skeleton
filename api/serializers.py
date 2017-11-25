from django.utils.translation import ugettext_lazy as _

from boilerplate.templatetags.boilerplate import (
    model_action, model_child_action
)
from rest_framework import serializers


class ActionSerializer(serializers.ModelSerializer):
    actions = serializers.SerializerMethodField()
    model = serializers.StringRelatedField()

    def get_actions(self, obj):
        actions = {'view': dict(
            title=_("View"),
            url=obj.get_absolute_url(),
            btn_class='info',
            btn_icon='eye-open',
        )}

        if not hasattr(obj, 'actions') or not obj.actions:
            return actions

        for title, act, class_, icon, permission in obj.actions:
            if hasattr(obj, 'parent') and obj.parent:
                url = model_child_action(obj, obj.parent, act)
            else:
                url = model_action(obj, act)

            actions[act] = dict(
                title=title,
                url=url,
                btn_class=class_,
                btn_icon=icon,
            )
        return actions

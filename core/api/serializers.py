from django.urls import reverse_lazy
from django.utils.translation import ugettext_lazy as _

from rest_framework import serializers

from core.constants import ACTIONS


class ActionSerializer(serializers.ModelSerializer):
    action_list = serializers.SerializerMethodField()
    model = serializers.StringRelatedField()

    def get_action_list(self, object):
        action_list = {'view': dict(
            title=_("View"),
            url=object.get_absolute_url(),
            btn_class='info',
            btn_icon='eye-open',
            visible=False,
        )}

        if not hasattr(object, 'action_list') or not object.action_list:
            return action_list

        for action in object.action_list:
            action_details = ACTIONS[action]
            app_name = object._meta.app_label
            app_name = app_name if app_name != 'core' else 'panel'
            args = []
            model = object.__class__.__name__.lower()
            parent = None

            if hasattr(object, 'parent') and object.parent:
                parent = object.parent.__class__.__name__.lower()
                args += [object.parent.pk]
                url_name = '{app_name}:{parent}_{model}_{action}'
            else:
                url_name = '{app_name}:{model}_{action}'
            args += [object.pk]

            url_name = url_name.format(
                app_name=app_name,
                model=model,
                parent=parent,
                action=action,
            )
            url = reverse_lazy(url_name, args=args)

            action_list[action] = dict(
                title=action_details['title'],
                url=url,
                btn_class=action_details['level'],
                btn_icon=action_details['icon'],
                visible=True,
            )
        return action_list

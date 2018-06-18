from django import template
from django.conf import settings as django_settings
from django.core.exceptions import ImproperlyConfigured
from django.urls import resolve, reverse_lazy
from django.utils.html import mark_safe

from core.constants import ACTIONS

register = template.Library()


@register.simple_tag(takes_context=True)
def settings(context, name):
    try:
        company = context['company']
        site_url = company.custom_domain or django_settings.SITE_URL
        site_name = company.name
        site_short_name = '{}+'.format(site_name[:2])
    except Exception:
        try:
            company = context['object'].company
            site_url = company.custom_domain or django_settings.SITE_URL
            site_name = company.name
            site_short_name = '{}+'.format(site_name[:2])
        except Exception:
            site_url = django_settings.SITE_URL
            site_name = django_settings.SITE_NAME
            site_short_name = django_settings.SITE_SHORT_NAME

    secure_settings = {
        'SITE_URL': site_url,
        'SITE_SHORT_NAME': site_short_name.upper(),
        'SITE_NAME': site_name,
        'FB_APP_ID': django_settings.FB_APP_ID,
        'CULQI_PUBLIC_KEY': django_settings.CULQI_PUBLIC_KEY,
    }
    return secure_settings.get(name, '')


@register.simple_tag()
def api_list_view(model, parent_obj=None):
    if parent_obj:
        parent_model = parent_obj.__class__.__name__.lower()

        return reverse_lazy(
            'api:{}:{}_{}-list'.format(
                parent_obj._meta.app_label, parent_model, model
            ),
            args=[parent_obj.pk, ]
        )
    else:
        return reverse_lazy(
            'api:{}-list'.format(model.app_label, model)
        )


@register.simple_tag(takes_context=True)
def action_button(
    context, action, object=None, object_list=None, size='sm',
    grouped=True, grouped_first=False, grouped_last=False, has_dropdown=True
):
    try:
        action_details = ACTIONS[action]
    except IndexError:
        action_details = None

    if not action_details:
        raise ImproperlyConfigured("Configure the action %s" % action)
    elif (object is None and object_list is None) or (object and object_list):
        raise ImproperlyConfigured(
            "Either define an `object` or a `object_list`"
        )

    app_name = resolve(context['request'].path).app_name
    if object is not None:
        relation = object.__class__.__name__.lower()
    elif object_list is not None:
        relation = object_list.model.__name__.lower()

    url_name = '{}:'.format(app_name)

    if object is not None:
        url_name = '{}{}_{}'.format(url_name, relation, action)
        url = reverse_lazy(url_name, args=[object.pk])
    elif object_list is not None:
        url_name = '{}{}_{}'.format(url_name, relation, action)
        url = reverse_lazy(url_name)

    if grouped_first:
        content = (
            '<a type="button" href={href} class="btn btn-{class_} btn-{size}">'
            '<span class="glyphicon glyphicon-{icon}"></span> '
            '{title}'
            '</a>'
        ).format(
            class_=action_details['class'],
            href=url,
            icon=action_details['icon'],
            size=size,
            title=action_details['title'],
        )

        if has_dropdown:
            content = (
                '{content}'
                '<button type="button" class="btn btn-{class_} btn-{size} '
                'dropdown-toggle" data-toggle="dropdown" aria-haspopup="true" '
                'aria-expanded="false">'
                '<span class="caret"></span>'
                '<span class="sr-only">Toggle Dropdown</span>'
                '</button>'
                '<ul class="dropdown-menu-right dropdown-menu">'
            ).format(
                content=content,
                class_=action_details['class'],
                size=size,
            )
    else:
        content = (
            '<li>'
            '<a href="{href}">'
            '<span class="glyphicon glyphicon-{icon}"></span> '
            '{title}'
            '</a>'
            '</li>'
        ).format(
            href=url,
            icon=action_details['icon'],
            title=action_details['title']
        )
        if grouped_last:
            content = (
                '{content}'
                '</ul>'
            ).format(
                content=content
            )

    return content


@register.simple_tag(takes_context=True)
def action_buttons(
    context, action_list=None, object=None, object_list=None, size='sm',
    grouped=True
):
    if not action_list:
        return ''

    buttons = list()
    index = 1
    total = len(action_list)

    for action in action_list:
        if index == 1:
            buttons.append(action_button(
                context=context,
                action=action,
                object=object,
                object_list=object_list,
                size=size,
                grouped=grouped,
                grouped_first=True,
                has_dropdown=True if total > 1 else False
            ))
        else:
            buttons.append(action_button(
                context=context,
                action=action,
                object=object,
                object_list=object_list,
                size=size,
                grouped=grouped,
                grouped_last=True if index == total else False,
            ))

        index += 1
    return mark_safe('<div class="btn-group">' + ''.join(buttons) + '</div>')

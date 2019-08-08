from django import template
from django.apps import apps
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.core.validators import EMPTY_VALUES
from django.urls import reverse_lazy
from django.utils.html import mark_safe
from django.utils.translation import ugettext_lazy as _

from boilerplate.templatetags.boilerplate import url_replace

from core.constants import ACTIONS
from core.models import Company


register = template.Library()


def render(tag, content=None, **kwargs):
    attrs = ''
    for attr in kwargs:
        attrs += ' {attr}="{value}"'.format(attr=attr, value=kwargs[attr])

    response = '<{tag} {attrs}'
    response += '>{content}</{tag}>' if content is not None else ' />'

    return response.format(attrs=attrs, content=content, tag=tag)


def build_breadcrumb_item(**kwargs):
    kwargs.update({'class': 'breadcrumb-item'})
    if kwargs.get('href', None):
        content = render('a', kwargs.pop('content'), href=kwargs.pop('href'))
    else:
        content = render('strong', kwargs.pop('content'))

    return render('li', content, **kwargs)


def build_icon(icon):
    class_ = 'glyphicon glyphicon-{}'.format(icon)
    return render('span', '', **{'class': class_})


def build_button(**kwargs):
    action_details = ACTIONS[kwargs['action']]
    href = build_url(**kwargs)
    icon = build_icon(action_details['icon'])
    title = action_details['title']
    class_ = 'btn btn-%(size)s btn-%(level)s' % dict(
        size=kwargs['size'],
        level=action_details['level'],
    )
    content = '{} {}'.format(icon, title)
    inline = kwargs.get('inline', False)
    index = kwargs.get('index')
    total = kwargs.get('total')

    if inline:
        return render(
            'a',
            content=content,
            **{'class': class_, 'href': href}
        )
    else:
        if index == 0:
            button_first = render(
                'a',
                content=content,
                **{
                    'class': class_,
                    'href': href,
                }
            )
            button_second = render(
                'button',
                content=render('span', ''),
                **{
                    'class': class_ + ' dropdown-toggle',
                    'data-toggle': 'dropdown',
                }
            )
            if total > 1:
                return button_first + button_second
            else:
                return button_first
        else:
            return render(
                'li', content=render('a', content=content, href=href)
            )


def build_url(
    app_name, action, object=None, object_list=None, parent_object=None,
    **kwargs
):
    args = []
    url_name = app_name + ':'

    if parent_object:
        url_name += parent_object.__class__.__name__.lower() + '_'
        args.append(parent_object.pk)

    if object:
        url_name += object.__class__.__name__.lower()
        args.append(object.pk)
    elif object_list is not None:
        url_name += object_list.model.__name__.lower()
    url_name += '_' + action

    return reverse_lazy(url_name, args=args)


@register.simple_tag(takes_context=True)
def action_buttons(context, **kwargs):
    object = (
        kwargs.get('object', None) or
        context.get('object', None)
    )
    object_list = (
        kwargs.get('object_list', None) or
        context.get('object_list', None)
    )
    parent_object = (
        kwargs.get('parent_object', None) or
        context.get('parent_object', None)
    )

    if object is not None and hasattr(object, 'action_list'):
        action_list = object.action_list
    elif object_list is not None:
        action_list = (
            kwargs.get('action_list', None) or
            context.get('action_list', None)
        )
    else:
        action_list = None

    if callable(action_list):
        action_list = action_list()

    if action_list in EMPTY_VALUES:
        return ''

    app_name = (
        kwargs.get('app_name', None) or
        context['request'].resolver_match.app_name
    )
    inline = True if kwargs.get('inline') else False
    index = 0
    size = kwargs.get('size', 'size-default')
    response = ''
    response_items = []

    for action in action_list:
        if object:
            model_app = object._meta.app_label.lower()
            model = object.__class__.__name__.lower()
        elif object_list is not None:
            model_app = object_list.model._meta.app_label.lower()
            model = object_list.model.__name__.lower()
        action_details = ACTIONS[action] if action else None

        permission_name = '{model_app}:{prefix}_{model}'.format(
            model_app=model_app,
            model=model,
            prefix=action_details['permission_prefix'],
        )

        if not context['user'].has_company_perm(
            context['request'].company, permission_name
        ):
            continue

        button = build_button(
            action=action,
            app_name=app_name,
            inline=inline,
            index=index,
            object=object,
            object_list=object_list,
            parent_object=parent_object,
            size=size,
            total=len(action_list),
        )

        if inline or index == 0:
            response += button + ' '
        else:
            response_items.append(button)
        index += 1

    if inline:
        return mark_safe(response)

    if len(response_items) == 0:
        response_items = ''
    else:
        response_items = render(
            'ul',
            content=''.join(response_items),
            **{'class': 'dropdown-menu dropdown-menu-right'}
        )

    return mark_safe(
        render(
            'div',
            content=(response + response_items),
            **{'class': 'btn-group'}
        )
    )


@register.simple_tag(takes_context=True)
def breadcrumb(context, **kwargs):
    action = (
        kwargs.get('action', None) or
        context.get('action', None)
    )
    action_details = ACTIONS[action] if action else None
    object = (
        kwargs.get('object', None) or
        context.get('object', None)
    )
    object_list = (
        kwargs.get('object_list', None) or
        context.get('object_list', None)
    )
    form = (
        kwargs.get('form', None) or
        context.get('form', None)
    )
    parent_object = (
        kwargs.get('parent_object', None) or
        context.get('parent_object', None)
    )

    response = list()

    # Home
    href = settings.LOGIN_REDIRECT_URL
    content = _("Home")
    response.append(
        build_breadcrumb_item(content=content, href=href)
    )

    # Current app
    app_name = (
        kwargs.get('app_name', None) or
        context['request'].resolver_match.app_name
    )

    if app_name != 'public':
        href = reverse_lazy('{}:index'.format(app_name))

        if parent_object:
            content = parent_object._meta.app_config.verbose_name
        elif object:
            content = object._meta.app_config.verbose_name
        elif object_list is not None:
            content = object_list.model._meta.app_config.verbose_name
        elif form and hasattr(form, '_meta'):
            content = form._meta.model._meta.app_config.verbose_name
        else:
            content = apps.get_app_config(app_name).verbose_name

        response.append(
            build_breadcrumb_item(content=content, href=href)
        )

    if parent_object:
        # Add list
        model_name = parent_object.__class__.__name__.lower()
        href = reverse_lazy('{}:{}_list'.format(app_name, model_name))
        content = parent_object._meta.verbose_name_plural
        response.append(
            build_breadcrumb_item(content=content, href=href)
        )
        # Add detail
        response.append(
            build_breadcrumb_item(
                content=parent_object,
                href=parent_object.get_absolute_url()
            )
        )

    if object_list is not None:
        content = object_list.model._meta.verbose_name_plural
        response.append(
            build_breadcrumb_item(content=content)
        )
    elif object:
        # Add list
        model_name = object.__class__.__name__.lower()
        content = object._meta.verbose_name_plural
        if not parent_object:
            href = reverse_lazy('{}:{}_list'.format(app_name, model_name))
            response.append(
                build_breadcrumb_item(content=content, href=href)
            )
        else:
            response.append(
                build_breadcrumb_item(content=content)
            )
        if form:
            # Add detail
            response.append(
                build_breadcrumb_item(
                    content=object,
                    href=object.get_absolute_url()
                )
            )
            if action:
                content = ACTIONS[action]['title']
                response.append(
                    build_breadcrumb_item(content=content)
                )
        elif action:
            response.append(
                build_breadcrumb_item(
                    content=object, href=object.get_absolute_url()
                )
            )
            response.append(
                build_breadcrumb_item(content=action_details['title'])
            )
        else:
            response.append(
                build_breadcrumb_item(content=object)
            )
    elif form:
        if hasattr(form, '_meta'):
            # Add list
            model_name = form._meta.model.__name__.lower()
            content = form._meta.model._meta.verbose_name_plural
            if parent_object:
                response.append(
                    build_breadcrumb_item(content=content)
                )
            else:
                href = reverse_lazy('{}:{}_list'.format(app_name, model_name))
                response.append(
                    build_breadcrumb_item(content=content, href=href)
                )

        if action:
            content = ACTIONS[action]['title']
            response.append(
                build_breadcrumb_item(content=content)
            )

    return mark_safe(
        render('ol', ''.join(response), **{'class': 'breadcrumb'})
    )


@register.simple_tag(takes_context=True)
def sortable_column(context, **kwargs):
    request = context['request']
    field = kwargs.get('field')
    title = kwargs.get('title')

    if 'o' in request.GET and request.GET['o'] == field:
        href = url_replace(request, 'o', '-{}'.format(field))
        icon = render('i', '', **{'class': 'fa fa-sort-asc'})
    elif 'o' in request.GET and request.GET['o'] == '-{}'.format(field):
        href = url_replace(request, 'o', '{}'.format(field))
        icon = render('i', '', **{'class': 'fa fa-sort-desc'})
    else:
        href = url_replace(request, 'o', '{}'.format(field))
        icon = render('i', '', **{'class': 'fa fa-sort'})

    return mark_safe(
        render(
            'a',
            '{} {}'.format(_(title), icon),
            href='?{}'.format(href)
        )
    )


@register.filter(name='has_module')
def has_module(company, module):
    if not isinstance(company, Company):
        return False
    return company.has_module(module)


@register.filter(name='module_price')
def module_price(company, module):
    if not isinstance(company, Company):
        return False
    return company.module_price(module)


@register.filter(name='event_url')
def event_url(object):
    ct = ContentType.objects.get_for_model(object)
    slug = '{}-{}'.format(ct.id, object.id)
    return reverse_lazy('public:event_add_object', args=[slug])

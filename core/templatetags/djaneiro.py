from django import template
from django.conf import settings
from django.core.validators import EMPTY_VALUES
from django.contrib.contenttypes.models import ContentType
from django.urls import resolve, reverse_lazy
from django.utils.html import mark_safe
from django.utils.translation import ugettext_lazy as _

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

    return render(
        'a',
        content=content,
        **{'class': class_, 'href': href}
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

    if action_list in EMPTY_VALUES:
        return ''

    if callable(action_list):
        action_list = action_list()

    app_name = (
        kwargs.get('app_name', None) or
        resolve(context['request'].path).app_name
    )
    grouped = True if kwargs.get('grouped') else False
    size = kwargs.get('size', 'size-default')
    response = ''

    for action in action_list:
        response += build_button(
            action=action,
            app_name=app_name,
            grouped=grouped,
            object=object,
            object_list=object_list,
            parent_object=parent_object,
            size=size,
        )

    return mark_safe(response)


@register.simple_tag(takes_context=True)
def breadcrumb(context, **kwargs):
    action = (
        kwargs.get('action', None) or
        context.get('action', None)
    )
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
        resolve(context['request'].path).app_name
    )

    if app_name != 'public':
        href = reverse_lazy('{}:index'.format(app_name))

        if parent_object:
            content = parent_object._meta.app_config.verbose_name
        elif object:
            content = object._meta.app_config.verbose_name
        elif object_list is not None:
            content = object_list.model._meta.app_config.verbose_name
        elif form:
            content = form._meta.model._meta.app_config.verbose_name

        response.append(
            build_breadcrumb_item(content=content, href=href)
        )

    if parent_object:
        # Add list
        model_name = parent_object.__class__.__name__.lower()
        href = reverse_lazy('{}:{}_list'.format(app_name, model_name))
        content = parent_object._model.verbose_name_plural
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
        href = reverse_lazy('{}:{}_list'.format(app_name, model_name))
        content = object._meta.verbose_name_plural
        response.append(
            build_breadcrumb_item(content=content, href=href)
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
        else:
            response.append(
                build_breadcrumb_item(content=object)
            )
    elif form:
        # Add list
        model_name = form._meta.model.__name__.lower()
        href = reverse_lazy('{}:{}_list'.format(app_name, model_name))
        content = form._meta.model._meta.verbose_name_plural
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


@register.filter(name='has_module')
def has_module(company, module):
    if not isinstance(company, Company):
        return False
    return company.has_module(module)


@register.filter(name='event_url')
def event_url(object):
    ct = ContentType.objects.get_for_model(object)
    slug = '{}-{}'.format(ct.id, object.id)
    return reverse_lazy('public:event_add_object', args=[slug])

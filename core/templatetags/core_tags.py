from django import template
from django.urls import resolve, reverse_lazy


register = template.Library()


@register.simple_tag(takes_context=True)
def api_list_view(context, model, parent_obj=None):
    if parent_obj:
        parent_model = parent_obj.__class__.__name__.lower()

        app_name = resolve(context['request'].path).app_name

        return reverse_lazy(
            'api:{}:{}_{}-list'.format(
                app_name,
                parent_model,
                model
            ),
            args=[parent_obj.pk, ]
        )
    else:
        return reverse_lazy(
            'api:{}:{}-list'.format(model.app_label, model)
        )


@register.simple_tag(takes_context=True)
def user_permissions_url(context, user):
    company = context['request'].company
    colaborator = user.as_colaborator(company)
    if colaborator:
        return ''
    return reverse_lazy('public:user_permissions', args=[colaborator.pk])


@register.simple_tag(takes_context=True)
def user_remove_url(context, user):
    company = context['request'].company
    colaborator = user.as_colaborator(company)
    if colaborator:
        return ''
    return reverse_lazy('public:user_remove', args=[colaborator.pk])

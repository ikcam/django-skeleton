from django import template
from django.urls import resolve, reverse_lazy

from core.models import Colaborator


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


@register.simple_tag()
def user_permissions_url(user_id, company_id):
    try:
        company_profile = Colaborator.objects.get(company_id=company_id, user_id=user_id)
    except Colaborator.DoesNotExist:
        return ''
    return reverse_lazy('public:user_permissions', args=[company_profile.pk])


@register.simple_tag()
def user_remove_url(user_id, company_id):
    try:
        company_profile = Colaborator.objects.get(company_id=company_id, user_id=user_id)
    except Colaborator.DoesNotExist:
        return ''
    return reverse_lazy('public:user_remove', args=[company_profile.pk])

from django import template
from django.conf import settings
from django.urls import reverse_lazy


register = template.Library()


@register.simple_tag()
def fb_app_id():
    return settings.FB_APP_ID


@register.simple_tag()
def site_short_name():
    return settings.SITE_SHORT_NAME


@register.simple_tag(takes_context=True)
def site_name(context):
    try:
        company = context['company']
        return company.name or settings.SITE_NAME
    except Exception:
        try:
            company = context['object'].company
            return company.name or settings.SITE_NAME
        except Exception:
            return settings.SITE_NAME


@register.simple_tag(takes_context=True)
def site_url(context):
    try:
        company = context['company']
        return company.custom_domain or settings.SITE_URL
    except Exception:
        try:
            company = context['object'].company
            return company.custom_domain or settings.SITE_URL
        except Exception:
            return settings.SITE_URL


@register.simple_tag()
def culqi_public_key():
    return settings.CULQI_PUBLIC_KEY


@register.simple_tag()
def api_list_view(model, parent_obj=None):
    if parent_obj:
        parent_model = parent_obj.__class__.__name__.lower()

        return reverse_lazy(
            'api:{}_{}-list'.format(parent_model, model),
            args=[parent_obj.pk, ]
        )
    else:
        return reverse_lazy(
            'api:{}-list'.format(model)
        )

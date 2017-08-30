from django import template
from django.conf import settings


register = template.Library()


@register.simple_tag()
def site_name():
    return settings.SITE_NAME


@register.simple_tag()
def site_short_name():
    return settings.SITE_SHORT_NAME


@register.simple_tag(takes_context=True)
def site_url(context):
    try:
        url = context['object'].company.custom_domain
        return url or settings.SITE_URL
    except Exception:
        return settings.SITE_URL


@register.simple_tag()
def culqi_public_key():
    return settings.CULQI_PUBLIC_KEY

from django import template
from django.conf import settings as django_settings
from django.urls import resolve, reverse_lazy

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
            'api:{}-list'.format(model.app_label, model)
        )

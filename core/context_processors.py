from django.conf import settings as django_settings


def settings(request=None):
    if request and request.user.is_authenticated and request.user.company:
        company = request.user.company
        site_name = company.name
        site_short_name = '{}+'.format(site_name[:2])
        site_url = company.custom_domain or django_settings.SITE_URL
    else:
        site_name = django_settings.SITE_NAME
        site_short_name = django_settings.SITE_SHORT_NAME
        site_url = django_settings.SITE_URL


    secure_settings = {
        'SITE_NAME': site_name,
        'SITE_URL': site_url,
        'SITE_SHORT_NAME': site_short_name.upper(),
        'FB_APP_ID': django_settings.FB_APP_ID,
        'GA_ID': django_settings.GA_ID,
        'BRAINTREE_PUBLIC_KEY': django_settings.BRAINTREE_PUBLIC_KEY,
        'CULQI_PUBLIC_KEY': django_settings.CULQI_PUBLIC_KEY,
        'STRIPE_PUBLIC_KEY': django_settings.STRIPE_PUBLIC_KEY,
        'ONESIGNAL_APP_ID': django_settings.ONESIGNAL_APP_ID,
    }
    return {'settings': secure_settings}

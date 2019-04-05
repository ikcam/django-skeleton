from django.conf import settings as django_settings


def settings(request=None):
    secure_settings = {
        'FB_APP_ID': django_settings.FB_APP_ID,
        'GA_ID': django_settings.GA_ID,
        'ONESIGNAL_APP_ID': django_settings.ONESIGNAL_APP_ID,
    }
    return {'settings': secure_settings}

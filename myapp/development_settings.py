import os

from .settings import BASE_DIR, INSTALLED_APPS, MIDDLEWARE


DEBUG = True


ALLOWED_HOSTS = ['*']


INTERNAL_IPS = [
    '127.0.0.1'
]


INSTALLED_APPS += [
    'debug_toolbar',
]


MIDDLEWARE += [
    'debug_toolbar.middleware.DebugToolbarMiddleware',
]


EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'


MESSAGE_STORAGE = 'django.contrib.messages.storage.cookie.CookieStorage'


CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
    }
}


# Site info

SITE_URL = 'http://localhost:8000'

SITE_NAME = 'My App (Local)'

SITE_SHORT_NAME = 'MA+'


CULQI_PUBLIC_KEY = None

CULQI_PRIVATE_KEY = None

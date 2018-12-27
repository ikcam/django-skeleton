import os

from .settings import BASE_DIR, INSTALLED_APPS, MIDDLEWARE


DEBUG = False


ALLOWED_HOSTS = [
    'stg.myapp.com',
    'www.stg.myapp.com',
]


INTERNAL_IPS = [
    '127.0.0.1'
]


INSTALLED_APPS += [
    'debug_toolbar',
]


MIDDLEWARE += [
    'debug_toolbar.middleware.DebugToolbarMiddleware',
]


# Site info

SITE_URL = 'http://stg.myapp.com'

SITE_NAME = 'My App (Staging)'

SITE_SHORT_NAME = 'MA+'

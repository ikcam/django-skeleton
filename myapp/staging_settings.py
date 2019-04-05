from .settings import INSTALLED_APPS, MIDDLEWARE


DEBUG = False


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

from .settings import INSTALLED_APPS, MIDDLEWARE


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

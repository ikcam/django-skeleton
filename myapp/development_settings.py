import os

from .settings import BASE_DIR, INSTALLED_APPS, MIDDLEWARE


DEBUG = True


ALLOWED_HOSTS = [
    '127.0.0.1',
    '0.0.0.0',
    'localhost'
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


# Database
# https://docs.djangoproject.com/en/1.9/ref/settings/#databases
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}


EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'


MESSAGE_STORAGE = 'django.contrib.messages.storage.cookie.CookieStorage'


STATIC_URL = 'http://localhost/myappdir/static/'


MEDIA_URL = 'http://localhost/myappdir/media/'


# Site info

SITE_URL = 'http://localhost:8000'

SITE_NAME = 'My App (Local)'

SITE_SHORT_NAME = 'MA+'


CULQI_PUBLIC_KEY = None

CULQI_PRIVATE_KEY = None

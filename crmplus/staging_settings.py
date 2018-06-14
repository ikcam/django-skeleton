import os

from .settings import BASE_DIR, INSTALLED_APPS, MIDDLEWARE


DEBUG = False


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


# Django Debug Toolbar
# Fix: Conflict between django-countries and django-debug-toolbar
DEBUG_TOOLBAR_CONFIG = {
    # Add in this line to disable the panel
    'DISABLE_PANELS': {
        'debug_toolbar.panels.templates.TemplatesPanel',
        'debug_toolbar.panels.redirects.RedirectsPanel',
    },
}

# Site info

SITE_URL = 'http://stating.crmplus.balegogroup.com'

SITE_NAME = 'My App (Staging)'

SITE_SHORT_NAME = 'MA+'


CULQI_PUBLIC_KEY = None

CULQI_PRIVATE_KEY = None

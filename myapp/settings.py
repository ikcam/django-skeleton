import os
import re

from django.urls import reverse_lazy
from django.utils.translation import ugettext_lazy as _


# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/dev/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'YOUSECRETKEY'


IGNORABLE_404_URLS = [
    re.compile(r'^/apple-touch-icon.*\.png$'),
    re.compile(r'^/favicon\.ico$'),
    re.compile(r'^/robots\.txt$'),
]


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.humanize',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Modules
    'boilerplate',
    'bootstrap3',
    'channels',
    'ckeditor',
    'ckeditor_uploader',
    'corsheaders',
    'dal',
    'dal_select2',
    'dal_queryset_sequence',
    'django_addanother',
    'django_countries',
    'django_filters',
    'rest_framework',
    'rest_framework.authtoken',
    # Apps
    'core',
    'public',
]

MIDDLEWARE = [
    'django.middleware.common.BrokenLinkEmailsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'core.middleware.TimezoneMiddleware',
    'core.middleware.SiteURLMiddleware',
]

ROOT_URLCONF = 'myapp.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(BASE_DIR, 'templates'),
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'myapp.wsgi.application'

ASGI_APPLICATION = 'myapp.routing.application'


AUTHENTICATION_BACKENDS = ('core.backends.AuthenticationBackend',)


# Password validation
# https://docs.djangoproject.com/en/1.11/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': (
            'django.contrib.auth.password_validation.'
            'UserAttributeSimilarityValidator'
        ),
    },
    {
        'NAME': (
            'django.contrib.auth.password_validation.MinimumLengthValidator'
        ),
    },
    {
        'NAME': (
            'django.contrib.auth.password_validation.CommonPasswordValidator'
        ),
    },
    {
        'NAME': (
            'django.contrib.auth.password_validation.NumericPasswordValidator'
        ),
    },
]

AUTH_USER_MODEL = 'core.User'


# Internationalization
# https://docs.djangoproject.com/en/1.11/topics/i18n/

LANGUAGE_CODE = 'en'

TIME_ZONE = 'America/Lima'

USE_I18N = True

USE_L10N = True

USE_TZ = True

LOCALE_PATHS = [
    os.path.join(BASE_DIR, 'locale'),
]

LANGUAGES = [
    ('en', _('English')),
    ('es', _('Spanish')),
    ('fr', _('French')),
]


# Login

LOGIN_URL = reverse_lazy('public:account_login')

LOGIN_REDIRECT_URL = reverse_lazy('public:dashboard')

LOGOUT_REDIRECT_URL = reverse_lazy('public:index')

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.9/howto/static-files/

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'assets/'),
]

MEDIA_ROOT = os.path.join(BASE_DIR, 'media/')

STATIC_ROOT = os.path.join(BASE_DIR, 'static/')

MEDIA_URL = '/media/'

STATIC_URL = '/static/'


SESSION_COOKIE_NAME = 'myappsessionid'

SESSION_ENGINE = "django.contrib.sessions.backends.cached_db"


# CKEditor
# https://github.com/django-ckeditor/django-ckeditor#plugins

CKEDITOR_UPLOAD_PATH = os.path.join(MEDIA_URL, 'uploads/')


# Django REST Framework
# http://www.django-rest-framework.org/api-guide/permissions/

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.SessionAuthentication',
    ),
    'DEFAULT_FILTER_BACKENDS': (
        'django_filters.rest_framework.DjangoFilterBackend',
    ),
    'DEFAULT_PAGINATION_CLASS': (
        'rest_framework.pagination.LimitOffsetPagination'
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    'PAGE_SIZE': 10,
}

# Facebook APP credentials

FB_APP_ID = ''

FB_APP_SECRET = ''


# Google Analytics

GA_ID = ''


# Enviroment variables

APP_ENV = os.getenv('APP_ENV')

if APP_ENV == 'production':
    from .production_settings import *  # NOQA
elif APP_ENV == 'staging':
    from .staging_settings import *  # NOQA
elif APP_ENV == 'tests':
    from .tests_settings import *  # NOQA
else:
    from .development_settings import *  # NOQA
    try:
        from .local_settings import *  # NOQA
    except ImportError:
        pass

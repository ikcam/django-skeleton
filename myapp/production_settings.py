import os
from .settings import BASE_DIR, INSTALLED_APPS

ALLOWED_HOSTS = [
    '127.0.0.1',
    'localhost',
]


ADMINS = [
]


MANAGERS = [
]


INTERNAL_IPS = [
    '127.0.0.1',
]


INSTALLED_APPS += [
    'django_ses',
]


# Database
# https://docs.djangoproject.com/en/1.9/ref/settings/#databases
DATABASES = {
    'default': {
        'ENGINE': os.getenv("APP_DB_TYPE"),
        'NAME': os.getenv("APP_DB_NAME"),
        'USER': os.getenv("APP_DB_USER"),
        'PASSWORD': os.getenv("APP_DB_PASS"),
        'HOST': os.getenv("APP_DB_HOST"),
        'PORT': os.getenv("APP_DB_PORT"),
    }
}


# Email
EMAIL_BACKEND = 'django_ses.SESBackend'

AWS_ACCESS_KEY_ID = os.getenv('APP_AWS_KEY')

AWS_SECRET_ACCESS_KEY = os.getenv('APP_AWS_SECRET')

AWS_SES_REGION_NAME = os.getenv('APP_AWS_REGION')

AWS_SES_REGION_ENDPOINT = 'email.{}.amazonaws.com'.format(
    AWS_SES_REGION_NAME
)

SERVER_EMAIL = os.getenv('APP_SEVER_EMAIL')

DEFAULT_FROM_EMAIL = os.getenv('APP_DEFAULT_EMAIL')


LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '%(levelname)s [%(asctime)s] %(module)s %(message)s'
        },
        'simple': {
            'format': '%(levelname)s %(message)s'
        },
    },
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse',
        }
    },
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'formatter': 'verbose',
            'filename': os.path.join(BASE_DIR, 'django.log'),
            'maxBytes': 1024000,
            'backupCount': 3,
        },
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        }
    },
    'loggers': {
        'django': {
            'handlers': ['file', 'mail_admins'],
            'propagate': True,
            'level': 'DEBUG',
        },
    },
}


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.9/howto/static-files/

STATIC_URL = '/static/'

MEDIA_URL = '/media/'


# Cache

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
        'LOCATION': '127.0.0.1:11211',
    }
}


# Celery
# http://docs.celeryproject.org/en/latest/django/index.html

CELERY_BROKER_URL = 'redis://localhost:6379/1'

CELERY_RESULT_BACKEND = 'redis://localhost:6379'

CELERY_ACCEPT_CONTENT = ['application/json']

CELERY_TASK_SERIALIZER = 'json'

CELERY_RESULT_SERIALIZER = 'json'

CELERY_TIMEZONE = 'America/Los_Angeles'


# Site info

SITE_URL = 'http://myapp.com'

SITE_NAME = 'My App'

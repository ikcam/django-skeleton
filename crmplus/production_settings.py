import os
from .settings import BASE_DIR, INSTALLED_APPS, TIME_ZONE

ALLOWED_HOSTS = [
    'crmplus.balegogroup.com',
    'www.crmplus.balegogroup.com',
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
        'ENGINE': 'django.db.backends.mysql',
        'NAME': os.getenv("APP_DB_NAME"),
        'USER': os.getenv("APP_DB_USER"),
        'PASSWORD': os.getenv("APP_DB_PASS"),
        'HOST': 'localhost',
        'PORT': '3306',
    }
}

CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            'hosts': [
                ('localhost', 6379)
            ],
        },
    },
}


# Email
EMAIL_BACKEND = 'django_ses.SESBackend'

AWS_ACCESS_KEY_ID = os.getenv('APP_AWS_KEY')

AWS_SECRET_ACCESS_KEY = os.getenv('APP_AWS_SECRET')

AWS_SES_REGION_NAME = os.getenv('APP_AWS_REGION')

AWS_SES_REGION_ENDPOINT = 'email.{}.amazonaws.com'.format(
    AWS_SES_REGION_NAME
)

AWS_SES_CONFIGURATION_SET = 'crmplus-set'

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


# Cache

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
        'LOCATION': '127.0.0.1:11211',
    }
}


# Celery
# http://docs.celeryproject.org/en/latest/django/index.html

CELERY_BROKER_URL = 'amqp://crmplus:guest@localhost:5672/crmplus'

CELERY_ACCEPT_CONTENT = ['application/json']

CELERY_TIMEZONE = TIME_ZONE


# Site info

SITE_URL = 'https://{}'.format(ALLOWED_HOSTS[0])

SITE_NAME = 'My App'

SITE_SHORT_NAME = 'MA+'


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.9/howto/static-files/
STATICFILES_STORAGE = (
    'django.contrib.staticfiles.storage.ManifestStaticFilesStorage'
)


CULQI_PUBLIC_KEY = None

CULQI_PRIVATE_KEY = None

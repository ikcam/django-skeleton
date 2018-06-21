DEBUG = False


ALLOWED_HOSTS = ['*']


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}


MESSAGE_STORAGE = 'django.contrib.messages.storage.cookie.CookieStorage'


EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'

# Site info

SITE_URL = 'http://tests.myapp.com'

SITE_NAME = 'My App (Tests)'

SITE_SHORT_NAME = 'MA+'


CULQI_PUBLIC_KEY = None

CULQI_PRIVATE_KEY = None

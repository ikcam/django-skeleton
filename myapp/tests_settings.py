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

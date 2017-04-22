DEBUG = False


DATABASES = {
  'default': {
    'ENGINE': 'django.db.backends.sqlite3',
    'NAME': ':memory:',
  }
}


EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'

# Site info

SITE_URL = 'http://tests.myapp.com'

SITE_NAME = 'My App (Tests)'

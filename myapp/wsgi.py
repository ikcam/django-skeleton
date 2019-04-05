import os

from django.core.wsgi import get_wsgi_application

import dotenv

dotenv.read_dotenv(
    os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "myapp.settings")

application = get_wsgi_application()

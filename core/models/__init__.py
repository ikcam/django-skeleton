from django.conf import settings
import culqipy


culqipy.public_key = settings.CULQI_PUBLIC_KEY
culqipy.secret_key = settings.CULQI_PRIVATE_KEY


MONTHLY_FEE = 50
GRACE_DAYS = 7

CICLE_DAY = 'day'
CICLE_WEEK = 'week'
CICLE_MONTH = 'month'
CICLE_YEAR = 'year'


from .company import Company  # NOQA
from .invite import Invite  # NOQA
from .invoice import Invoice  # NOQA
from .payment import Payment  # NOQA
from .role import Role  # NOQA

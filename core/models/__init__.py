from django.conf import settings

import braintree
import culqipy
import stripe

from core.models.attachment import Attachment
from core.models.colaborator import Colaborator
from core.models.company import Company
from core.models.event import Event
from core.models.invite import Invite
from core.models.invoice import Invoice
from core.models.link import Link
from core.models.message import Message
from core.models.notification import Notification
from core.models.payment import Payment
from core.models.role import Role
from core.models.visit import Visit
from core.models.user import User


braintree = braintree.BraintreeGateway(
    braintree.Configuration(
        braintree.Environment.Sandbox,
        merchant_id=settings.BRAINTREE_MERCHANT_ID,
        public_key=settings.BRAINTREE_PUBLIC_KEY,
        private_key=settings.BRAINTREE_PRIVATE_KEY,
    )
)


culqipy.public_key = settings.CULQI_PUBLIC_KEY
culqipy.secret_key = settings.CULQI_PRIVATE_KEY


stripe.api_key = settings.STRIPE_PRIVATE_KEY


__all__ = [
    'braintree', 'culqipy', 'stripe',
    'Attachment', 'Colaborator', 'Company', 'Event', 'Invite', 'Invoice',
    'Link', 'Message', 'Notification', 'Payment', 'Role', 'Visit', 'User'
]

from datetime import timedelta
from django.contrib.messages.storage import default_storage
from django.contrib.auth.models import AnonymousUser
from django.test import override_settings, RequestFactory, TestCase
from django.utils import timezone

from core.constants import ACCOUNT_ACTIVATION_HOURS
from .models import User
from . import views


@override_settings(DEBUG=True)
class ProfileTestCase(TestCase):
    def setUp(self):
        # 1. gclooney - Active user
        User.objects.create(
            username="gclooney", email="gclooney@test.com",
            first_name="George", last_name="Clooney",
            is_active=True
        )
        # 2. bcooper - Inactive user
        User.objects.create(
            username="bcooper", email="bcooper@test.com",
            first_name="Bradley", last_name="Cooper",
            is_active=False
        )
        self.factory = RequestFactory()

    def test_user_status(self):
        gclooney = User.objects.get(username="gclooney")
        bcooper = User.objects.get(username="bcooper")

        self.assertIsNone(gclooney.activation_key)
        self.assertIsNone(gclooney.date_key_expiration)
        self.assertIsNotNone(bcooper.activation_key)
        self.assertIsNotNone(bcooper.date_key_expiration)

    def test_user_key_generation(self):
        gclooney = User.objects.get(username="gclooney")
        bcooper = User.objects.get(username="bcooper")

        gclooney_key = gclooney.key_generate()
        bcooper_key = bcooper.key_generate()

        self.assertFalse(gclooney_key)
        self.assertFalse(bcooper_key)

        bcooper.date_key_expiration = (
            timezone.now() - timedelta(hours=ACCOUNT_ACTIVATION_HOURS)
        )
        bcooper.save()

        self.assertTrue(bcooper.key_generate())

    def test_user_key_activation(self):
        gclooney = User.objects.get(username="gclooney")
        bcooper = User.objects.get(username="bcooper")
        self.assertFalse(gclooney.key_deactivate())

        request = self.factory.get('/fake-path')
        request.user = AnonymousUser()
        request._messages = default_storage(request)
        response = views.Activate.as_view()(
            request,
            token=bcooper.activation_key
        )
        self.assertEqual(response.status_code, 302)

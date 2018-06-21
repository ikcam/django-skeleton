from django.contrib.messages.constants import SUCCESS
from django.contrib.messages.storage import default_storage
from django.contrib.auth.models import AnonymousUser
from django.core.exceptions import PermissionDenied
from django.test import override_settings, RequestFactory, TestCase

from core.models import User
from core.constants import LEVEL_ERROR, LEVEL_SUCCESS
from core.models import Company
from public import views


@override_settings(DEBUG=True)
class CoreTestCase(TestCase):
    user = None
    company = None

    def setUp(self):
        self.user = User.objects.create(
            username="gclooney", email="gclooney@test.com",
            first_name="George", last_name="Clooney",
            is_active=True
        )
        self.colaborator = User.objects.create(
            username="bcooper", email="bcooper@test.com",
            first_name="Bradley", last_name="Cooper",
            is_active=True
        )
        self.company = Company.objects.create(
            name='Company', email='company@test.com', user=self.user
        )
        # Setup colaborator
        self.colaborator.company = self.company
        self.colaborator.save()
        self.colaborator.colaborator_set.create(
            company=self.company
        )
        # Request factory
        self.factory = RequestFactory()


class CoreViewTestCase(CoreTestCase):
    def test_views_index_no_redirect(self):
        factory = RequestFactory()
        request = factory.get('/fake-path')
        request.user = AnonymousUser()
        response = views.IndexView.as_view()(request)
        self.assertEqual(response.status_code, 200)

    def test_views_dashboard_redirect(self):
        factory = RequestFactory()
        request = factory.get('/fake-path')
        request.user = AnonymousUser()
        response = views.DashboardView.as_view()(request)
        self.assertEqual(response.status_code, 302)

    def test_company_detail_success(self):
        request = self.factory.get('/fake-path')
        request.user = self.user
        response = views.CompanyDetailView.as_view()(request)
        self.assertEqual(response.status_code, 200)

    def test_company_detail_denied(self):
        request = self.factory.get('/fake-path')
        request.user = self.colaborator
        with self.assertRaises(PermissionDenied):
            views.CompanyDetailView.as_view()(request)


class InviteTestCase(CoreTestCase):
    def setUp(self):
        super().setUp()
        self.invite = self.company.invite_set.create(
            name='gclooney', email="gclooney@test.com"
        )

    def test_send_success(self):
        level, response = self.invite.send()
        self.assertEqual(level, LEVEL_SUCCESS)

    def test_send_error(self):
        self.invite.user = self.user
        self.invite.save()
        level, response = self.invite.send()
        self.assertEqual(level, LEVEL_ERROR)


class InviteViewTestCase(CoreTestCase):
    def setUp(self):
        super().setUp()
        self.invite = self.company.invite_set.create(
            name='gclooney', email="gclooney@test.com"
        )

    def test_invite_send(self):
        request = self.factory.get('/fake-path')
        request._messages = default_storage(request)
        request.user = self.user
        response = views.InviteSendView.as_view()(request, pk=self.invite.pk)
        self.assertEqual(response.status_code, 302)
        for message in request._messages:
            self.assertEqual(message.level, SUCCESS)

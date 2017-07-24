from django.contrib.auth.models import AnonymousUser
from django.test import RequestFactory, TestCase
from . import views


class CoreTests(TestCase):
    def test_views_index_no_redirect(self):
        factory = RequestFactory()
        request = factory.get('/fake-path')
        request.user = AnonymousUser()
        response = views.Index.as_view()(request)
        self.assertEqual(response.status_code, 200)

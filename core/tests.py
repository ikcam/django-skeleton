from django.test import RequestFactory, TestCase
from . import views


class CoreTests(TestCase):
    def test_views_index(self):
        factory = RequestFactory()
        request = factory.get('/fake-path')
        response = views.Index.as_view()(request)
        self.assertEqual(response.status_code, 200)

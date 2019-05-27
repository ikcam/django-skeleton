from django.conf import settings
from django.http import HttpResponse
from django.views.generic import DetailView

from core import tasks
from core.models import Link
from core.utils import get_client_ip


class LinkDetailView(DetailView):
    model = Link

    def get(self, request, *args, **kwargs):
        obj = self.get_object()
        ip = get_client_ip(request)
        task = tasks.link_task

        if not settings.DEBUG:
            task = task.delay

        task(
            company_id=obj.company.id,
            task='visit_create',
            pk=obj.pk,
            data={'ip_address': ip}
        )
        response = HttpResponse("", status=301)
        response['Location'] = obj.destination
        return response

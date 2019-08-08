from django.http import HttpResponse
from django.views.generic import DetailView

from core.constants import PIXEL_GIF_DATA
from core.models import Message


class MessagePixelView(DetailView):
    model = Message

    def get(self, *args, **kwargs):
        self.object = self.get_object()
        self.object.set_read()
        return HttpResponse(PIXEL_GIF_DATA, content_type='image/gif')

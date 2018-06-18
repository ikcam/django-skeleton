from django.http import Http404, HttpResponse
from django.views.generic import DetailView, ListView

from core.constants import PIXEL_GIF_DATA
from core.mixins import CompanyQuerySetMixin
from core.models import Message


class MessageDetailView(CompanyQuerySetMixin, DetailView):
    model = Message
    permission_required = 'core:view_message'
    template_name = 'public/message_detail.html'


class MessageFrameView(CompanyQuerySetMixin, DetailView):
    model = Message
    permission_required = 'core:view_message'
    template_name = 'public/message_frame.html'


class MessageListView(CompanyQuerySetMixin, ListView):
    model = Message
    paginate_by = 30
    permission_required = 'core:view_message'
    template_name = 'public/message_list.html'


class MessagePixelView(
    DetailView
):
    model = Message

    def get_object(self):
        try:
            qs = self.get_queryset()
            return qs.get(token=self.kwargs['token'])
        except Message.DoesNotExist:
            raise Http404

    def get(self, *args, **kwargs):
        obj = self.get_object()
        obj.set_read()
        return HttpResponse(PIXEL_GIF_DATA, content_type='image/gif')

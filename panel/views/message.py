from django.views.generic import DetailView, ListView

from core.models import Message
from core.views.mixins import CompanyQuerySetMixin


class MessageDetailView(CompanyQuerySetMixin, DetailView):
    model = Message
    permission_required = 'core:view_message'
    template_name = 'panel/message/message_detail.html'


class MessageFrameView(CompanyQuerySetMixin, DetailView):
    model = Message
    permission_required = 'core:view_message'
    template_name = 'panel/message/message_frame.html'


class MessageListView(CompanyQuerySetMixin, ListView):
    model = Message
    paginate_by = 30
    permission_required = 'core:view_message'
    template_name = 'panel/message/message_list.html'

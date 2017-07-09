import pytz

from django.utils import timezone
from django.utils.deprecation import MiddlewareMixin


class TimezoneMiddleware(MiddlewareMixin):
    def process_request(self, request):
        user = request.user

        if user.is_authenticated:
            tzname = user.profile.timezone

            if tzname:
                timezone.activate(pytz.timezone(tzname))
            else:
                timezone.deactivate()

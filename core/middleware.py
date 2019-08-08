from django.utils.deprecation import MiddlewareMixin

from core.shortcuts import get_current_company


class CurrentCompanyMiddleware(MiddlewareMixin):
    def process_request(self, request):
        request.company = get_current_company(request)

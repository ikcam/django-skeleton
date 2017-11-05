import pytz

from django.conf import settings
from django.core.urlresolvers import resolve, translate_url
from django.shortcuts import redirect
from django.urls import reverse
from django.utils import timezone, translation
from django.utils.deprecation import MiddlewareMixin


class TimezoneMiddleware(MiddlewareMixin):
    def process_request(self, request):
        user = request.user

        if user.is_authenticated:
            tzname = user.profile.timezone
            timezone.activate(pytz.timezone(tzname))

            language = user.profile.language
            url_parts = resolve(request.path)

            if (
                translation.get_language() != language and
                language in settings.LANGUAGES
            ):
                url = reverse(url_parts.view_name, kwargs=url_parts.kwargs)
                url = translate_url(url, language)
                translation.activate(language)
                return redirect(url)


class SiteURLMiddleware(MiddlewareMixin):
    def process_request(self, request):
        user = request.user

        if user.is_authenticated and not settings.DEBUG:
            company = user.profile.company
            domain_current = request.META['HTTP_HOST']

            if company and company.custom_domain:
                domain_company = company.custom_domain.split('//')[1] \
                    .replace('/', '')
                domain = '{}/'.format(company.custom_domain)
            else:
                domain_company = settings.SITE_URL.split('//')[1] \
                    .replace('/', '')
                domain = settings.SITE_URL

            if domain_company != domain_current:
                url = '{0}{1}'.format(domain, request.path)
                return redirect(url)

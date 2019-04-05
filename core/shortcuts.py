def get_current_company(request):
    from core.models import Company
    return Company.objects.get_current(request)

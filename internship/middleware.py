from django.shortcuts import render
from internship.models import SiteSetting

class MaintenanceModeMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        try:
            setting = SiteSetting.objects.first()
            maintenance = setting.maintenance_mode if setting else False
        except:
            maintenance = False
        


        # Block non-staff users if maintenance is ON
        if maintenance and not request.user.is_staff:
            return render(request, "maintenance.html", status=503)

        return self.get_response(request)

from django.shortcuts import redirect
from django.conf import settings
from django.urls import resolve

EXEMPT_URLS = [
    '/accounts/google/login/',
    '/accounts/google/login/callback/',
    '/admin/',  # allow admin
]

class LoginRequiredMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if not request.user.is_authenticated:
            if not any(request.path.startswith(url) for url in EXEMPT_URLS):
                return redirect(settings.LOGIN_URL)
        return self.get_response(request)


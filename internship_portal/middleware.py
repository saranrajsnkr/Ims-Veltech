import datetime
from django.conf import settings
from django.shortcuts import render
from internship.models import SiteSetting
from django.shortcuts import redirect
from django.contrib import messages
from django.contrib.auth import logout




class DomainRestrictMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            email = request.user.email
            if not email.endswith("@veltech.edu.in"):
                # Add a message with an explicit tag
                messages.add_message(
                    request,
                    messages.ERROR,
                    "Only @veltech.edu.in emails are allowed.",
                    extra_tags='domain_error'
                )
                logout(request)
                return redirect("custom_login")
        return self.get_response(request) 
    

class LoginRequiredMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Paths that should not require login
        exempt_paths = [
            "/accounts/",      # for django-allauth
            "/login/",  # your custom login page
            "/static/",        # static files
            "/favicon.ico",    # optional
            "/admin/",
        ]

        if (
            not request.user.is_authenticated
            and not any(request.path.startswith(path) for path in exempt_paths)
        ):
            return redirect("custom_login")

        return self.get_response(request)


class AdminLoginBypassMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path.startswith('/admin/'):
            # Disable social login for admin
            request.session['skip_social_login'] = True
        return self.get_response(request)



class RoleBasedSessionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if not request.user.is_authenticated:
            return self.get_response(request)

        now = datetime.datetime.now().timestamp()

        if request.user.is_staff or request.user.is_superuser:
            # Admin → idle timeout
            idle_timeout = getattr(settings, "ADMIN_IDLE_TIMEOUT", 1800)  # default 15 mins
            last_activity = request.session.get("last_activity", now)

            if now - last_activity > idle_timeout:
                logout(request)
                request.session.flush()
            else:
                request.session["last_activity"] = now

        else:
            # Normal users → absolute timeout (default Django behavior)
            request.session.set_expiry(settings.SESSION_COOKIE_AGE)

        return self.get_response(request)

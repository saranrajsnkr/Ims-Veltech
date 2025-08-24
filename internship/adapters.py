# myapp/adapters.py
from allauth.account.adapter import DefaultAccountAdapter
from allauth.exceptions import ImmediateHttpResponse
from django.shortcuts import render
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter


class CustomAccountAdapter(DefaultAccountAdapter):
    def is_open_for_signup(self, request):
        # Block all signups except via social auth
        return False

    def login_cancel(self, request):
        return ImmediateHttpResponse(
            render(request, "myapp/error.html", {
                "message": "Only Google Login is allowed."
            }, status=403)
        )


# myapp/adapters.py (extend)

class MySocialAccountAdapter(DefaultSocialAccountAdapter):
    def pre_social_login(self, request, sociallogin):
        email = (sociallogin.user.email or '').lower()
        if not (email.endswith('@veltech.edu.in') and email.startswith('vtu')):
            raise ImmediateHttpResponse(
                render(request, "myapp/error.html", {
                    "message": "Only Veltech VTU emails are allowed."
                }, status=403)
            )

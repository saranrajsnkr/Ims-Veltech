from allauth.account.adapter import DefaultAccountAdapter
from django.shortcuts import redirect

class CustomAccountAdapter(DefaultAccountAdapter):
    def get_login_redirect_url(self, request):
        return '/'

    def get_login_url(self, request):
        return '/login/'   # redirect to your site_login.html

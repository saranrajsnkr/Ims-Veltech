from allauth.account.adapter import DefaultAccountAdapter
from django.shortcuts import redirect

# class CustomAccountAdapter(DefaultAccountAdapter):
#     def get_login_redirect_url(self, request):
#         return '/'

#     def get_login_url(self, request):
#         return '/login/'   # redirect to your site_login.html


class CustomAccountAdapter(DefaultAccountAdapter):
    def is_open_for_signup(self, request):
        # Allow signup only for non-admin paths
        if request and request.session.get('skip_social_login', False):
            return False  # Prevent Google signup for admin
        return True

    def get_login_url(self, request):
        # Always use Django's default admin login for /admin/
        if request and request.path.startswith('/admin/'):
            return '/admin/login/'
        return '/login/'
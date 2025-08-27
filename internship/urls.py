from django.urls import path
from . import views
from .views import performance_view


urlpatterns = [
    path('',views.home, name='home'),
    # path('sitelogin/', views.sitelogin, name='sitelogin'),
    # path('logout/', views.logout_view, name='logout'),
    path('Internships/', views.company_list, name='company_list'),
    path('apply/<int:company_id>/', views.apply_to_company, name='apply_to_company'),
    path("server-stats/", performance_view, name="performance"),
    path('check-status/', views.check_application_status, name='check_application_status'),
    path('support-login/', views.login_view, name='support'),
    path('verify/', views.verify_otp_view, name='verify_otp'),
    path('support/', views.submit_report_view, name='submit_report'),
    path('thank-you/', views.thank_you_view, name='thank_you'),
    path('apply/', views.cmpapply_login, name='cmpapply_login'),  # Step 1: Ask for email
    path('apply/verify/', views.cmpapply_verify_otp, name='cmpapply_verify_otp'),  # Step 2: Verify OTP
    path('apply/form/', views.cmpapply_form_view, name='cmpapply_form'),  # Step 3: Show internship form
    path('apply/thank-you/', views.cmpapply_thank_you, name='cmpapply_thank_you'),  # Step 4: Thank you
    path('student-report/login/', views.rep_login_view, name='rep_login'),
    path('student-report/verify/', views.rep_verify_otp_view, name='rep_verify_otp'),
    path('student-report/submit/', views.rep_submit_report_view, name='rep_submit_report'),
    path('student-report/thank-you/', views.rep_thank_you_view, name='rep_thank_you'),
    
]

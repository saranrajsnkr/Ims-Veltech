from django.urls import path
from . import views

urlpatterns = [
    path('', views.company_list, name='company_list'),
    path('apply/<int:company_id>/', views.apply_to_company, name='apply_to_company'),
]

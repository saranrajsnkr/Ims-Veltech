from django.urls import path
from . import views
from .views import performance_view


urlpatterns = [
    path('', views.company_list, name='company_list'),
    path('apply/<int:company_id>/', views.apply_to_company, name='apply_to_company'),
    path("server-stats/", performance_view, name="performance"),

]

from django.contrib import admin
from .models import Company, Student

@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ('name', 'skill_required', 'vacancy')
    search_fields = ('name',)

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('name', 'roll_number', 'email', 'applied_company')
    search_fields = ('name', 'roll_number')

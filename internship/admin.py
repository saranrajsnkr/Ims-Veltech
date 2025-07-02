import csv
from django.contrib import admin
from .models import Company, Student
from django.http import HttpResponse, JsonResponse


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ('name', 'skill_required', 'vacancy')
    search_fields = ('name',)

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('name', 'roll_number', 'email', 'applied_company')
    search_fields = ('name', 'roll_number')
    actions = ["export_as_csv"]
    
    def export_as_csv(self, request, queryset):
        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = 'attachment; filename="device_logs.csv"'
        writer = csv.writer(response)

        writer.writerow(['name', 'roll_number', 'email', 'mobile_number', 'department', 'applied_company'])
        for log in queryset:
            writer.writerow([
                log.name,
                log.roll_number,
                log.email,
                log.mobile_number,
                log.department,
                log.applied_company,
      
            ])
        return response

    export_as_csv.short_description = "Export Selected Logs to CSV"


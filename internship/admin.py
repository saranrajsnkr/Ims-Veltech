import csv
from django.contrib import admin
from .models import Company, Student
from django.http import HttpResponse
from .admin_forms import CsvImportForm  # if you saved it separately
from django.shortcuts import render, redirect
from django.contrib import messages



@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ('name', 'skill_required', 'vacancy')
    actions = None  # disables action choices

    def get_actions(self, request):
        # this removes the entire action box including Go and "x of y selected"
        return {}

    def changelist_view(self, request, extra_context=None):
        # This removes the selection checkboxes next to rows
        request.GET = request.GET.copy()
        if '_selected_action' in request.GET:
            del request.GET['_selected_action']
        return super().changelist_view(request, extra_context=extra_context)


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('name', 'roll_number','department' ,'applied_company')
    search_fields = ('name', 'roll_number')
    actions = ["export_as_csv"]

    def export_as_csv(self, request, queryset):
        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = 'attachment; filename="student_data.csv"'
        writer = csv.writer(response)

        # CSV Header
        writer.writerow(['Name', 'Roll Number',  'Mobile Number', 'Department', 'Applied Company', 'Fee'])

        # CSV Data
        for log in queryset:
            writer.writerow([
                log.name,
                log.roll_number,
                log.mobile_number,
                log.department,
                log.applied_company.name if log.applied_company else '',
                log.fee if log.fee else '',
            ])

        return response
    

    export_as_csv.short_description = "Export Selected Students to CSV"
    
    change_list_template = "admin/internship/student/changelist.html"

    def get_urls(self):
        from django.urls import path
        urls = super().get_urls()
        custom_urls = [
            path('upload-csv/', self.upload_csv),
        ]
        return custom_urls + urls

    def upload_csv(self, request):
        if request.method == "POST":
            csv_file = request.FILES["csv_upload"]
            if not csv_file.name.endswith('.csv'):
                messages.error(request, "This is not a CSV file")
                return redirect("..")

            try:
                decoded_file = csv_file.read().decode('utf-8').splitlines()
                reader = csv.DictReader(decoded_file)

                for row in reader:
                    try:
                        student = Student.objects.create(
                            name=row['Name'].strip(),
                            roll_number=row['Roll Number'].strip().lower(),
                            mobile_number=row.get('Mobile Number', '').strip(),
                            department=row.get('Department', '').strip(),
                            applied_company=Company.objects.get(name__iexact=row['Applied Company'].strip()),
                            fee=row.get('Fee', '').strip()
                        )
                    except Company.DoesNotExist:
                        self.message_user(request, f"Company '{row['Applied Company']}' not found. Row skipped.", level=messages.WARNING)
                    except Exception as e:
                        self.message_user(request, f"Error importing row: {row} → {e}", level=messages.ERROR)



                messages.success(request, "CSV file has been processed successfully.")
                return redirect("..")

            except Exception as e:
                messages.error(request, f"Error processing file: {e}")
                return redirect("..")

        form = CsvImportForm()
        payload = {"form": form}
        return render(request, "admin/csv_upload.html", payload)


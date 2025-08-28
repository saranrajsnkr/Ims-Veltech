import csv
from django.contrib import admin, messages
from .models import Company, Student , Announcement , SiteSetting , UserReport , InternshipApplication , StudentReport , Attendance
from django.http import HttpResponse
from django.shortcuts import render, redirect
from .admin_forms import CsvImportForm  # Make sure you have this form
from django.db.models import F


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ('name', 'skill_required', 'vacancy')
    actions = None  # disables action choices

    def get_actions(self, request):
        # Remove the bulk action box
        return {}

    def changelist_view(self, request, extra_context=None):
        # Remove selection checkboxes
        request.GET = request.GET.copy()
        if '_selected_action' in request.GET:
            del request.GET['_selected_action']
        return super().changelist_view(request, extra_context=extra_context)


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('name', 'roll_number', 'department', 'applied_company', 'house')
    search_fields = ('name', 'roll_number',)
    list_filter = ('applied_company', 'house')
    actions = ["export_as_csv"]
    change_list_template = "admin/internship/student/changelist.html"

    def export_as_csv(self, request, queryset):
        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = 'attachment; filename="student_data.csv"'
        writer = csv.writer(response)

        # CSV Header
        writer.writerow(['Name', 'Roll Number', 'Mobile Number', 'Department', 'Applied Company', 'Fee'])

        # CSV Rows
        for student in queryset:
            writer.writerow([
                student.name,
                student.roll_number,
                student.mobile_number,
                student.department,
                student.applied_company.name if student.applied_company else '',
                student.fee if student.fee else '',
            ])

        return response

    export_as_csv.short_description = "Export Selected Students to CSV"

    def get_urls(self):
        from django.urls import path
        urls = super().get_urls()
        custom_urls = [
            path('upload-csv/', self.upload_csv),
        ]
        return custom_urls + urls

    def upload_csv(self, request):
        if request.method == "POST":
            csv_file = request.FILES.get("csv_upload")
            if not csv_file or not csv_file.name.endswith('.csv'):
                messages.error(request, "Please upload a valid CSV file.")
                return redirect("..")

            try:
                try:
                    decoded_file = csv_file.read().decode('utf-8').splitlines()
                except UnicodeDecodeError:
                    csv_file.seek(0)  # Reset file pointer
                    decoded_file = csv_file.read().decode('latin-1').splitlines()

                reader = csv.DictReader(decoded_file)

                for row in reader:
                    try:
                        # Normalize fields
                        roll = row['Roll Number'].strip().lower()
                        company_name = row['Applied Company'].strip()

                        # Get or create company
                        company, created = Company.objects.get_or_create(
                            name__iexact=company_name,
                            defaults={
                                'name': company_name,
                                'vacancy': 1,  # First entry for new company
                                'fees': row.get('Fee', '').strip() or '0',
                                'location': row.get('Location', 'Not Provided'),
                                'domain': row.get('Domain', 'Unknown'),
                                'active': False,
                                'description': "Auto-created from CSV upload"
                            }
                        )

                        if not created:
                            # If company already exists → increase vacancy before adding
                            company.vacancy = F('vacancy') + 1
                            company.save()
                            company.refresh_from_db()

                        # Duplicate check
                        if Student.objects.filter(roll_number=roll, applied_company=company).exists():
                            self.message_user(request, f"Duplicate: {roll} already applied to {company.name}. Skipping.", level=messages.WARNING)
                            continue

                        # Create student
                        Student.objects.create(
                            name=row['Name'].strip(),
                            roll_number=roll,
                            mobile_number=row.get('Mobile Number', '').strip(),
                            department=row.get('Department', '').strip(),
                            applied_company=company,
                            fee=row.get('Fee', '').strip()
                        )

                    except Exception as e:
                        self.message_user(request, f"Error importing row: {row} → {e}", level=messages.ERROR)

                messages.success(request, "CSV file has been processed successfully.")
                return redirect("..")

            except Exception as e:
                messages.error(request, f"Error processing file: {e}")
                return redirect("..")

        # GET request – show upload form
        form = CsvImportForm()
        payload = {"form": form}
        return render(request, "admin/csv_upload.html", payload)


@admin.register(SiteSetting)
class SiteSettingAdmin(admin.ModelAdmin):
    list_display = ['maintenance_mode']

    def has_add_permission(self, request):
        # Only allow adding if no announcement exists
        return not Announcement.objects.exists()

@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):
    list_display = ['message1','is_message1_active','message2','is_message2_active']
    


    def has_add_permission(self, request):
        # Only allow adding if no announcement exists
        return not Announcement.objects.exists()

from django.contrib import admin
from .models import UserReport

@admin.register(UserReport)
class UserReportAdmin(admin.ModelAdmin):
    list_display = ('name', 'roll_number', 'email', 'submitted_at')
    search_fields = ('name', 'roll_number', 'email')
    list_filter = ('submitted_at',)

    # 🚫 Disable Add
    def has_add_permission(self, request):
        return False

    # 🚫 Disable Edit
    def has_change_permission(self, request, obj=None):
        return False

    # # 🚫 Disable Delete
    # def has_delete_permission(self, request, obj=None):
    #     return False
  

from django.contrib import admin
from .models import InternshipApplication

@admin.register(InternshipApplication)
class InternshipApplicationAdmin(admin.ModelAdmin):
    list_display = ("student_name", "vtu_number", "industry_name", "application_approved", "submitted_at")
    list_filter=("application_approved",)
    search_fields = ("student_name", "vtu_number", "industry_name")

    def get_readonly_fields(self, request, obj=None):
        if obj:  # editing an existing object
            all_fields = [field.name for field in obj._meta.fields]
            return [f for f in all_fields if f not in ("application_approved", "approval_message")]
        return []  # allow editing all fields while creating a new object


    fieldsets = (
        ('Student Details', {
            'fields': ('student_name', 'vtu_number', 'department', 'email', 'contact_number')
        }),
        ('Industry Details', {
            'fields': (
                'industry_name', 'industry_location', 'domain_of_work',
                'industry_category', 'industry_website', 'industry_email', 'industry_phone_number' , 'referal_person_name', 'referal_person_designation' , 'referal_person_email', 'referal_person_phone_number'
            )
        }),
        ('Stipend & Fees', {
            'fields': ('stipend_provided', 'stipend_amount', 'fees_required', 'fees_amount')
        }),
        ('Meta', {
            'fields': ('submitted_at',),
        }),
        
        ('Approval Status', {
            'fields': ('application_approved', 'approval_message'),
        }),
    )






@admin.register(StudentReport)
class StudentReportAdmin(admin.ModelAdmin):
    list_display = ('roll_number', 'report_status')
    list_filter = ('report_status',)
    search_fields = ('roll_number',)



@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ("student", "company", "date", "status")
    search_fields = ("student__name", "company__name")
    list_filter = ("date", "status", "company")
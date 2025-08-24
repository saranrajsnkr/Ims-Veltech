# signals.py
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import InternshipApplication, Company, Student
from django.utils.text import slugify
from internship.models import Student
import gspread
from google.oauth2.service_account import Credentials
from django.conf import settings
# from internship.utils.google_sheets import sync_db_to_sheets
import time
from gspread.exceptions import GSpreadException




# Setup Google credentials
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
creds = Credentials.from_service_account_info(settings.GOOGLE_CONFIG, scopes=SCOPES)
client = gspread.authorize(creds)
sheet = client.open_by_key(settings.GOOGLE_SHEET_ID).sheet1

@receiver(post_save, sender=InternshipApplication)
def handle_approved_application(sender, instance, created, **kwargs):
    if instance.application_approved != "APPROVED":
        return

    # Normalize company name for uniqueness handling
    base_name = instance.industry_name.strip()
    normalized_name = base_name
    counter = 1

    while Company.objects.filter(name=normalized_name).exists():
        normalized_name = f"{base_name} ({counter})"
        counter += 1

    # Try to find an exact match on location + domain, not just name
    company = Company.objects.filter(
        name__iexact=base_name,
    ).first()

    if company:
        # Company exists — increase vacancy
        company.vacancy += 1
        company.save()
    else:
        # Company doesn't exist — create a new one with unique name
        company = Company.objects.create(
            name=normalized_name,
            fees=instance.fees_amount or '0',
            location=instance.industry_location,
            domain=instance.domain_of_work,
            vacancy=1,
            active=False,
            description="Auto-created from external application",
        )

    # Check if student exists by roll number
    student, created = Student.objects.get_or_create(
        roll_number=instance.vtu_number.lower(),
        defaults={
            'name': instance.student_name,
            'mobile_number': instance.contact_number,
            'department': instance.department,
            'applied_company': company,
            'fee': instance.fees_amount or '0',
        }
    )

    # Optional: if student exists but applied_company is blank, update it
    if not created and not student.applied_company:
        student.applied_company = company
        student.save()



# @receiver([post_save, post_delete], sender=Student)
# def update_google_sheet(sender, instance, **kwargs):
#     """Whenever a Student is added/updated/deleted, update Google Sheets"""
#     sync_db_to_sheets()


# 🔹 Save or Update Student in Sheet
@receiver(post_save, sender=Student)
def track_save(sender, instance, created, **kwargs):
    row_data = [
        instance.id,
        instance.name,
        instance.roll_number,
        instance.mobile_number or "",
        instance.department or "",
        instance.applied_company.name if instance.applied_company else "",
        instance.applied_company.id if instance.applied_company else "",
        instance.fee or "",
        "TRUE",
    ]

    try:
        cells = sheet.findall(str(instance.id))
        if cells:
            cell = cells[0]
            # Prepare bulk cell updates if needed
            cell_list = []
            for col, value in enumerate(row_data, start=1):
                cell_obj = sheet.cell(cell.row, col)
                cell_obj.value = value
                cell_list.append(cell_obj)
            # Batch update with proper parsing
            sheet.update_cells(cell_list, value_input_option='USER_ENTERED')
            print(f"♻️ Updated student {instance.name} in sheet.")
            time.sleep(2)
        else:
            raise ValueError("Not found")
    except (GSpreadException, ValueError):
        # Append row with interpretation
        sheet.append_row(row_data, value_input_option='USER_ENTERED')
        print(f"➕ Added or appended new student {instance.name} to sheet.")
        time.sleep(2)
    except Exception as e:
        print(f"⚠️ Error updating sheet: {e}")


# 🔹 Delete Student from Sheet
@receiver(post_delete, sender=Student)
def track_delete(sender, instance, **kwargs):
    try:
        cell = sheet.find(str(instance.id))
        if cell:
            sheet.delete_rows(cell.row)
            print(f"🗑️ Deleted student {instance.name} (ID={instance.id}) from sheet.")
            time.sleep(2)
    except Exception as e:
        print(f"⚠️ Error deleting from sheet: {e}")

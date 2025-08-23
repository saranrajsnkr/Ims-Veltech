# import gspread
# from google.oauth2.service_account import Credentials
# from django.conf import settings
# from internship.models import Student, Company
# import time


# # Setup Google credentials
# SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
# creds = Credentials.from_service_account_info(settings.GOOGLE_CONFIG, scopes=SCOPES)
# client = gspread.authorize(creds)
# sheet = client.open_by_key(settings.GOOGLE_SHEET_ID).sheet1


# def sync_db_to_sheets():
#     """Push all Student rows → Google Sheets"""
#     students = Student.objects.all()

#     # Clear existing sheet data
#     sheet.clear()

#     # Add header row
#     sheet.append_row(["ID", "Name", "Roll Number", "Mobile Number", "Department", "Company", "Fee"])

#     for s in students:
#         sheet.append_row([
#             s.id,
#             s.name,
#             s.roll_number,
#             s.mobile_number or "",
#             s.department or "",
#             s.applied_company.name if s.applied_company else "",
#             s.fee or ""
#         ])
#         time.sleep(2)


# def sync_sheets_to_db():
#     """Full sync: Google Sheets → Student DB (add, update, delete, auto company create)"""
#     rows = sheet.get_all_records()
#     sheet_ids = set()

#     for row in rows:
#         student_id = row.get("ID")
#         company_name = row.get("Company")

#         company = None
#         if company_name:
#             # ✅ Try to fetch company
#             company = Company.objects.filter(name__iexact=company_name.strip()).first()
#             if not company:
#                 # ✅ Auto-create company if not found
#                 company = Company.objects.create(
#                     name=company_name.strip(),
#                     fees=row.get("Fee") or "0",   # If fee available, use it
#                     location="(Auto-created from Sheet)",  
#                     domain="(Unknown)",  
#                     vacancy=1,
#                     active=False,
#                     description="Auto-created from Google Sheet sync",
#                 )

#         if student_id:  
#             # ✅ Existing student → update
#             sheet_ids.add(int(student_id))
#             Student.objects.update_or_create(
#                 id=student_id,
#                 defaults={
#                     "name": row.get("Name"),
#                     "roll_number": row.get("Roll Number").lower() if row.get("Roll Number") else None,
#                     "mobile_number": row.get("Mobile Number") or None,
#                     "department": row.get("Department") or None,
#                     "fee": row.get("Fee") or None,
#                     "applied_company": company,
#                 }
#             )
#         else:
#             # ✅ New student → create
#             student = Student.objects.create(
#                 name=row.get("Name"),
#                 roll_number=row.get("Roll Number").lower() if row.get("Roll Number") else None,
#                 mobile_number=row.get("Mobile Number") or None,
#                 department=row.get("Department") or None,
#                 fee=row.get("Fee") or None,
#                 applied_company=company,
#             )
#             sheet_ids.add(student.id)

#     # ✅ Handle deletions
#     db_ids = set(Student.objects.values_list("id", flat=True))
#     ids_to_delete = db_ids - sheet_ids
#     if ids_to_delete:
#         Student.objects.filter(id__in=ids_to_delete).delete()

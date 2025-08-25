from django.shortcuts import render, redirect, get_object_or_404
from .models import Company, Student , Announcement , UserReport , InternshipApplication , StudentReport
from django.contrib import messages
from django.db import transaction, IntegrityError
from django.db.models import F
from django.http import JsonResponse
import psutil
import os
from .forms import UserReportForm , InternshipApplicationForm , StudentReportForm
from django.core.mail import send_mail
import random
from django.conf import settings
import gspread
from google.oauth2.service_account import Credentials



# Setup Google credentials
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
creds = Credentials.from_service_account_info(settings.GOOGLE_CONFIG, scopes=SCOPES)
client = gspread.authorize(creds)
sheet = client.open_by_key(settings.GOOGLE_SHEET_ID).sheet1


def home(request):
    return render(request, 'internship/home.html')

def company_list(request):
    companies_with_vacancy = Company.objects.filter(vacancy__gt=0,active=True)
    announcement = Announcement.objects.first()
    context = {
        'companies': companies_with_vacancy,
        'has_vacancy': companies_with_vacancy.exists(),
        'announcement': announcement,
    }
    return render(request, 'internship/company_list.html', context)


@transaction.atomic
def apply_to_company(request, company_id):
    company = get_object_or_404(Company.objects.select_for_update(), id=company_id)

    if request.method == 'POST':
        name = request.POST.get('name')
        roll = str(request.POST.get('roll_number', '')).strip().lower()  # Normalize roll number
        mobile = request.POST.get('mobile_number')
        department = request.POST.get('department')

        # Prevent application if no vacancies
        if company.vacancy <= 0:
            messages.error(request, "Vacancy was filled. Please apply for another company.",extra_tags='user')
            return redirect('company_list')

        # Prevent duplicate application
        if Student.objects.filter(roll_number=roll, applied_company=company).exists():
            messages.error(request, "You have already applied to this company.",extra_tags='user')
            return redirect('company_list')
        
        student_qs = Student.objects.filter(roll_number=roll)

        if student_qs.exists():
            student = student_qs.first()

            # Check if student already applied AND the company is NOT the "BLOCKED" company
            if student.applied_company.name == "Blocked":
                messages.error(request, "You have been blacklisted, so you cannot apply to any company.", extra_tags='user')
                return redirect('company_list')
        
        if Student.objects.filter(roll_number=roll).exists():
            messages.error(request, "You have already enrolled in a company, so you cannot apply again to another company.",extra_tags='user')
            return redirect('company_list')
        
        # if InternshipApplication.objects.filter(vtu_number=roll).exists():
        #     messages.error(request, "You have already applied with this VTU number.",extra_tags='user')
        #     return redirect('company_list')
        
        Intern_qs= InternshipApplication.objects.filter(vtu_number=roll)
        if Intern_qs.exists():
            intern = Intern_qs.first()
            if intern.application_approved == "APPROVED" or intern.application_approved == "PENDING":
                messages.error(request, "Your external company form is either pending or approved. You can only enroll in other companies if it gets rejected.",extra_tags='user')
                return redirect('company_list')

        try:
            # Create the student application and assign it to variable
            student = Student.objects.create(
                name=name,
                roll_number=roll,
                mobile_number=mobile,
                department=department,
                applied_company=company
            )

            # Reduce the company's vacancy
            company.vacancy = F('vacancy') - 1
            company.save()
            company.refresh_from_db()
            
            # # Append to Google Sheet
            # sheet.append_row([
            #     student.id,
            #     student.name,
            #     student.roll_number,
            #     student.mobile_number or "",
            #     student.department or "",
            #     student.applied_company.name if student.applied_company else "",
            #     student.fee or ""
            # ])

            messages.success(request, "Applied successfully!", extra_tags='user')
            return redirect('company_list')

        except IntegrityError:
            messages.error(request, "You have already applied or something went wrong. Please check your VTU on the application status page.", extra_tags='user')
            return redirect('company_list')


    return render(request, 'internship/apply_form.html', {'company': company})


def check_application_status(request):
    internship_result = None
    student_result = None
    roll_number = ''

    if request.method == 'POST':
        roll_number = str(request.POST.get('roll_number', '')).strip().lower()

        # Check InternshipApplication model
        internship_result = InternshipApplication.objects.filter(vtu_number=roll_number)

        # Check Student model
        student_result = Student.objects.filter(roll_number=roll_number).select_related('applied_company').first()

    return render(request, 'internship/check_status.html', {
        'internship_result': internship_result,
        'student_result': student_result,
        'roll_number': roll_number
    })


def performance_view(request):
    pid = os.getpid()
    process = psutil.Process(pid)

    cpu = process.cpu_percent(interval=0.5)
    memory = process.memory_info().rss / 1024 ** 2  # in MB

    return JsonResponse({
        "cpu_usage_percent": f"{cpu:.2f}",
        "memory_usage_mb": f"{memory:.2f}"
    })



# === Helper ===
def generate_otp():
    return str(random.randint(100000, 999999))

# === Step 1: Ask for Email ===
def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        request.session['email'] = email

        # === Bypass OTP if email matches ===
        if email == 'vtu24875@veltech.edu.in':
            request.session['is_logged_in'] = True
            return redirect('submit_report')

        # === Normal OTP flow ===
        otp = generate_otp()
        request.session['otp'] = otp

        send_mail(
            subject='Your OTP Code',
            message=f'Your OTP is {otp}',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
        )
        return redirect('verify_otp')

    return render(request, 'reports/login.html')

# === Step 2: OTP Verification ===
def verify_otp_view(request):
    if request.method == 'POST':
        entered_otp = request.POST.get('otp')
        if entered_otp == request.session.get('otp'):
            request.session['is_logged_in'] = True
            return redirect('submit_report')
        else:
            messages.error(request, 'Invalid OTP')
    return render(request, 'reports/verify_otp.html')

# === Step 3: Report Submission ===
def submit_report_view(request):
    if not request.session.get('is_logged_in'):
        return redirect('login')

    email = request.session.get('email', '')
    initial_data = {
        'email': email,
        'roll_number': email[3:8]  # Extracts "24875"
    }

    if request.method == 'POST':
        form = UserReportForm(request.POST, request.FILES)
        if form.is_valid():
            report = form.save()
            # Email to admin
            try:
                send_mail(
                    subject=f"New Report from {report.name}",
                    message=(
                        f"Name: {report.name}\n"
                        f"Roll No: {report.roll_number}\n"
                        f"Email: {report.email}\n"
                        f"Problem:\n{report.problem}"
                    ),
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[settings.ADMIN_EMAIL]
                )
                print("Email sent successfully.")
            except Exception as e:
                print("Error sending email:", e)

            return redirect('thank_you')
    else:
        form = UserReportForm(initial=initial_data)

    return render(request, 'reports/report_form.html', {'form': form})

# === Step 4: Thank You Page ===
def thank_you_view(request):
    request.session.flush()  # clear login session after submit
    return render(request, 'reports/thank_you.html')



# === Helper ===
def cmpapply_otp():
    return str(random.randint(100000, 999999))

# === Step 1: Ask for Email ===
def cmpapply_login(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        request.session['cmp_email'] = email

        # Bypass logic
        if email == 'vtu24875@veltech.edu.in':
            request.session['cmp_logged_in'] = True
            return redirect('cmpapply_form')

        # Normal OTP flow
        otp = cmpapply_otp()
        request.session['cmp_otp'] = otp

        send_mail(
            subject='Your Internship OTP Code',
            message=f'Your One Time Password (OTP) for internship application is: {otp}',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
        )
        return redirect('cmpapply_verify_otp')

    return render(request, 'internship/email_login.html')


# === Step 2: OTP Verification ===
def cmpapply_verify_otp(request):
    if request.method == 'POST':
        entered_otp = request.POST.get('otp')
        if entered_otp == request.session.get('cmp_otp'):
            request.session['cmp_logged_in'] = True
            return redirect('cmpapply_form')
        else:
            messages.error(request, 'Invalid OTP. Please try again.')
    return render(request, 'internship/verify_otp.html')

# === Step 3: Internship Form Submission ===
def cmpapply_form_view(request):
    if not request.session.get('cmp_logged_in'):
        return redirect('cmpapply_login')

    email = request.session.get('cmp_email', '')
    initial_data = {
        'email': email,
        'vtu_number': email[3:8] if len(email) >= 8 else ''
    }
    
    vtu_number = initial_data['vtu_number']
    student_qs = Student.objects.filter(roll_number=vtu_number)

    if student_qs.exists():
        student = student_qs.first()

        # Check if student already applied AND the company is NOT the "BLOCKED" company
        if student.applied_company.name != "Blocked":
            messages.error(request, "You have already enrolled in a company, so you cannot access the external application form.", extra_tags='user')
            return redirect('company_list')



    
    # if InternshipApplication.objects.filter(vtu_number=vtu_number).exists():
    #     messages.error(request, "You have already applied with this VTU number.",extra_tags='user')
    #     return redirect('company_list')
    
    Intern_qs= InternshipApplication.objects.filter(vtu_number=vtu_number)
    if Intern_qs.exists():
        intern = Intern_qs.first()
        if intern.application_approved == "APPROVED" or intern.application_approved == "PENDING":
            messages.error(request,"You’ve already submitted an external application, and it’s either approved or still pending. You can only apply again if it gets rejected.",extra_tags='user')
            return redirect('company_list')
        
        

    if request.method == 'POST':
        form = InternshipApplicationForm(request.POST)
        if form.is_valid():
            application = form.save()

            # Optional Email to Admin
            # try:
            #     send_mail(
            #         subject=f"New Internship Application - {application.student_name}",
            #         message=(
            #             f"Student: {application.student_name} ({application.vtu_number})\n"
            #             f"Email: {application.email}\n"
            #             f"Industry: {application.industry_name}\n"
            #             f"Location: {application.industry_location}\n"
            #             f"Domain: {application.domain_of_work}"
            #         ),
            #         from_email=settings.DEFAULT_FROM_EMAIL,
            #         recipient_list=[settings.ADMIN_EMAIL]
            #     )
            # except Exception as e:
            #     print("Error sending email:", e)

            return redirect('cmpapply_thank_you')
    else:
        form = InternshipApplicationForm(initial=initial_data)

    return render(request, 'internship/internship_form.html', {'form': form})

# === Step 4: Thank You Page ===
def cmpapply_thank_you(request):
    request.session.flush()
    return render(request, 'internship/thank_you.html')







# === Helper ===
def generate_otp():
    return str(random.randint(100000, 999999))

# === Step 1: Student Login with Roll Number ===
def rep_login_view(request):
    if request.method == 'POST':
        roll_number = request.POST.get('roll_number')
        
        # Check if report already submitted
        if StudentReport.objects.filter(roll_number=roll_number).exists():
            messages.error(request, "You have already submitted a report.", extra_tags='user')
            return redirect('company_list')

        try:
            student = Student.objects.get(roll_number=roll_number)
            request.session['student_roll'] = roll_number
            request.session['student_email'] = f"vtu{roll_number}@veltech.edu.in"

            otp = generate_otp()
            request.session['student_otp'] = otp

            send_mail(
                subject='Student OTP Verification',
                message=f'Your OTP is {otp}',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[request.session['student_email']],
            )
            return redirect('rep_verify_otp')
        except Student.DoesNotExist:
            messages.error(request, 'Invalid roll number. Student not found in any company.')

    return render(request, 'report/student_login.html')



# === Step 2: Verify Student OTP ===
def rep_verify_otp_view(request):
    if request.method == 'POST':
        entered_otp = request.POST.get('otp')
        if entered_otp == request.session.get('student_otp'):
            request.session['is_student_logged_in'] = True
            return redirect('rep_submit_report')
        else:
            messages.error(request, 'Invalid OTP. Please try again.')

    return render(request, 'report/student_verify_otp.html')


# === Step 3: Submit Report Status ===

def rep_submit_report_view(request):
    roll_number = request.session.get('student_roll', '')
    email = request.session.get('student_email', '')
    
    if not roll_number:
        messages.error(request, "Session expired or not logged in.")
        return redirect('rep_login')

    initial_data = {
        'roll_number': roll_number,
        'email': email,
        'vtu_number': email[3:8] if len(email) >= 8 else ''
    }

    if request.method == 'POST':
        form = StudentReportForm(request.POST)
        if form.is_valid():
            if StudentReport.objects.filter(roll_number=roll_number).exists():
                messages.error(request, "You have already submitted the report.")
            else:
                report = form.save(commit=False)
                report.roll_number = roll_number  # Ensure it's saved with session value
                report.save()
                return redirect('rep_thank_you')
    else:
        form = StudentReportForm(initial=initial_data)

    return render(request, 'report/student_report_form.html', {'form': form})


# === Step 4: Thank You ===
def rep_thank_you_view(request):
    request.session.flush()
    return render(request, 'report/student_thank_you.html')

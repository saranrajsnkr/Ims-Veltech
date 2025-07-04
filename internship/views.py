from django.shortcuts import render, redirect, get_object_or_404
from .models import Company, Student
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.db.models import F
from django.db import transaction, IntegrityError
import psutil
from django.http import JsonResponse
import os


def company_list(request):
    companies = Company.objects.all()
    companies_with_vacancy = [c for c in companies if c.vacancy > 0]
    context = {
        'companies': companies_with_vacancy,
        'has_vacancy': bool(companies_with_vacancy),
    }
    return render(request, 'internship/company_list.html', context)

@transaction.atomic
def apply_to_company(request, company_id):
    company = Company.objects.select_for_update().get(id=company_id)

    if request.method == 'POST':
        name = request.POST.get('name')
        roll = request.POST.get('roll_number', '').strip().lower()  # Normalize
        mobile = request.POST.get('mobile_number')
        department = request.POST.get('department')

        # ✅ Check if vacancies are left
        # ✅ Updated friendly message here
        if company.vacancy <= 0:
            messages.error(request, "Vacancy was filled. Please apply for another company.")
            return redirect('company_list')

        # ✅ Prevent duplicate roll number for this company
        if Student.objects.filter(roll_number=roll, applied_company=company).exists():
            messages.error(request, "You have already applied with this roll number.")
            return redirect('company_list')

        try:
            # ✅ Create the student record
            Student.objects.create(
                name=name,
                roll_number=roll,
                mobile_number=mobile,
                department=department,
                applied_company=company
            )

            # ✅ Reduce vacancy atomically
            company.vacancy = F('vacancy') - 1
            company.save()
            company.refresh_from_db()  # Apply the updated value

            messages.success(request, "Applied successfully!")
            return redirect('company_list')

        except IntegrityError:
            messages.error(request, "You have already applied or something went wrong.<br>Please check your VTU on the application status page.")
            return redirect('company_list')

    return render(request, 'internship/apply_form.html', {'company': company})



def performance_view(request):
    pid = os.getpid()
    p = psutil.Process(pid)

    cpu = p.cpu_percent(interval=0.5)
    memory = p.memory_info().rss / 1024 ** 2  # in MB

    return JsonResponse({
        "cpu_usage_percent": f"{cpu:.2f}",
        "memory_usage_mb": f"{memory:.2f}"
    })
    


def check_application_status(request):
    result = None
    roll_number = ''

    if request.method == 'POST':
        roll_number = request.POST.get('roll_number', '').strip().lower()
        result = Student.objects.filter(roll_number=roll_number).select_related('applied_company')

    return render(request, 'internship/check_status.html', {
        'result': result,
        'roll_number': roll_number
    })

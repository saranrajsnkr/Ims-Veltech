from django.shortcuts import render, redirect, get_object_or_404
from .models import Company, Student
from django.contrib import messages
from django.db import transaction, IntegrityError
from django.db.models import F
from django.http import JsonResponse
import psutil
import os


def company_list(request):
    companies_with_vacancy = Company.objects.filter(vacancy__gt=0)
    context = {
        'companies': companies_with_vacancy,
        'has_vacancy': companies_with_vacancy.exists(),
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
            messages.error(request, "Vacancy was filled. Please apply for another company.")
            return redirect('company_list')

        # Prevent duplicate application
        if Student.objects.filter(roll_number=roll, applied_company=company).exists():
            messages.error(request, "You have already applied to this company.")
            return redirect('company_list')
        
        if Student.objects.filter(roll_number=roll).exists():
            messages.error(request, "You have already applied with this VTU number.")
            return redirect('company_list')

        try:
            # Create the student application
            Student.objects.create(
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

            messages.success(request, "Applied successfully!")
            return redirect('company_list')

        except IntegrityError:
            messages.error(request, "You have already applied or something went wrong. Please check your VTU on the application status page.")
            return redirect('company_list')

    return render(request, 'internship/apply_form.html', {'company': company})


def check_application_status(request):
    result = None
    roll_number = ''

    if request.method == 'POST':
        roll_number = str(request.POST.get('roll_number', '')).strip().lower()
        result = Student.objects.filter(roll_number=roll_number).select_related('applied_company')

    return render(request, 'internship/check_status.html', {
        'result': result,
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

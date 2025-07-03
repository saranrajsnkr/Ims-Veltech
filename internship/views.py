from django.shortcuts import render, redirect, get_object_or_404
from .models import Company, Student
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.db.models import F
from django.db import transaction, IntegrityError



def company_list(request):
    companies = Company.objects.all()
    return render(request, 'internship/company_list.html', {'companies': companies})

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
            messages.error(request, "🚫 Vacancy was filled. Please apply for another company.")
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
            messages.error(request, "An error occurred during application.")
            return redirect('company_list')

    return render(request, 'internship/apply_form.html', {'company': company})